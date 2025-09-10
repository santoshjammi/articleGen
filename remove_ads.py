#!/usr/bin/env python3
"""
Script to remove all ad-related fields from existing articles
"""
import json
import os
import shutil
from datetime import datetime

def remove_ad_fields_from_articles():
    """Remove ad-related fields from all articles in articles.json"""
    articles_file = "articles.json"
    
    if not os.path.exists(articles_file):
        print(f"❌ {articles_file} not found")
        return
    
    # Create backup
    backup_file = f"articles_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    shutil.copy(articles_file, backup_file)
    print(f"✅ Created backup: {backup_file}")
    
    try:
        with open(articles_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading {articles_file}: {e}")
        return
    
    if not isinstance(data, list):
        print(f"❌ Expected array in {articles_file}, got {type(data)}")
        return
    
    articles_processed = 0
    fields_removed = 0
    
    # Fields to remove
    ad_fields = [
        'adPlacementKeywords',
        'adDensity',
        'sponsorName', 
        'isSponsoredContent'
    ]
    
    for article in data:
        if not isinstance(article, dict):
            continue
            
        article_modified = False
        for field in ad_fields:
            if field in article:
                del article[field]
                fields_removed += 1
                article_modified = True
        
        if article_modified:
            articles_processed += 1
    
    # Write cleaned data back
    try:
        with open(articles_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Successfully cleaned {articles_file}")
        print(f"   - Processed {articles_processed} articles")
        print(f"   - Removed {fields_removed} ad-related fields")
        print(f"   - Backup saved as {backup_file}")
    except Exception as e:
        print(f"❌ Error writing cleaned data: {e}")
        # Restore backup
        shutil.copy(backup_file, articles_file)
        print(f"🔄 Restored from backup")

def remove_ad_fields_from_generated_files():
    """Remove ad-related fields from generated article files in output directories"""
    
    # Check for output directories
    output_dirs = ['output', 'dist', 'generated_articles']
    found_dirs = []
    
    for dir_name in output_dirs:
        if os.path.exists(dir_name):
            found_dirs.append(dir_name)
    
    if not found_dirs:
        print("ℹ️  No output directories found to clean")
        return
    
    total_files_processed = 0
    
    for output_dir in found_dirs:
        print(f"\n🔍 Cleaning files in {output_dir}/...")
        files_in_dir = 0
        
        # Walk through all subdirectories
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    if clean_json_file(file_path):
                        files_in_dir += 1
                        total_files_processed += 1
        
        print(f"   ✅ Cleaned {files_in_dir} JSON files in {output_dir}/")
    
    print(f"\n✅ Total files processed: {total_files_processed}")

def clean_json_file(file_path):
    """Clean a single JSON file of ad-related fields"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Fields to remove
        ad_fields = [
            'adPlacementKeywords',
            'adDensity', 
            'sponsorName',
            'isSponsoredContent'
        ]
        
        modified = False
        
        # Handle both single articles and arrays of articles
        if isinstance(data, dict):
            for field in ad_fields:
                if field in data:
                    del data[field]
                    modified = True
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    for field in ad_fields:
                        if field in item:
                            del item[field]
                            modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️  Error cleaning {file_path}: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Starting ad removal process...\n")
    
    # Clean main articles.json
    remove_ad_fields_from_articles()
    
    # Clean generated files
    remove_ad_fields_from_generated_files()
    
    print("\n🎉 Ad removal process completed!")
