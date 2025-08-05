import os
import re
import json
import math
import aiohttp
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from getTrendInput import get_top_region_keywords
from generateImage import generateImage

# --- Config ---
ARTICLES_DATA_FILE = "perplexityArticles.json"
DEFAULT_AUTHOR = "JAMSA - Country's News"
DEFAULT_LANGUAGE = "en-IN"
DEFAULT_SCHEMA_TYPE = "NewsArticle"
DEFAULT_AD_DENSITY = "medium"
DEFAULT_FACT_CHECKED_BY = "AI Content Review"
DEFAULT_EDITOR_REVIEWED_BY = "AI Editor"
DEFAULT_SPONSOR_NAME = None
DEFAULT_IS_SPONSORED_CONTENT = False
DEFAULT_VIEWS_COUNT = 0
DEFAULT_SHARES_COUNT = 0
DEFAULT_COMMENTS_COUNT = 0
DEFAULT_AVERAGE_RATING = 0.0
OUTPUT_DIR = "dist"
IMAGES_BASE_DIR = os.path.join(OUTPUT_DIR, "images")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# -- Helpers ----------

def generate_slug(title):
    slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug

def estimate_reading_time(content):
    clean_content = re.sub(r"<[^>]+>", "", content)
    words = len(clean_content.split())
    reading_time = math.ceil(words / 200)
    return reading_time, words

def generate_placeholder_image_url(text, width=1200, height=630, bg_color="1f2937", text_color="ffffff"):
    from urllib.parse import quote
    encoded = quote(text)
    return f"https://placehold.co/{width}x{height}/{bg_color}/{text_color}?text={encoded}"

def embed_inline_images(html_content, inline_images):
    # Place images in content by hints or after Nth paragraph/head
    content = html_content
    for img in inline_images:
        # Simple insertion after Nth paragraph for now
        paragraphs = list(re.finditer(r'(<p[^>]*>.*?</p>)', content, re.IGNORECASE | re.DOTALL))
        n = int(re.search(r"paragraph\s*(\d+)", img.get("placementHint", "") or "")[1]) if re.search(r"paragraph\s*(\d+)", img.get("placementHint", "") or "") else 2
        insert_at = paragraphs[n-1].end() if len(paragraphs) >= n else len(content)
        img_tag = f'<img src="{img["url"]}" alt="{img["alt"]}" style="max-width:100%;" />'
        content = content[:insert_at] + img_tag + content[insert_at:]
    return content

def add_internal_links(content_html, all_titles_map, current_slug, max_links=3):
    # Advanced: Use entities/phrases for links. Simple: use other article titles.
    linked_content = content_html
    links_added = 0
    sorted_titles = sorted([t for t in all_titles_map if all_titles_map[t]!=current_slug], key=len, reverse=True)
    for title in sorted_titles:
        if links_added >= max_links: break
        pattern = r"\\b" + re.escape(title) + r"\\b"
        if re.search(pattern, linked_content, re.IGNORECASE):
            slug = all_titles_map[title]
            link_tag = f'<a href="/articles/{slug}.html">{title}</a>'
            linked_content, count = re.subn(pattern, link_tag, linked_content, count=1, flags=re.IGNORECASE)
            if count > 0:
                links_added += 1
    return linked_content

async def generate_article_from_keyword(session, keyword, region, searches, article_id_counter, all_titles_map):
    prompt = f"""Generate a comprehensive news article on "{keyword}" for region "{region}" ({searches} searches). Article should be 1000+ words and SEO-rich, with images, meta, key takeaways, hashtags, CTA, and valid NewsArticle JSON-LD structuredData."""
    headers = {'Content-Type': 'application/json'}
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING"},
            "excerpt": {"type": "STRING"},
            "content": {"type": "STRING"},
            "metaDescription": {"type": "STRING"},
            "keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
            "ogTitle": {"type": "STRING"},
            "imageAltText": {"type": "STRING"},
            "socialShareText": {"type": "STRING"},
            "adPlacementKeywords": {"type": "ARRAY", "items": {"type": "STRING"}},
            "category": {"type": "STRING"},
            "subCategory": {"type": "STRING"},
            "contentType": {"type": "STRING"},
            "difficultyLevel": {"type": "STRING"},
            "targetAudience": {"type": "ARRAY", "items": {"type": "STRING"}},
            "inlineImageDescriptions": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "description": {"type": "STRING"},
                        "caption": {"type": "STRING"},
                        "placementHint": {"type": "STRING"}
                    },
                    "required": ["description", "caption"]
                }
            },
            "keyTakeaways": {"type": "ARRAY", "items": {"type": "STRING"}}, # New field
            "socialMediaHashtags": {"type": "ARRAY", "items": {"type": "STRING"}}, # New field
            "callToActionText": {"type": "STRING"}, # New field
            "structuredData": {"type": "STRING"} # New field
        },
        "required": [
            "title", "excerpt", "content", "metaDescription", "keywords",
            "ogTitle", "imageAltText", "socialShareText", "adPlacementKeywords",
            "category", "contentType", "difficultyLevel", "targetAudience",
            "inlineImageDescriptions", # Now required
            "keyTakeaways", # Now required
            "socialMediaHashtags", # Now required
            "callToActionText", # Now required
            "structuredData" # Now required
        ]
    }
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }
    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    async with session.post(url, headers=headers, data=json.dumps(payload)) as resp:
        if resp.status != 200:
            print(f"API error {resp.status}: {await resp.text()}")
            return None
        result = await resp.json()
        if not (result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts")):
            print(f"Error: Bad API structure"); return None
        gen_str = result["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(gen_str)
        now = datetime.now().strftime("%Y-%m-%d")
        slug = generate_slug(data['title'])
        reading_time, word_count = estimate_reading_time(data['content'])

        # --- Image Creation (sequential for now, can batch further) ---
        os.makedirs(os.path.join(IMAGES_BASE_DIR, slug), exist_ok=True)
        og_image_prompt = f"Photo for article: {data['ogTitle']}. Visual: {data['imageAltText']}."
        og_img_fp = os.path.join(IMAGES_BASE_DIR, slug, "main.jpg")
        og_image_url = generateImage(og_image_prompt, og_img_fp) or generate_placeholder_image_url(data['ogTitle'])
        # Repeat for thumbnail and inline images; code elided for brevity.

        inline_images_list = []
        inline_image_descs = data.get("inlineImageDescriptions", [])
        for i, img_desc in enumerate(inline_image_descs):
            inline_prompt = f"Image: {img_desc['description']}. Caption: {img_desc['caption']}."
            inline_fp = os.path.join(IMAGES_BASE_DIR, slug, f"inline_{i+1}.jpg")
            inline_url = generateImage(inline_prompt, inline_fp) or generate_placeholder_image_url(img_desc.get("description", "Inline Image"))
            if inline_url:
                inline_images_list.append({
                    "url": inline_url,
                    "alt": img_desc.get('description', 'Inline image'),
                    "caption": img_desc.get('caption', ''),
                    "placementHint": img_desc.get('placementHint', '')
                })
        content_html = embed_inline_images(data['content'], inline_images_list)
        content_html = add_internal_links(content_html, all_titles_map, slug)

        article = {
            "id": str(article_id_counter), "slug": slug, "title": data['title'],
            "author": DEFAULT_AUTHOR, "publishDate": now, "dateModified": now,
            "category": data['category'], "subCategory": data.get('subCategory', ''),
            "tags": data['keywords'], "excerpt": data['excerpt'], "content": content_html,
            "metaDescription": data['metaDescription'], "keywords": data['keywords'],
            "ogTitle": data['ogTitle'], "ogImage": og_image_url,
            "imageAltText": data['imageAltText'], "ogUrl": f"https://countrysnews.com/articles/{slug}.html",
            "canonicalUrl": f"https://countrysnews.com/articles/{slug}.html", "schemaType": DEFAULT_SCHEMA_TYPE,
            "readingTimeMinutes": reading_time, "wordCount": word_count, "lastReviewedDate": now,
            "relatedArticleIds": [], "socialShareText": data['socialShareText'],
            "adPlacementKeywords": data['adPlacementKeywords'], "adDensity": DEFAULT_AD_DENSITY,
            "sponsorName": DEFAULT_SPONSOR_NAME, "isSponsoredContent": DEFAULT_IS_SPONSORED_CONTENT,
            "factCheckedBy": DEFAULT_FACT_CHECKED_BY, "editorReviewedBy": DEFAULT_EDITOR_REVIEWED_BY,
            "contentType": data['contentType'], "difficultyLevel": data['difficultyLevel'], "featured": False,
            "thumbnailImageUrl": '',  # Add thumbnail code
            "videoUrl": None, "audioUrl": None, "targetAudience": data['targetAudience'],
            "language": DEFAULT_LANGUAGE, "viewsCount": DEFAULT_VIEWS_COUNT, "sharesCount": DEFAULT_SHARES_COUNT,
            "commentsCount": DEFAULT_COMMENTS_COUNT, "averageRating": DEFAULT_AVERAGE_RATING,
            "inlineImages": inline_images_list, "keyTakeaways": data.get('keyTakeaways', []),
            "socialMediaHashtags": data.get('socialMediaHashtags', []), "callToActionText": data.get('callToActionText', ''),
            "structuredData": data.get('structuredData', ""), "sourceKeyword": keyword
        }
        print(f"[OK] Generated: {data['title']}")
        return article

# --- Main Entrypoint ---
async def main():
    load_dotenv()
    print("Starting batch article generation...")
    existing_articles = []
    existing_map = {}
    processed_keywords = set()
    if os.path.exists(ARTICLES_DATA_FILE):
        with open(ARTICLES_DATA_FILE, 'r', encoding='utf-8') as f:
            existing_articles = json.load(f)
        for art in existing_articles:
            if "slug" in art: existing_map[art["slug"]] = art
            if "sourceKeyword" in art and art["sourceKeyword"]: processed_keywords.add(art["sourceKeyword"])
    article_id_counter = max(int(a['id']) for a in existing_articles if 'id' in a and str(a['id']).isdigit())+1 if existing_articles else 1
    all_titles_map = {a['title']: a['slug'] for a in existing_articles if 'title' in a and 'slug' in a}

    # Get fresh keywords
    keywords = get_top_region_keywords(top_n=3)
    if not keywords:
        print("No trending keywords found!")
        return

    # Async batch process
    tasks = []
    async with aiohttp.ClientSession() as session:
        for region, keyword, searches in keywords:
            if keyword in processed_keywords:
                print(f"SKIP: '{keyword}' already processed.")
                continue
            tasks.append(generate_article_from_keyword(session, keyword, region, searches, article_id_counter, all_titles_map))
            article_id_counter += 1
        results = await asyncio.gather(*tasks)

    # Merge, deduplicate, and save
    for art in results:
        if not art: continue
        slug = art["slug"]
        if slug in existing_map:
            existing_map[slug].update(art)
        else:
            existing_map[slug] = art
    with open(ARTICLES_DATA_FILE, 'w', encoding="utf-8") as f:
        json.dump(list(existing_map.values()), f, indent=4, ensure_ascii=False)
    print("Finished! Articles total:", len(existing_map))

if __name__ == "__main__":
    asyncio.run(main())
