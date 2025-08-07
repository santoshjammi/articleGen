#!/usr/bin/env python3
"""
Thumbnail Path Detective - Find path mismatches peacefully
"""

import os
import re
from pathlib import Path

def check_html_vs_filesystem():
    """Compare HTML image paths with actual file system"""
    
    print("🕵️ Peaceful Path Investigation")
    print("=" * 50)
    
    # Read the generated HTML
    try:
        with open('dist/index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("❌ dist/index.html not found")
        return
    
    # Find all image sources
    img_pattern = r'src="([^"]*(?:thumb\.webp|main\.webp|\.jpg|\.png))"'
    img_matches = re.findall(img_pattern, html_content)
    
    print(f"🖼️  Found {len(img_matches)} image references in HTML")
    print()
    
    # Check each image path
    missing_files = []
    existing_files = []
    
    for img_src in img_matches[:15]:  # Check first 15
        # Build full path
        if img_src.startswith('dist/'):
            full_path = img_src
        else:
            full_path = f"dist/{img_src}"
        
        if os.path.exists(full_path):
            existing_files.append(img_src)
            print(f"✅ {img_src}")
        else:
            missing_files.append(img_src)
            print(f"❌ {img_src} -> {full_path}")
    
    if len(img_matches) > 15:
        print(f"... and {len(img_matches) - 15} more images")
    
    print()
    print(f"📊 Summary: {len(existing_files)} found, {len(missing_files)} missing (from first 15)")
    
    if missing_files:
        print("\n🔧 Easy fixes:")
        for missing in missing_files[:5]:
            # Suggest alternatives
            suggestions = []
            
            # Try different path variations
            variations = [
                missing.replace('images/', 'dist/images/'),
                missing.replace('dist/images/', 'images/'),
                missing.replace('thumb.webp', 'main.webp'),
                'dist/images/placeholder.jpg'
            ]
            
            for var in variations:
                if os.path.exists(var):
                    suggestions.append(var)
            
            print(f"\n❌ Missing: {missing}")
            if suggestions:
                print(f"   💡 Found: {suggestions[0]}")
            else:
                print("   💡 No alternatives found")

def check_webp_vs_jpg():
    """Check if we have alternatives for missing images"""
    print("\n🔄 Alternative Format Check")
    print("-" * 30)
    
    # List all available images
    image_dirs = []
    if os.path.exists('dist/images'):
        for item in os.listdir('dist/images'):
            item_path = f"dist/images/{item}"
            if os.path.isdir(item_path):
                image_dirs.append(item)
    
    print(f"📁 Found {len(image_dirs)} image directories")
    
    # Check formats available
    format_stats = {'webp': 0, 'jpg': 0, 'png': 0, 'main.webp': 0, 'thumb.webp': 0}
    
    for dir_name in image_dirs[:10]:  # Check first 10
        dir_path = f"dist/images/{dir_name}"
        files = os.listdir(dir_path)
        
        for file in files:
            if file.endswith('.webp'):
                format_stats['webp'] += 1
                if file == 'main.webp':
                    format_stats['main.webp'] += 1
                elif file == 'thumb.webp':
                    format_stats['thumb.webp'] += 1
            elif file.endswith('.jpg'):
                format_stats['jpg'] += 1
            elif file.endswith('.png'):
                format_stats['png'] += 1
    
    print("\n📈 Image Format Statistics (first 10 dirs):")
    for format_type, count in format_stats.items():
        print(f"   {format_type}: {count}")

if __name__ == "__main__":
    check_html_vs_filesystem()
    check_webp_vs_jpg()
