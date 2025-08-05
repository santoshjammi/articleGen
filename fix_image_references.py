#!/usr/bin/env python3
"""
Image Reference Fixer for Country's News
Updates all .jpg/.png references to .webp in JSON files and other content
"""

import os
import json
import re
from pathlib import Path

def fix_json_file(file_path):
    """
    Fix image references in a JSON file from .jpg/.png to .webp
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: Summary of changes made
    """
    changes_made = 0
    
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count original references
        original_jpg_count = len(re.findall(r'\.jpg', content, re.IGNORECASE))
        original_png_count = len(re.findall(r'\.png', content, re.IGNORECASE))
        original_jpeg_count = len(re.findall(r'\.jpeg', content, re.IGNORECASE))
        
        # Replace .jpg with .webp
        content = re.sub(r'\.jpg', '.webp', content, flags=re.IGNORECASE)
        
        # Replace .png with .webp  
        content = re.sub(r'\.png', '.webp', content, flags=re.IGNORECASE)
        
        # Replace .jpeg with .webp
        content = re.sub(r'\.jpeg', '.webp', content, flags=re.IGNORECASE)
        
        # Write the updated content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        changes_made = original_jpg_count + original_png_count + original_jpeg_count
        
        return {
            'file': file_path,
            'changes': changes_made,
            'jpg_count': original_jpg_count,
            'png_count': original_png_count,
            'jpeg_count': original_jpeg_count
        }
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return {
            'file': file_path,
            'changes': 0,
            'error': str(e)
        }

def fix_python_files(file_path):
    """
    Fix image references in Python files from .jpg/.png to .webp
    """
    changes_made = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count original references
        original_jpg_count = len(re.findall(r'\.jpg', content, re.IGNORECASE))
        original_png_count = len(re.findall(r'\.png', content, re.IGNORECASE))
        original_jpeg_count = len(re.findall(r'\.jpeg', content, re.IGNORECASE))
        
        # Replace image extensions with webp
        content = re.sub(r'\.jpg', '.webp', content, flags=re.IGNORECASE)
        content = re.sub(r'\.png', '.webp', content, flags=re.IGNORECASE)
        content = re.sub(r'\.jpeg', '.webp', content, flags=re.IGNORECASE)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        changes_made = original_jpg_count + original_png_count + original_jpeg_count
        
        return {
            'file': file_path,
            'changes': changes_made,
            'jpg_count': original_jpg_count,
            'png_count': original_png_count,
            'jpeg_count': original_jpeg_count
        }
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return {
            'file': file_path,
            'changes': 0,
            'error': str(e)
        }

def find_and_fix_references():
    """
    Find and fix all image references in the project
    """
    
    # Files to process
    files_to_process = []
    
    # Add JSON files
    json_files = [
        'articles.json',
        'perplexityArticles.json'
    ]
    
    for json_file in json_files:
        if os.path.exists(json_file):
            files_to_process.append(('json', json_file))
    
    # Add Python files that might contain image references
    python_files = [
        'generateSite.py',
        'super_article_manager.py',
        'generateImage.py'
    ]
    
    for py_file in python_files:
        if os.path.exists(py_file):
            files_to_process.append(('python', py_file))
    
    # Find all perplexity operation files
    for file in os.listdir('.'):
        if file.startswith('perplexityArticles_operation_') and file.endswith('.json'):
            files_to_process.append(('json', file))
    
    return files_to_process

def main():
    print("🔧 Country's News Image Reference Fixer")
    print("=" * 50)
    print("🎯 Converting all .jpg/.png references to .webp")
    print("📁 Processing JSON files and Python scripts...")
    print()
    
    # Find files to process
    files_to_process = find_and_fix_references()
    
    if not files_to_process:
        print("❌ No files found to process")
        return
    
    print(f"📊 Found {len(files_to_process)} files to process:")
    for file_type, file_path in files_to_process:
        print(f"   - {file_path} ({file_type})")
    
    print()
    
    # Process files
    total_changes = 0
    successful_files = 0
    failed_files = 0
    
    for file_type, file_path in files_to_process:
        print(f"🔄 Processing: {file_path}")
        
        if file_type == 'json':
            result = fix_json_file(file_path)
        elif file_type == 'python':
            result = fix_python_files(file_path)
        
        if 'error' in result:
            print(f"   ❌ Failed: {result['error']}")
            failed_files += 1
        else:
            changes = result['changes']
            if changes > 0:
                print(f"   ✅ Fixed {changes} references (.jpg: {result.get('jpg_count', 0)}, .png: {result.get('png_count', 0)}, .jpeg: {result.get('jpeg_count', 0)})")
                total_changes += changes
                successful_files += 1
            else:
                print(f"   ⏭️  No changes needed")
                successful_files += 1
    
    print("\n" + "=" * 50)
    print("🎉 IMAGE REFERENCE UPDATE COMPLETE!")
    print(f"✅ Successfully processed: {successful_files} files")
    print(f"❌ Failed to process: {failed_files} files")
    print(f"🔧 Total references updated: {total_changes}")
    
    if total_changes > 0:
        print(f"\n🚀 All image references now point to WebP files!")
        print(f"📈 Your website should now display all images correctly")
        print(f"🔍 Thumbnails and inline images should work properly")
    
    print(f"\n🔧 Next steps:")
    print(f"   1. Test your website to ensure all images load correctly")
    print(f"   2. Check thumbnails and inline images in articles")
    print(f"   3. Regenerate your site if needed: python generateSite.py")

if __name__ == "__main__":
    main()
