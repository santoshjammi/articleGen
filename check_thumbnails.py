#!/usr/bin/env python3
"""
Gentle Thumbnail Checker - A peaceful way to find and fix missing thumbnails
"""

import os
import json
from pathlib import Path

def check_thumbnails():
    """Check which thumbnails are missing and provide gentle solutions"""
    
    print("🔍 Peaceful Thumbnail Investigation")
    print("=" * 50)
    
    # Check articles.json for all articles
    try:
        with open('articles.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ articles.json not found")
        return
    
    print(f"📚 Found {len(articles)} articles to check")
    print()
    
    missing_thumbs = []
    existing_thumbs = []
    
    for article in articles:
        slug = article.get('slug', '')
        if not slug:
            continue
            
        # Check both possible thumbnail paths
        paths_to_check = [
            f"dist/images/{slug}/thumb.webp",
            f"images/{slug}/thumb.webp"
        ]
        
        found = False
        for thumb_path in paths_to_check:
            if os.path.exists(thumb_path):
                existing_thumbs.append({
                    'title': article.get('title', 'Unknown'),
                    'slug': slug,
                    'path': thumb_path
                })
                found = True
                break
        
        if not found:
            missing_thumbs.append({
                'title': article.get('title', 'Unknown'),
                'slug': slug,
                'expected_paths': paths_to_check
            })
    
    # Results
    print(f"✅ Thumbnails found: {len(existing_thumbs)}")
    print(f"❌ Thumbnails missing: {len(missing_thumbs)}")
    print()
    
    if missing_thumbs:
        print("🚨 Missing Thumbnails (First 10):")
        print("-" * 40)
        for i, missing in enumerate(missing_thumbs[:10]):
            print(f"{i+1}. {missing['title'][:60]}...")
            print(f"   Slug: {missing['slug']}")
            print(f"   Expected: {missing['expected_paths'][0]}")
            print()
    
    if len(missing_thumbs) > 10:
        print(f"... and {len(missing_thumbs) - 10} more missing thumbnails")
        print()
    
    # Check if placeholder exists
    placeholder_path = "dist/images/placeholder.jpg"
    if os.path.exists(placeholder_path):
        print("✅ Placeholder image exists")
    else:
        print("❌ Placeholder image missing - this might be why you see broken images")
    
    return missing_thumbs, existing_thumbs

def create_simple_placeholder():
    """Create a simple placeholder if it doesn't exist"""
    placeholder_path = "dist/images/placeholder.jpg"
    if not os.path.exists(placeholder_path):
        print("\n🎨 Creating a simple placeholder image...")
        # For now, just create a text file to indicate the issue
        os.makedirs("dist/images", exist_ok=True)
        with open("dist/images/placeholder_needed.txt", "w") as f:
            f.write("Placeholder image needed here\n")
        print("📝 Created placeholder indicator file")

if __name__ == "__main__":
    missing, existing = check_thumbnails()
    create_simple_placeholder()
    
    print("\n💡 Next Steps:")
    print("1. Run the thumbnail generation script for missing images")
    print("2. Or use existing main.webp files as thumbnails")
    print("3. Create a proper placeholder.jpg image")
