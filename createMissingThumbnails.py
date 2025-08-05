#!/usr/bin/env python3
"""
Generate Missing Thumbnails
Creates thumbnail images for articles that don't have them.
"""

import json
import os
from generateImage import generateImage

def generate_placeholder_image_url(text, width=400, height=200, bg_color="cccccc", text_color="333333"):
    """Generate placeholder image URL"""
    from urllib.parse import quote
    encoded = quote(text)
    return f"https://placehold.co/{width}x{height}/{bg_color}/{text_color}?text={encoded}"

def create_missing_thumbnails():
    """Create thumbnail images for articles that don't have them"""
    
    # Load articles
    with open('perplexityArticles.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    created_count = 0
    
    for article in articles:
        slug = article.get('slug', '')
        if not slug:
            continue
            
        # Check if thumbnail exists
        thumb_path = os.path.join('dist', 'images', slug, 'thumb.jpg')
        main_path = os.path.join('dist', 'images', slug, 'main.jpg')
        
        if not os.path.exists(thumb_path) and os.path.exists(main_path):
            print(f"Creating thumbnail for: {article.get('title', 'Unknown')}")
            
            # Generate thumbnail
            thumb_prompt = f"Thumbnail for news article: {article.get('ogTitle', article.get('title', 'News Article'))}. Compact, visually appealing, news-style thumbnail."
            
            try:
                thumbnail_url = generateImage(thumb_prompt, thumb_path)
                if thumbnail_url:
                    print(f"✅ Created thumbnail: {thumb_path}")
                    created_count += 1
                else:
                    print(f"⚠️  Failed to create thumbnail for: {slug}")
            except Exception as e:
                print(f"❌ Error creating thumbnail for {slug}: {e}")
    
    print(f"\n🎉 Created {created_count} thumbnails!")

if __name__ == "__main__":
    create_missing_thumbnails()
