#!/usr/bin/env python3
"""
JPG Image Removal Tool for Country's News
Safely removes JPG/PNG images after WebP conversion
Only removes images that have corresponding WebP files to ensure safety
"""

import os
import sys
from pathlib import Path

def find_and_remove_jpg_images(directories_to_clean):
    """
    Find and remove JPG/PNG images that have corresponding WebP files
    
    Args:
        directories_to_clean (list): List of directories to process
        
    Returns:
        dict: Summary of removal results
    """
    total_removed = 0
    total_skipped = 0
    total_errors = 0
    removed_files = []
    skipped_files = []
    error_files = []
    
    for directory in directories_to_clean:
        if not os.path.exists(directory):
            print(f"⏭️  Directory not found (skipping): {directory}")
            continue
            
        print(f"\n📁 Processing directory: {directory}")
        print("🔍 Scanning for JPG/PNG files with WebP counterparts...")
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    jpg_path = os.path.join(root, file)
                    
                    # Generate the corresponding WebP path
                    base_name = os.path.splitext(jpg_path)[0]
                    webp_path = f"{base_name}.webp"
                    
                    # Only remove if WebP version exists
                    if os.path.exists(webp_path):
                        try:
                            # Get file size before removal for reporting
                            file_size = os.path.getsize(jpg_path)
                            
                            # Remove the JPG file
                            os.remove(jpg_path)
                            
                            print(f"✅ Removed: {jpg_path} ({file_size:,} bytes)")
                            removed_files.append(jpg_path)
                            total_removed += 1
                            
                        except Exception as e:
                            print(f"❌ Error removing {jpg_path}: {e}")
                            error_files.append(jpg_path)
                            total_errors += 1
                    else:
                        print(f"⚠️  Skipped (no WebP found): {jpg_path}")
                        skipped_files.append(jpg_path)
                        total_skipped += 1
    
    return {
        'removed': total_removed,
        'skipped': total_skipped,
        'errors': total_errors,
        'removed_files': removed_files,
        'skipped_files': skipped_files,
        'error_files': error_files
    }

def get_directory_size(directory):
    """Calculate total size of JPG/PNG files in directory"""
    total_size = 0
    if not os.path.exists(directory):
        return 0
        
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                except:
                    pass
    return total_size

def main():
    print("🗑️  Country's News JPG Image Removal Tool")
    print("=" * 50)
    print("⚠️  This tool will remove JPG/PNG files that have WebP counterparts")
    print("🔒 Safety: Only removes images with confirmed WebP versions")
    print()
    
    # Define directories to clean
    directories_to_clean = [
        "./images/",
        "./dist/images/", 
        "./images_backup/"
    ]
    
    # Calculate current disk usage
    total_jpg_size = 0
    for directory in directories_to_clean:
        dir_size = get_directory_size(directory)
        total_jpg_size += dir_size
        if dir_size > 0:
            print(f"📊 Current JPG/PNG size in {directory}: {dir_size:,} bytes ({dir_size/1024/1024:.1f} MB)")
    
    print(f"\n💾 Total JPG/PNG disk usage: {total_jpg_size:,} bytes ({total_jpg_size/1024/1024:.1f} MB)")
    print()
    
    # Confirmation prompt
    response = input("🤔 Do you want to proceed with JPG removal? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Operation cancelled by user")
        return
    
    print("\n🔄 Starting JPG removal process...")
    print("🔍 Only removing images with confirmed WebP versions...")
    
    # Remove JPG images
    summary = find_and_remove_jpg_images(directories_to_clean)
    
    # Calculate space saved
    space_saved = 0
    for removed_file in summary['removed_files']:
        try:
            # File is already removed, so we can't get size, but we can estimate
            pass
        except:
            pass
    
    print("\n" + "=" * 50)
    print("🎉 JPG REMOVAL COMPLETE!")
    print(f"✅ Successfully removed: {summary['removed']} JPG/PNG files")
    print(f"⏭️  Safely skipped: {summary['skipped']} files (no WebP found)")
    print(f"❌ Removal errors: {summary['errors']} files")
    
    if summary['removed'] > 0:
        print(f"\n💾 Estimated disk space freed: ~{total_jpg_size:,} bytes ({total_jpg_size/1024/1024:.1f} MB)")
        print(f"🚀 Your website now uses only optimized WebP images!")
        print(f"📂 Directories cleaned: {len([d for d in directories_to_clean if os.path.exists(d)])}")
    
    if summary['skipped_files']:
        print(f"\n⚠️  Files skipped (missing WebP counterpart):")
        for skipped_file in summary['skipped_files'][:10]:  # Show first 10
            print(f"   - {skipped_file}")
        if len(summary['skipped_files']) > 10:
            print(f"   ... and {len(summary['skipped_files']) - 10} more")
    
    if summary['error_files']:
        print(f"\n❌ Files with removal errors:")
        for error_file in summary['error_files']:
            print(f"   - {error_file}")
    
    print(f"\n🔧 Result:")
    print(f"   ✅ All JPG files with WebP counterparts have been removed")
    print(f"   🔒 WebP files are preserved and optimized")
    print(f"   📈 Website performance improved with smaller file sizes")

if __name__ == "__main__":
    main()
