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
    
    # Define directories to process
    directories_to_process = [
        "./images/",
        "./dist/images/", 
        "./images_backup/"
    ]
    
    total_converted = 0
    total_skipped = 0 
    total_errors = 0
    all_error_files = []
    
    print("🔍 Scanning directories for JPG/PNG images to convert...")
    print()
    
    for images_dir in directories_to_process:
        if not os.path.exists(images_dir):
            print(f"⏭️  Directory not found (skipping): {images_dir}")
            continue
            
        print(f"📁 Processing directory: {images_dir}")
        print("🔄 Converting images to WebP format...")
        
        # Convert all images to WebP in this directory
        summary = batch_convert_to_webp(images_dir, quality=85)
        
        # Accumulate totals
        total_converted += summary['converted']
        total_skipped += summary['skipped']
        total_errors += summary['errors']
        all_error_files.extend(summary['error_files'])
        
        print(f"   ✅ Converted: {summary['converted']} images")
        print(f"   ⏭️  Skipped: {summary['skipped']} images")
        print(f"   ❌ Errors: {summary['errors']} images")
        print()
    
    print("=" * 50)
    print("🎉 COMPLETE CONVERSION SUMMARY!")
    print(f"✅ Total successfully converted: {total_converted} images")
    print(f"⏭️  Total already existed (skipped): {total_skipped} images") 
    print(f"❌ Total conversion errors: {total_errors} images")
    
    if total_converted > 0:
        print(f"\n💾 File size savings expected: ~40-70% smaller than original JPG/PNG")
        print(f"🚀 Web loading performance: Significantly improved")
        print(f"📂 Directories processed: {len([d for d in directories_to_process if os.path.exists(d)])}")
    
    if all_error_files:
        print(f"\n❌ Files with errors:")
        for error_file in all_error_files:
            print(f"   - {error_file}")
    
    print(f"\n🔧 Next steps:")
    print(f"   1. Run 'python generateSite.py' to regenerate website with WebP images")
    print(f"   2. New images will automatically be generated as WebP format")
    print(f"   3. All directories now use WebP for faster loading")

if __name__ == "__main__":
    main()
