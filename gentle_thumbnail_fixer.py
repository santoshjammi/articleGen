#!/usr/bin/env python3
"""
Gentle Thumbnail Fixer - Peaceful solutions for missing thumbnails
"""

import os
import shutil
import json
from PIL import Image, ImageDraw, ImageFont
import io

def create_simple_placeholder():
    """Create a beautiful, simple placeholder image"""
    print("🎨 Creating a beautiful placeholder image...")
    
    # Create a 400x300 image with a pleasant gradient
    width, height = 400, 300
    img = Image.new('RGB', (width, height), color='#f8fafc')
    draw = ImageDraw.Draw(img)
    
    # Create a subtle gradient background
    for y in range(height):
        color_intensity = int(248 - (y / height) * 20)  # Subtle gradient
        draw.line([(0, y), (width, y)], fill=(color_intensity, color_intensity + 2, color_intensity + 5))
    
    # Add a border
    border_color = '#e2e8f0'
    draw.rectangle([5, 5, width-5, height-5], outline=border_color, width=2)
    
    # Add centered text
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
    
    text = "📰 News Image"
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center the text
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw text with shadow
    draw.text((x+2, y+2), text, fill='#cbd5e0', font=font)  # Shadow
    draw.text((x, y), text, fill='#64748b', font=font)      # Main text
    
    # Save as JPG for better compatibility
    placeholder_path = 'dist/images/placeholder.jpg'
    os.makedirs('dist/images', exist_ok=True)
    img.save(placeholder_path, 'JPEG', quality=90)
    
    print(f"✅ Created placeholder: {placeholder_path}")
    return placeholder_path

def copy_main_to_thumb():
    """Copy main.webp to thumb.webp where thumb is missing"""
    print("\n🔄 Creating missing thumbnails from main images...")
    
    copied_count = 0
    
    # Walk through all article directories
    if os.path.exists('dist/images'):
        for item in os.listdir('dist/images'):
            item_path = f"dist/images/{item}"
            if os.path.isdir(item_path):
                thumb_path = f"{item_path}/thumb.webp"
                main_path = f"{item_path}/main.webp"
                
                # If thumb is missing but main exists, copy it
                if not os.path.exists(thumb_path) and os.path.exists(main_path):
                    try:
                        shutil.copy2(main_path, thumb_path)
                        print(f"   ✅ Created {item}/thumb.webp from main.webp")
                        copied_count += 1
                    except Exception as e:
                        print(f"   ❌ Failed to copy {item}: {e}")
    
    print(f"📊 Created {copied_count} thumbnails from main images")
    return copied_count

def fix_article_paths():
    """Update articles.json to use correct thumbnail paths"""
    print("\n🔧 Checking article thumbnail paths...")
    
    try:
        with open('articles.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ articles.json not found")
        return False
    
    updated_count = 0
    
    for article in articles:
        slug = article.get('slug', '')
        if not slug:
            continue
        
        # Check current thumbnail path
        current_thumb = article.get('thumbnailImageUrl', '')
        
        # Preferred path
        preferred_path = f"dist/images/{slug}/thumb.webp"
        
        # If current path doesn't exist, try to find alternatives
        if not os.path.exists(current_thumb.replace('dist/', '') if current_thumb.startswith('dist/') else f"dist/{current_thumb}"):
            
            # Try different alternatives
            alternatives = [
                f"dist/images/{slug}/thumb.webp",
                f"dist/images/{slug}/main.webp",
                f"images/{slug}/thumb.webp",
                f"images/{slug}/main.webp",
                "dist/images/placeholder.jpg"
            ]
            
            for alt in alternatives:
                if os.path.exists(alt):
                    # Update the article
                    if alt.startswith('dist/'):
                        article['thumbnailImageUrl'] = alt
                    else:
                        article['thumbnailImageUrl'] = alt
                    updated_count += 1
                    print(f"   ✅ Updated {slug}: {alt}")
                    break
    
    if updated_count > 0:
        # Save updated articles
        with open('articles.json', 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"📝 Updated {updated_count} article paths")
        return True
    else:
        print("✅ All article paths look good")
        return False

def gentle_regenerate():
    """Offer to regenerate the site with fixed paths"""
    print("\n🔄 Would you like to regenerate the website with fixed thumbnails?")
    print("   This will ensure all thumbnail paths are correct")
    
    # Just show the command, don't run it automatically
    print("\n💡 To regenerate with fixes:")
    print("   python3 generateSite_advanced.py")

def main():
    """Run all gentle fixes"""
    print("🕊️  Gentle Thumbnail Repair Tool")
    print("=" * 50)
    print("Working peacefully to fix thumbnail issues...")
    print()
    
    # Step 1: Create placeholder
    try:
        create_simple_placeholder()
    except ImportError:
        print("ℹ️  PIL not available, skipping custom placeholder creation")
        print("   You can manually add a placeholder.jpg to dist/images/")
    except Exception as e:
        print(f"⚠️  Could not create placeholder: {e}")
    
    # Step 2: Copy main to thumb where needed
    copy_main_to_thumb()
    
    # Step 3: Fix article paths
    paths_updated = fix_article_paths()
    
    # Step 4: Suggest next steps
    print("\n🎯 Suggested Next Steps:")
    print("1. Check the thumbnail test page: http://localhost:8080/thumbnail_test.html")
    print("2. Open browser Dev Tools → Network tab to see any 404 errors")
    
    if paths_updated:
        print("3. Regenerate the website: python3 generateSite_advanced.py")
    
    print("4. Clear browser cache if needed (Ctrl+F5 or Cmd+Shift+R)")
    
    print("\n✨ Remember: We're taking a peaceful, step-by-step approach!")

if __name__ == "__main__":
    main()
