#!/usr/bin/env python3
"""
Keyword-Based Article Generator
Generates high-quality SEO articles based on specific keywords provided by the user.
Similar to perplexitySEOArticleGen.py but allows manual keyword input.
"""

import os
import re
import json
import math
import aiohttp
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional
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

# --- Helper Functions ---

def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug

def estimate_reading_time(content: str) -> Tuple[int, int]:
    """Estimate reading time and word count"""
    clean_content = re.sub(r"<[^>]+>", "", content)
    words = len(clean_content.split())
    reading_time = math.ceil(words / 200)
    return reading_time, words

def generate_placeholder_image_url(text: str, width: int = 1200, height: int = 630, 
                                 bg_color: str = "1f2937", text_color: str = "ffffff") -> str:
    """Generate placeholder image URL"""
    from urllib.parse import quote
    encoded = quote(text)
    return f"https://placehold.co/{width}x{height}/{bg_color}/{text_color}?text={encoded}"

def embed_inline_images(html_content: str, inline_images: List[Dict]) -> str:
    """Embed inline images into HTML content"""
    content = html_content
    for img in inline_images:
        paragraphs = list(re.finditer(r'(<p[^>]*>.*?</p>)', content, re.IGNORECASE | re.DOTALL))
        placement_hint = img.get("placementHint", "")
        match = re.search(r"paragraph\s*(\d+)", placement_hint)
        n = int(match.group(1)) if match else 2
        
        insert_at = paragraphs[n-1].end() if len(paragraphs) >= n else len(content)
        img_tag = f'<img src="{img["url"]}" alt="{img["alt"]}" style="max-width:100%; height:auto; margin: 1rem 0;" />'
        if img.get("caption"):
            img_tag += f'<p style="font-size: 0.9em; color: #666; font-style: italic; text-align: center;">{img["caption"]}</p>'
        content = content[:insert_at] + img_tag + content[insert_at:]
    return content

def add_internal_links(content_html: str, all_titles_map: Dict[str, str], 
                      current_slug: str, max_links: int = 3) -> str:
    """Add internal links to related articles"""
    linked_content = content_html
    links_added = 0
    sorted_titles = sorted([t for t in all_titles_map if all_titles_map[t] != current_slug], 
                          key=len, reverse=True)
    
    for title in sorted_titles:
        if links_added >= max_links:
            break
        pattern = r"\b" + re.escape(title) + r"\b"
        if re.search(pattern, linked_content, re.IGNORECASE):
            slug = all_titles_map[title]
            link_tag = f'<a href="/articles/{slug}.html" style="color: #2563eb; text-decoration: underline;">{title}</a>'
            linked_content, count = re.subn(pattern, link_tag, linked_content, 
                                          count=1, flags=re.IGNORECASE)
            if count > 0:
                links_added += 1
    return linked_content

def expand_keywords(base_keyword: str, target_region: str = "India") -> List[str]:
    """Expand a base keyword into related keywords for better SEO coverage"""
    expansions = [
        f"{base_keyword} in {target_region}",
        f"{base_keyword} news",
        f"{base_keyword} latest updates",
        f"{base_keyword} analysis",
        f"{base_keyword} trends 2025",
        f"what is {base_keyword}",
        f"{base_keyword} benefits",
        f"{base_keyword} impact",
        f"{base_keyword} guide",
        f"{base_keyword} overview"
    ]
    return [base_keyword] + expansions

def validate_keyword_input(keywords: List[str]) -> List[str]:
    """Validate and clean keyword input"""
    cleaned_keywords = []
    for keyword in keywords:
        if isinstance(keyword, str) and keyword.strip():
            cleaned = keyword.strip().lower()
            if len(cleaned) >= 2 and cleaned not in cleaned_keywords:
                cleaned_keywords.append(cleaned)
    return cleaned_keywords

async def generate_article_from_specific_keyword(session: aiohttp.ClientSession, 
                                               keyword: str, region: str, 
                                               article_id_counter: int, 
                                               all_titles_map: Dict[str, str],
                                               custom_prompt_additions: str = "") -> Optional[Dict]:
    """Generate article from a specific keyword with enhanced customization"""
    
    # Create enhanced prompt
    base_prompt = f"""Generate a comprehensive, engaging news article about "{keyword}" specifically for readers in {region}. 

    Requirements:
    - 1200+ words of high-quality, informative content
    - SEO-optimized with natural keyword integration
    - Include current trends and recent developments
    - Professional journalistic tone
    - Well-structured with clear headings and paragraphs
    - Include quotes, statistics, or expert opinions where relevant
    - Ensure content is accurate and factual
    
    {custom_prompt_additions}
    
    The article should be engaging, informative, and provide real value to readers interested in {keyword}."""

    headers = {'Content-Type': 'application/json'}
    
    # Enhanced response schema
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "title": {"type": "STRING", "description": "Compelling, SEO-optimized title (60 chars max)"},
            "excerpt": {"type": "STRING", "description": "Engaging summary (150-160 chars)"},
            "content": {"type": "STRING", "description": "Full HTML article content (1200+ words)"},
            "metaDescription": {"type": "STRING", "description": "SEO meta description (150-160 chars)"},
            "keywords": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "10-15 relevant SEO keywords"},
            "ogTitle": {"type": "STRING", "description": "Social media optimized title"},
            "imageAltText": {"type": "STRING", "description": "Descriptive alt text for main image"},
            "socialShareText": {"type": "STRING", "description": "Compelling social media share text"},
            "adPlacementKeywords": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Keywords for ad targeting"},
            "category": {"type": "STRING", "description": "Main article category"},
            "subCategory": {"type": "STRING", "description": "Specific subcategory"},
            "contentType": {"type": "STRING", "description": "Content type (news, analysis, guide, etc.)"},
            "difficultyLevel": {"type": "STRING", "description": "Reading difficulty (beginner, intermediate, advanced)"},
            "targetAudience": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Target audience segments"},
            "inlineImageDescriptions": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "description": {"type": "STRING", "description": "Image content description"},
                        "caption": {"type": "STRING", "description": "Image caption"},
                        "placementHint": {"type": "STRING", "description": "Where to place (e.g., 'after paragraph 3')"}
                    },
                    "required": ["description", "caption"]
                },
                "description": "2-4 inline images for the article"
            },
            "keyTakeaways": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "3-5 key points"},
            "socialMediaHashtags": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Relevant hashtags"},
            "callToActionText": {"type": "STRING", "description": "Engaging CTA for readers"},
            "structuredData": {"type": "STRING", "description": "JSON-LD structured data for SEO"},
            "relatedTopics": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Related topics for further reading"}
        },
        "required": [
            "title", "excerpt", "content", "metaDescription", "keywords",
            "ogTitle", "imageAltText", "socialShareText", "adPlacementKeywords",
            "category", "contentType", "difficultyLevel", "targetAudience",
            "inlineImageDescriptions", "keyTakeaways", "socialMediaHashtags", 
            "callToActionText", "structuredData"
        ]
    }

    payload = {
        "contents": [{"role": "user", "parts": [{"text": base_prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
            "temperature": 0.7,
            "maxOutputTokens": 8192
        }
    }

    url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    
    try:
        async with session.post(url, headers=headers, data=json.dumps(payload)) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                print(f"❌ API error {resp.status} for '{keyword}': {error_text}")
                return None
                
            result = await resp.json()
            
            if not (result.get("candidates") and 
                   result["candidates"][0].get("content") and 
                   result["candidates"][0]["content"].get("parts")):
                print(f"❌ Invalid API response structure for '{keyword}'")
                return None
                
            gen_str = result["candidates"][0]["content"]["parts"][0]["text"]
            data = json.loads(gen_str)
            
            # Generate article metadata
            now = datetime.now().strftime("%Y-%m-%d")
            slug = generate_slug(data['title'])
            reading_time, word_count = estimate_reading_time(data['content'])
            
            # Create images directory
            os.makedirs(os.path.join(IMAGES_BASE_DIR, slug), exist_ok=True)
            
            # Generate main image
            og_image_prompt = f"Professional news article image for: {data['ogTitle']}. Visual style: {data['imageAltText']}. High quality, news-appropriate."
            og_img_fp = os.path.join(IMAGES_BASE_DIR, slug, "main.jpg")
            og_image_url = generateImage(og_image_prompt, og_img_fp) or generate_placeholder_image_url(data['ogTitle'])
            
            # Generate thumbnail image (smaller version for article cards)
            thumb_image_prompt = f"Thumbnail for news article: {data['ogTitle']}. Compact, visually appealing, news-style thumbnail."
            thumb_img_fp = os.path.join(IMAGES_BASE_DIR, slug, "thumb.jpg")
            thumbnail_url = generateImage(thumb_image_prompt, thumb_img_fp) or generate_placeholder_image_url(data['ogTitle'], 400, 200)
            
            # Generate inline images
            inline_images_list = []
            inline_image_descs = data.get("inlineImageDescriptions", [])
            
            for i, img_desc in enumerate(inline_image_descs):
                inline_prompt = f"Supporting image for article section: {img_desc['description']}. Caption context: {img_desc['caption']}. Professional, high-quality."
                inline_fp = os.path.join(IMAGES_BASE_DIR, slug, f"inline_{i+1}.jpg")
                inline_url = generateImage(inline_prompt, inline_fp) or generate_placeholder_image_url(
                    img_desc.get("description", f"Article Image {i+1}")
                )
                
                if inline_url:
                    inline_images_list.append({
                        "url": inline_url,
                        "alt": img_desc.get('description', f'Article illustration {i+1}'),
                        "caption": img_desc.get('caption', ''),
                        "placementHint": img_desc.get('placementHint', f'after paragraph {i+2}')
                    })
            
            # Process content
            content_html = embed_inline_images(data['content'], inline_images_list)
            content_html = add_internal_links(content_html, all_titles_map, slug)
            
            # Expand keywords for better SEO
            expanded_keywords = expand_keywords(keyword, region)
            all_keywords = list(set(data['keywords'] + expanded_keywords))
            
            # Build complete article object
            article = {
                "id": str(article_id_counter),
                "slug": slug,
                "title": data['title'],
                "author": DEFAULT_AUTHOR,
                "publishDate": now,
                "dateModified": now,
                "category": data['category'],
                "subCategory": data.get('subCategory', ''),
                "tags": all_keywords,
                "excerpt": data['excerpt'],
                "content": content_html,
                "metaDescription": data['metaDescription'],
                "keywords": all_keywords,
                "ogTitle": data['ogTitle'],
                "ogImage": og_image_url,
                "imageAltText": data['imageAltText'],
                "ogUrl": f"https://countrysnews.com/articles/{slug}.html",
                "canonicalUrl": f"https://countrysnews.com/articles/{slug}.html",
                "schemaType": DEFAULT_SCHEMA_TYPE,
                "readingTimeMinutes": reading_time,
                "wordCount": word_count,
                "lastReviewedDate": now,
                "relatedArticleIds": [],
                "socialShareText": data['socialShareText'],
                "adPlacementKeywords": data['adPlacementKeywords'],
                "adDensity": DEFAULT_AD_DENSITY,
                "sponsorName": DEFAULT_SPONSOR_NAME,
                "isSponsoredContent": DEFAULT_IS_SPONSORED_CONTENT,
                "factCheckedBy": DEFAULT_FACT_CHECKED_BY,
                "editorReviewedBy": DEFAULT_EDITOR_REVIEWED_BY,
                "contentType": data['contentType'],
                "difficultyLevel": data['difficultyLevel'],
                "featured": False,
                "thumbnailImageUrl": thumbnail_url,  # Use dedicated thumbnail image
                "videoUrl": None,
                "audioUrl": None,
                "targetAudience": data['targetAudience'],
                "language": DEFAULT_LANGUAGE,
                "viewsCount": DEFAULT_VIEWS_COUNT,
                "sharesCount": DEFAULT_SHARES_COUNT,
                "commentsCount": DEFAULT_COMMENTS_COUNT,
                "averageRating": DEFAULT_AVERAGE_RATING,
                "inlineImages": inline_images_list,
                "keyTakeaways": data.get('keyTakeaways', []),
                "socialMediaHashtags": data.get('socialMediaHashtags', []),
                "callToActionText": data.get('callToActionText', ''),
                "structuredData": data.get('structuredData', ""),
                "sourceKeyword": keyword,
                "relatedTopics": data.get('relatedTopics', []),
                "generationMethod": "keyword_based",
                "region": region
            }
            
            print(f"✅ Generated: '{data['title']}' ({word_count} words)")
            return article
            
    except Exception as e:
        print(f"❌ Error generating article for '{keyword}': {str(e)}")
        return None

def load_existing_articles() -> Tuple[List[Dict], Dict[str, Dict], set]:
    """Load existing articles and create lookup structures"""
    existing_articles = []
    existing_map = {}
    processed_keywords = set()
    
    if os.path.exists(ARTICLES_DATA_FILE):
        try:
            with open(ARTICLES_DATA_FILE, 'r', encoding='utf-8') as f:
                existing_articles = json.load(f)
                
            for art in existing_articles:
                if "slug" in art:
                    existing_map[art["slug"]] = art
                if "sourceKeyword" in art and art["sourceKeyword"]:
                    processed_keywords.add(art["sourceKeyword"].lower())
        except Exception as e:
            print(f"⚠️  Error loading existing articles: {e}")
    
    return existing_articles, existing_map, processed_keywords

def save_articles(existing_map: Dict[str, Dict]) -> None:
    """Save articles to JSON file with backup"""
    try:
        # Create backup
        if os.path.exists(ARTICLES_DATA_FILE):
            backup_file = f"{ARTICLES_DATA_FILE}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(ARTICLES_DATA_FILE, backup_file)
            print(f"📁 Backup created: {backup_file}")
        
        # Save updated articles
        with open(ARTICLES_DATA_FILE, 'w', encoding="utf-8") as f:
            json.dump(list(existing_map.values()), f, indent=4, ensure_ascii=False)
        
        print(f"💾 Articles saved successfully. Total: {len(existing_map)}")
        
    except Exception as e:
        print(f"❌ Error saving articles: {e}")

async def generate_articles_from_keywords(keywords: List[str], region: str = "India", 
                                        custom_prompt: str = "", 
                                        skip_existing: bool = True) -> None:
    """Main function to generate articles from specific keywords"""
    
    print(f"🚀 Starting keyword-based article generation...")
    print(f"📍 Target region: {region}")
    print(f"🎯 Keywords: {', '.join(keywords)}")
    
    # Load existing data
    existing_articles, existing_map, processed_keywords = load_existing_articles()
    
    # Calculate next article ID
    article_id_counter = 1
    if existing_articles:
        max_id = max(int(a['id']) for a in existing_articles 
                    if 'id' in a and str(a['id']).isdigit())
        article_id_counter = max_id + 1
    
    # Create title mapping for internal links
    all_titles_map = {a['title']: a['slug'] for a in existing_articles 
                     if 'title' in a and 'slug' in a}
    
    # Filter keywords
    keywords_to_process = []
    for keyword in validate_keyword_input(keywords):
        if skip_existing and keyword in processed_keywords:
            print(f"⏭️  SKIP: '{keyword}' already processed")
            continue
        keywords_to_process.append(keyword)
    
    if not keywords_to_process:
        print("ℹ️  No new keywords to process!")
        return
    
    print(f"📝 Processing {len(keywords_to_process)} keywords...")
    
    # Generate articles
    tasks = []
    async with aiohttp.ClientSession() as session:
        for keyword in keywords_to_process:
            task = generate_article_from_specific_keyword(
                session, keyword, region, article_id_counter, 
                all_titles_map, custom_prompt
            )
            tasks.append(task)
            article_id_counter += 1
        
        print("⏳ Generating articles... This may take a few minutes.")
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_articles = 0
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Task failed with exception: {result}")
            continue
            
        if result:
            slug = result["slug"]
            if slug in existing_map:
                existing_map[slug].update(result)
                print(f"🔄 Updated existing article: {result['title']}")
            else:
                existing_map[slug] = result
                print(f"✨ Added new article: {result['title']}")
            successful_articles += 1
    
    # Save results
    if successful_articles > 0:
        save_articles(existing_map)
        print(f"🎉 Success! Generated {successful_articles} articles.")
    else:
        print("⚠️  No articles were generated successfully.")

def interactive_keyword_input() -> Tuple[List[str], str, str]:
    """Interactive mode for keyword input"""
    print("\n" + "="*60)
    print("🔤 KEYWORD-BASED ARTICLE GENERATOR")
    print("="*60)
    
    # Get keywords
    print("\n📝 Enter keywords (one per line, empty line to finish):")
    keywords = []
    while True:
        keyword = input("Keyword: ").strip()
        if not keyword:
            break
        keywords.append(keyword)
    
    # Get region
    region = input(f"\n🌍 Target region (default: India): ").strip() or "India"
    
    # Get custom prompt
    print(f"\n✍️  Custom prompt additions (optional, press Enter to skip):")
    custom_prompt = input("Additional requirements: ").strip()
    
    return keywords, region, custom_prompt

async def main():
    """Main entry point"""
    import sys
    
    load_dotenv()
    
    # Check for API key
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not found in environment variables!")
        print("Please add your Gemini API key to your .env file.")
        return
    
    # Command line arguments or interactive mode
    if len(sys.argv) > 1:
        # Command line mode
        keywords = sys.argv[1:]
        region = "India"
        custom_prompt = ""
    else:
        # Interactive mode
        keywords, region, custom_prompt = interactive_keyword_input()
    
    if not keywords:
        print("❌ No keywords provided!")
        return
    
    await generate_articles_from_keywords(keywords, region, custom_prompt)
    print("\n✅ Article generation complete!")

if __name__ == "__main__":
    asyncio.run(main())
