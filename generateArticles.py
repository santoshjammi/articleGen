import json
import os
import csv
import re
import uuid
from datetime import datetime
import math
import requests
from dotenv import load_dotenv # Import load_dotenv
from getTrendInput import get_top_region_keywords
from generateImage import generateImage # Assuming generateImage function is available from generateImage.py
import base64

# --- Configuration ---
ARTICLES_DATA_FILE = "articles.json"
DEFAULT_AUTHOR = "AI News Generator" # Consider updating this for older articles if 'Your News Reporter' is not desired
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

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
IMAGEN_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict" # Imagen API URL

OUTPUT_DIR = "dist"
IMAGES_BASE_DIR = os.path.join(OUTPUT_DIR, "images")

# --- Helper Functions ---

def generate_slug(title):
    """Generates a URL-friendly slug from a title."""
    slug = re.sub(r'[^\w\s-]', '', title).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

def estimate_reading_time(content):
    """Estimates reading time and word count from HTML content."""
    # Remove HTML tags for accurate word count
    clean_content = re.sub(r'<[^>]+>', '', content)
    words = len(clean_content.split())
    # Average reading speed is about 200 words per minute
    reading_time = math.ceil(words / 200)
    return reading_time, words

def generate_placeholder_image_url(text, width=1200, height=630, bg_color="1f2937", text_color="ffffff"):
    """Generates a placeholder image URL from placehold.co."""
    encoded_text = requests.utils.quote(text)
    return f"https://placehold.co/{width}x{height}/{bg_color}/{text_color}?text={encoded_text}"

def generate_image(prompt, output_filepath):
    """
    Calls the Imagen API to generate an image and saves it to output_filepath.
    Returns the relative URL to the saved image.
    """
    return generateImage(prompt, output_filepath) # Assuming generateImage function is available from generateImage.py


def embed_inline_images(html_content, inline_image_data):
    """
    Embeds inline images into the HTML content based on placement hints.
    This is a simplified regex-based approach.
    """
    modified_content = html_content
    
    # Sort images by their intended placement to avoid issues with shifting indices
    # For simplicity, we'll try to place them after <p> tags or <h3> tags
    # This is a heuristic and might need fine-tuning based on actual content structure
    
    insertions = [] # (index_to_insert_at, html_to_insert)

    for i, img_info in enumerate(inline_image_data):
        img_tag = f'<figure class="my-6">\n<img src="{img_info["url"]}" alt="{img_info["alt"]}" class="w-full rounded-lg shadow-md">\n<figcaption class="text-center text-gray-600 text-sm mt-2">{img_info["caption"]}</figcaption>\n</figure>'
        
        placement_hint = img_info.get("placementHint", "").lower()
        
        if "after first h3" in placement_hint:
            match = re.search(r'(<h3[^>]*>.*?<\/h3>)', modified_content, re.IGNORECASE)
            if match:
                insertions.append((match.end(), img_tag))
                # To avoid re-matching the same h3, we can replace it with a temporary placeholder
                # This is a bit hacky but works for simple regex insertions
                # For more robust parsing, use BeautifulSoup
                modified_content = modified_content[:match.end()] + f"<!-- INSERTED_IMG_{i} -->" + modified_content[match.end():]
        elif "after second h3" in placement_hint:
            matches = list(re.finditer(r'(<h3[^>]*>.*?<\/h3>)', modified_content, re.IGNORECASE))
            if len(matches) > 1:
                insertions.append((matches[1].end(), img_tag))
                modified_content = modified_content[:matches[1].end()] + f"<!-- INSERTED_IMG_{i} -->" + modified_content[matches[1].end():]
        elif "after paragraph" in placement_hint:
            # Try to find a specific paragraph number if hinted, otherwise a general one
            para_num_match = re.search(r'after paragraph (\d+)', placement_hint)
            if para_num_match:
                para_index = int(para_num_match.group(1)) - 1 # Convert to 0-based index
                paragraphs = list(re.finditer(r'(<p[^>]*>.*?<\/p>)', modified_content, re.IGNORECASE | re.DOTALL))
                if len(paragraphs) > para_index:
                    insertions.append((paragraphs[para_index].end(), img_tag))
                    modified_content = modified_content[:paragraphs[para_index].end()] + f"<!-- INSERTED_IMG_{i} -->" + modified_content[paragraphs[para_index].end():]
            else:
                # Default: after first few paragraphs if no specific hint
                paragraphs = list(re.finditer(r'(<p[^>]*>.*?<\/p>)', modified_content, re.IGNORECASE | re.DOTALL))
                if len(paragraphs) > 2: # After the third paragraph
                    insertions.append((paragraphs[2].end(), img_tag))
                    modified_content = modified_content[:paragraphs[2].end()] + f"<!-- INSERTED_IMG_{i} -->" + modified_content[paragraphs[2].end():]
                elif len(paragraphs) > 0: # After the first paragraph if less than 3
                    insertions.append((paragraphs[0].end(), img_tag))
                    modified_content = modified_content[:paragraphs[0].end()] + f"<!-- INSERTED_IMG_{i} -->" + modified_content[paragraphs[0].end():]
        else:
            # Fallback: just append to the end or after the first paragraph
            paragraphs = list(re.finditer(r'(<p[^>]*>.*?<\/p>)', modified_content, re.IGNORECASE | re.DOTALL))
            if paragraphs:
                insertions.append((paragraphs[0].end(), img_tag))
                modified_content = modified_content[:paragraphs[0].end()] + f"<!-- INSERTED_IMG_{i} -->" + modified_content[paragraphs[0].end():]
            else:
                modified_content += img_tag # Append if no paragraphs

    # Reconstruct the content by inserting in reverse order to maintain correct indices
    # And remove the temporary placeholders
    final_content = html_content
    insertions.sort(key=lambda x: x[0], reverse=True)
    for index, tag_html in insertions:
        final_content = final_content[:index] + tag_html + final_content[index:]
    
    # Remove any temporary placeholders used for regex matching
    final_content = re.sub(r'<!-- INSERTED_IMG_\d+ -->', '', final_content)

    return final_content

def add_internal_links(content_html, all_article_titles_map, current_article_slug, max_links=3):
    """
    Scans HTML content and adds internal links to other articles based on their titles.
    Avoids linking within existing <a> tags and limits the number of links.
    """
    linked_content = content_html
    links_added = 0
    
    # Sort titles by length (descending) to prioritize linking longer, more specific titles first
    sorted_titles = sorted(all_article_titles_map.keys(), key=len, reverse=True)

    # Protect existing links by replacing them with a placeholder
    # Store original links to restore them later
    existing_links = re.findall(r'(<a[^>]*>.*?<\/a>)', linked_content, re.IGNORECASE | re.DOTALL)
    linked_content_temp = re.sub(r'<a[^>]*>.*?<\/a>', '@@@EXISTING_LINK_PLACEHOLDER@@@', linked_content, flags=re.IGNORECASE | re.DOTALL)
    
    for title in sorted_titles:
        target_slug = all_article_titles_map[title]
        
        # Skip linking to the current article or if max links reached
        if target_slug == current_article_slug or links_added >= max_links:
            continue
        
        # Create the link HTML
        link_html = f'<a href="../articles/{target_slug}.html" class="text-blue-600 hover:underline font-semibold">{title}</a>'
        
        # Use a simple word boundary regex to find the title in the temporary content
        # This avoids the variable-width lookbehind error
        pattern = r'\b' + re.escape(title) + r'\b'
        
        # Find the first occurrence in the temporary content
        match = re.search(pattern, linked_content_temp, re.IGNORECASE)
        
        if match:
            # Replace only the first occurrence found
            linked_content_temp = re.sub(pattern, link_html, linked_content_temp, 1, flags=re.IGNORECASE)
            links_added += 1
            print(f"    -> Added internal link: '{title}' to '{target_slug}.html'")
                
    # Restore original links from placeholders
    for original_link in existing_links:
        linked_content_temp = linked_content_temp.replace('@@@EXISTING_LINK_PLACEHOLDER@@@', original_link, 1)

    return linked_content_temp


def generate_article_from_keyword(keyword, region, searches, article_id_counter, all_article_titles_map):
    """
    Generates a full article dictionary using the Gemini API based on a keyword.
    """
    global GEMINI_API_KEY
    if not GEMINI_API_KEY:
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not GEMINI_API_KEY:
            print("Error: GEMINI_API_KEY environment variable not set. Cannot call Gemini API.")
            return None

    prompt = f"""
    Generate a comprehensive news article based on the keyword "{keyword}" from the region "{region}". This keyword is trending with "{searches}" searches.
    The article should be informative, engaging, and suitable for a news website.
    The article's content should be substantial, aiming for a minimum of 800-1000 words, and can be longer if the topic allows for more meaningful detail.
    It should cover the topic in depth, providing insights, analysis, and relevant information that would interest readers in {region}.

    In addition to the article content and metadata, also suggest descriptions for 2-3 inline images that could be embedded within the article. For each inline image, provide a brief description (for image generation), a short caption, and a placement hint (e.g., "after first h3", "after paragraph 3").

    Also, provide a concise list of `keyTakeaways` (3-5 bullet points) from the article.
    Suggest 3-5 `socialMediaHashtags` relevant for sharing this article.
    Include a `callToActionText` for the end of the article, encouraging further engagement (e.g., "Share your thoughts in the comments!", "Subscribe to our newsletter!").
    Generate a JSON-LD `structuredData` string for a NewsArticle schema, including relevant fields like `@context`, `@type`, `headline`, `image`, `datePublished`, `dateModified`, `author`, `publisher`, `description`, and `mainEntityOfPage`. Ensure the JSON-LD is a valid string, properly escaped if necessary, and ready to be embedded directly in HTML.

    The response MUST be a JSON object conforming to the following schema.
    """

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

    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": response_schema
        }
    }

    try:
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
            generated_json_str = result["candidates"][0]["content"]["parts"][0]["text"]
            generated_data = json.loads(generated_json_str)

            current_date = datetime.now().strftime("%Y-%m-%d")
            slug = generate_slug(generated_data['title'])
            reading_time, word_count = estimate_reading_time(generated_data['content'])

            # --- Image Generation ---
            article_image_dir = os.path.join(IMAGES_BASE_DIR, slug)
            os.makedirs(article_image_dir, exist_ok=True)

            # 1. Generate Main (ogImage)
            og_image_prompt = f"High-quality, photo-realistic image for news article: '{generated_data['ogTitle']}'. Visual description: '{generated_data['imageAltText']}'. Context: '{generated_data['excerpt']}'. Style: Journalistic, clear, engaging."
            og_image_filepath = os.path.join(article_image_dir, "main.jpg")
            og_image_url = generate_image(og_image_prompt, og_image_filepath) or \
                           generate_placeholder_image_url(generated_data['ogTitle'], width=1200, height=630)

            # 2. Generate Thumbnail
            thumbnail_image_prompt = f"Thumbnail for news article: '{generated_data['ogTitle']}'. Simple visual representation of: '{generated_data['imageAltText']}'. Style: Iconographic, clear."
            thumbnail_image_filepath = os.path.join(article_image_dir, "thumb.jpg")
            thumbnail_image_url = generate_image(thumbnail_image_prompt, thumbnail_image_filepath) or \
                                  generate_placeholder_image_url(generated_data['ogTitle'], width=400, height=200)

            # 3. Generate Inline Images
            inline_images_list = []
            generated_content_html = generated_data['content'] # Start with original content
            for i, img_desc in enumerate(generated_data.get('inlineImageDescriptions', [])):
                inline_prompt = f"Image for news article section: '{img_desc.get('description', keyword)}'. Caption: '{img_desc.get('caption', '')}'. Style: Journalistic, relevant, detailed."
                inline_filepath = os.path.join(article_image_dir, f"inline_{i+1}.jpg")
                inline_url = generate_image(inline_prompt, inline_filepath) or \
                             generate_placeholder_image_url(img_desc.get('description', 'Inline Image'), width=800, height=450)
                
                if inline_url:
                    inline_images_list.append({
                        "url": inline_url,
                        "alt": img_desc.get('description', 'Inline image'),
                        "caption": img_desc.get('caption', '')
                    })
            
            # Embed inline images into the HTML content
            generated_content_html = embed_inline_images(generated_content_html, inline_images_list)


            # Construct the full article dictionary
            article = {
                "id": str(article_id_counter), # Temporary ID, will be updated if existing
                "slug": slug,
                "title": generated_data['title'],
                "author": DEFAULT_AUTHOR,
                "publishDate": current_date,
                "dateModified": current_date,
                "category": generated_data['category'],
                "subCategory": generated_data.get('subCategory', ""),
                "tags": generated_data['keywords'],
                "excerpt": generated_data['excerpt'],
                "content": generated_content_html, # Use content with embedded images
                "metaDescription": generated_data['metaDescription'],
                "keywords": generated_data['keywords'],
                "ogTitle": generated_data['ogTitle'],
                "ogImage": og_image_url,
                "imageAltText": generated_data['imageAltText'],
                "ogUrl": f"https://countrysnews.com/articles/{slug}.html",
                "canonicalUrl": f"https://countrysnews.com/articles/{slug}.html",
                "schemaType": DEFAULT_SCHEMA_TYPE,
                "readingTimeMinutes": reading_time,
                "wordCount": word_count,
                "lastReviewedDate": current_date,
                "relatedArticleIds": [],
                "socialShareText": generated_data['socialShareText'],
                "adPlacementKeywords": generated_data['adPlacementKeywords'],
                "adDensity": DEFAULT_AD_DENSITY,
                "sponsorName": DEFAULT_SPONSOR_NAME,
                "isSponsoredContent": DEFAULT_IS_SPONSORED_CONTENT,
                "factCheckedBy": DEFAULT_FACT_CHECKED_BY,
                "editorReviewedBy": DEFAULT_EDITOR_REVIEWED_BY,
                "contentType": generated_data['contentType'],
                "difficultyLevel": generated_data['difficultyLevel'],
                "featured": False,
                "thumbnailImageUrl": thumbnail_image_url,
                "videoUrl": None,
                "audioUrl": None,
                "targetAudience": generated_data['targetAudience'],
                "language": DEFAULT_LANGUAGE,
                "viewsCount": DEFAULT_VIEWS_COUNT,
                "sharesCount": DEFAULT_SHARES_COUNT,
                "commentsCount": DEFAULT_COMMENTS_COUNT,
                "averageRating": DEFAULT_AVERAGE_RATING,
                "inlineImages": inline_images_list, # New field for inline image metadata
                "keyTakeaways": generated_data.get('keyTakeaways', []), # New field
                "socialMediaHashtags": generated_data.get('socialMediaHashtags', []), # New field
                "callToActionText": generated_data.get('callToActionText', ""), # New field
                "structuredData": generated_data.get('structuredData', ""), # New field
                "sourceKeyword": keyword # Ensure sourceKeyword is set for new articles
            }
            print(f"Successfully generated article data for keyword: {keyword}")
            return article
        else:
            print(f"Error: Gemini API response structure unexpected for keyword: {keyword}")
            print(f"Raw response: {result}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API for keyword '{keyword}': {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Gemini API for keyword '{keyword}': {e}")
        if response and response.text:
            print(f"Raw response text: {response.text[:500]}...")
        return None
    except Exception as e:
        print(f"An unexpected error occurred for keyword '{keyword}': {e}")
        return None

def main():
    load_dotenv()

    print("Starting article generation from keywords...")

    existing_articles_list = []
    existing_articles_map = {}
    processed_keywords = set() # New set to track keywords that have been processed

    if os.path.exists(ARTICLES_DATA_FILE):
        try:
            with open(ARTICLES_DATA_FILE, 'r', encoding='utf-8') as f:
                existing_articles_list = json.load(f)
            print(f"Successfully loaded {len(existing_articles_list)} existing articles from {ARTICLES_DATA_FILE}")
            for article in existing_articles_list:
                if 'slug' in article:
                    existing_articles_map[article['slug']] = article
                else:
                    print(f"Warning: Article with ID {article.get('id', 'N/A')} has no slug. It will be treated as a new article if regenerated.")
                
                # Ensure sourceKeyword is present for all existing articles
                if 'sourceKeyword' not in article or not article['sourceKeyword']:
                    # Attempt to infer source keyword from title or excerpt if missing
                    inferred_keyword = None
                    if 'title' in article and article['title']:
                        inferred_keyword = article['title'].split(':')[0].strip() # Simple heuristic
                    elif 'excerpt' in article and article['excerpt']:
                        inferred_keyword = article['excerpt'].split(' ')[0].strip() # Another simple heuristic
                    article['sourceKeyword'] = inferred_keyword if inferred_keyword else None
                    if article['sourceKeyword']:
                        print(f"  -> Backfilled sourceKeyword '{article['sourceKeyword']}' for article: {article.get('title', 'N/A')}")
                
                # Add existing sourceKeywords to the processed set
                if 'sourceKeyword' in article and article['sourceKeyword']:
                    processed_keywords.add(article['sourceKeyword'])

        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {ARTICLES_DATA_FILE}. Starting with empty articles list.")
            existing_articles_list = []
            existing_articles_map = {}
        except FileNotFoundError:
            print(f"Warning: {ARTICLES_DATA_FILE} not found. Starting with empty articles list.")
            existing_articles_list = []
            existing_articles_map = {}
    else:
        print(f"Info: {ARTICLES_DATA_FILE} not found. A new file will be created.")

    max_id = 0
    if existing_articles_list:
        try:
            max_id = max(int(article['id']) for article in existing_articles_list if 'id' in article and str(article['id']).isdigit())
        except ValueError:
            print("Warning: Non-integer article IDs found or 'id' field missing. Starting new IDs from 1.")
            max_id = 0
    article_id_counter = max_id + 1

    # Prepare a map of all existing article titles to their slugs for internal linking
    all_article_titles_map = {
        article['title']: article['slug']
        for article in existing_articles_list if 'title' in article and 'slug' in article
    }

    # Fetch top 3 keywords (changed from 20 to 3)
    keywords_from_trends = get_top_region_keywords(top_n=3)
    if not keywords_from_trends:
        print("No keywords found from trending input. Exiting.")
        return

    print(f"Successfully loaded {len(keywords_from_trends)} keywords from trending input.")

    newly_generated_count = 0
    updated_count = 0
    skipped_count = 0 # New counter for skipped keywords

    # Define all possible fields with their default values for new articles
    all_article_fields_defaults = {
        "id": None,
        "slug": None,
        "title": None,
        "author": DEFAULT_AUTHOR,
        "publishDate": None,
        "dateModified": None,
        "category": None,
        "subCategory": "",
        "tags": [],
        "excerpt": None,
        "content": None,
        "metaDescription": None,
        "keywords": [],
        "ogTitle": None,
        "ogImage": None,
        "imageAltText": None,
        "ogUrl": None,
        "canonicalUrl": None,
        "schemaType": DEFAULT_SCHEMA_TYPE,
        "readingTimeMinutes": 0,
        "wordCount": 0,
        "lastReviewedDate": None,
        "relatedArticleIds": [],
        "socialShareText": None,
        "adPlacementKeywords": [],
        "adDensity": DEFAULT_AD_DENSITY,
        "sponsorName": DEFAULT_SPONSOR_NAME,
        "isSponsoredContent": DEFAULT_IS_SPONSORED_CONTENT,
        "factCheckedBy": DEFAULT_FACT_CHECKED_BY,
        "editorReviewedBy": DEFAULT_EDITOR_REVIEWED_BY,
        "contentType": None,
        "difficultyLevel": None,
        "featured": False,
        "thumbnailImageUrl": None,
        "videoUrl": None,
        "audioUrl": None,
        "targetAudience": [],
        "language": DEFAULT_LANGUAGE,
        "viewsCount": DEFAULT_VIEWS_COUNT,
        "sharesCount": DEFAULT_SHARES_COUNT,
        "commentsCount": DEFAULT_COMMENTS_COUNT,
        "averageRating": DEFAULT_AVERAGE_RATING,
        "inlineImages": [],
        "keyTakeaways": [],
        "socialMediaHashtags": [],
        "callToActionText": "",
        "structuredData": "",
        "sourceKeyword": None # New field to track the keyword that generated/updated the article
    }

    for region, keyword, searches in keywords_from_trends:
        # Check if this keyword has already been processed
        if keyword in processed_keywords:
            print(f"Skipping keyword '{keyword}' as it has already been processed.")
            skipped_count += 1
            continue # Skip to the next keyword

        print(f"Processing keyword: '{keyword}' (Region: {region}, Searches: {searches})...")
        generated_article_data = generate_article_from_keyword(keyword, region, searches, article_id_counter, all_article_titles_map)

        if generated_article_data:
            slug = generated_article_data['slug']
            
            if slug in existing_articles_map:
                existing_article = existing_articles_map[slug]
                print(f"  -> Updating existing article: '{existing_article['title']}' (ID: {existing_article['id']})")

                # --- START: Logic to ensure all fields are present in existing_article and updated ---
                for field, default_value in all_article_fields_defaults.items():
                    if field not in existing_article:
                        existing_article[field] = default_value
                    
                    # Special handling for lists that should be merged (union of old and new)
                    if isinstance(existing_article.get(field), list) and field in ['keywords', 'tags', 'adPlacementKeywords', 'targetAudience', 'keyTakeaways', 'socialMediaHashtags']:
                        existing_list = set(existing_article.get(field, []))
                        new_list = set(generated_article_data.get(field, []))
                        existing_article[field] = list(existing_list.union(new_list))
                    # Fields that should be directly overwritten by the new generated data
                    elif field in ['title', 'excerpt', 'content', 'metaDescription', 'ogTitle', 'ogImage', 'imageAltText',
                                  'socialShareText', 'category', 'subCategory', 'contentType', 'difficultyLevel',
                                  'readingTimeMinutes', 'wordCount', 'inlineImages', 'callToActionText', 'structuredData', 'sourceKeyword']: # Added sourceKeyword here
                        existing_article[field] = generated_article_data.get(field, default_value)
                    # Fields that should preserve their existing value unless they are default/empty
                    elif field in ['viewsCount', 'sharesCount', 'commentsCount', 'averageRating', 'featured', 'videoUrl', 'audioUrl', 'language', 'sponsorName', 'isSponsoredContent', 'factCheckedBy', 'editorReviewedBy', 'schemaType', 'adDensity', 'relatedArticleIds']:
                        if existing_article.get(field) is None or existing_article.get(field) == default_value:
                            existing_article[field] = generated_article_data.get(field, default_value)
                    elif field == 'author':
                        if existing_article.get(field) == "Your News Reporter" or existing_article.get(field) is None:
                            existing_article[field] = generated_article_data.get(field, DEFAULT_AUTHOR)
                    elif field in ['publishDate', 'ogUrl', 'canonicalUrl']:
                        if existing_article.get(field) is None or existing_article.get(field) == all_article_fields_defaults.get(field):
                             existing_article[field] = generated_article_data.get(field, default_value)
                    
                # Always update modification dates
                existing_article['dateModified'] = datetime.now().strftime("%Y-%m-%d")
                existing_article['lastReviewedDate'] = datetime.now().strftime("%Y-%m-%d")
                existing_article['sourceKeyword'] = keyword # Explicitly set/update sourceKeyword on update

                updated_count += 1
            else:
                # New article: Initialize with all defaults and then populate from generated data
                new_article = all_article_fields_defaults.copy()
                new_article.update(generated_article_data) # Overwrite defaults with generated data

                new_article['id'] = str(article_id_counter)
                new_article['publishDate'] = datetime.now().strftime("%Y-%m-%d")
                new_article['dateModified'] = datetime.now().strftime("%Y-%m-%d")
                new_article['lastReviewedDate'] = datetime.now().strftime("%Y-%m-%d")
                new_article['ogUrl'] = f"https://countrysnews.com/articles/{new_article['slug']}.html"
                new_article['canonicalUrl'] = f"https://countrysnews.com/articles/{new_article['slug']}.html"
                new_article['sourceKeyword'] = keyword # Set sourceKeyword for new article
                
                existing_articles_map[slug] = new_article
                article_id_counter += 1
                newly_generated_count += 1
            
            # Add the keyword to the processed set after successful generation/update
            processed_keywords.add(keyword)
        else:
            print(f"  -> Failed to generate article for '{keyword}'. Skipping.")

    final_articles_list = list(existing_articles_map.values())

    try:
        with open(ARTICLES_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_articles_list, f, indent=4, ensure_ascii=False)
        print(f"\nArticle generation and update process complete.")
        print(f"Summary: {newly_generated_count} new articles generated, {updated_count} existing articles updated, {skipped_count} keywords skipped (Total: {len(final_articles_list)} articles).")
    except Exception as e:
        print(f"Error saving articles to {ARTICLES_DATA_FILE}: {e}")

if __name__ == "__main__":
    main()
