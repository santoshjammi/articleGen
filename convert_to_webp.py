#!/usr/bin/env python3
"""
WebP Image Conversion Tool for Country's News
Converts existing JPG/PNG images to WebP format for better performance
"""

import os
import sys
sys.path.append('.')

from generateImage import batch_convert_to_webp, convert_to_webp

def main():
    print("🌟 Country's News WebP Image Conversion Tool")
    print("=" * 50)
    
    # Check if images directory exists
    images_dir = "./images/"
    if not os.path.exists(images_dir):
        print(f"❌ Images directory not found: {images_dir}")
        print("No images to convert.")
        return
    
    print(f"📁 Converting images in: {images_dir}")
    print("🔄 Starting batch conversion to WebP format...")
    print()
    
    # Convert all images to WebP
    summary = batch_convert_to_webp(images_dir, quality=85)
    
    print("\n" + "=" * 50)
    print("🎉 Conversion Complete!")
    print(f"✅ Successfully converted: {summary['converted']} images")
    print(f"⏭️  Already existed (skipped): {summary['skipped']} images") 
    print(f"❌ Conversion errors: {summary['errors']} images")
    
    if summary['converted'] > 0:
        print(f"\n💾 File size savings expected: ~40-70% smaller than original JPG/PNG")
        print(f"🚀 Web loading performance: Significantly improved")
    
    if summary['error_files']:
        print(f"\n❌ Files with errors:")
        for error_file in summary['error_files']:
            print(f"   - {error_file}")
    
    print(f"\n🔧 Next steps:")
    print(f"   1. Run 'python generateSite.py' to regenerate website with WebP images")
    print(f"   2. New images will automatically be generated as WebP format")
    print(f"   3. Existing WebP images will be used for faster loading")

if __name__ == "__main__":
    main()
