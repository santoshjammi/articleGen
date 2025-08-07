#!/usr/bin/env python3
"""
Migration Script for Consolidated Article Generation System
Helps migrate from old article generation files to the new consolidated system.
"""

import os
import json
import shutil
from datetime import datetime
from typing import Dict, List

# Old files to be replaced
OLD_FILES = [
    "generateArticles.py",
    "keywordBasedArticleGen.py", 
    "perplexitySEOArticleGen.py",
    "quickKeywordGen.py",
    "batchKeywordGen.py"
]

# Data files to migrate
OLD_ARTICLES_FILE = "articles.json"
NEW_ARTICLES_FILE = "perplexityArticles.json"

def backup_old_files():
    """Create backup of old files"""
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    print(f"📦 Creating backup in {backup_dir}/")
    
    backed_up = []
    for file in OLD_FILES:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            backed_up.append(file)
            print(f"   ✅ Backed up {file}")
    
    # Backup data files
    for data_file in [OLD_ARTICLES_FILE, NEW_ARTICLES_FILE]:
        if os.path.exists(data_file):
            shutil.copy2(data_file, os.path.join(backup_dir, data_file))
            backed_up.append(data_file)
            print(f"   ✅ Backed up {data_file}")
    
    return backup_dir, backed_up

def migrate_articles_data():
    """Migrate articles from old format to new format"""
    print("\n📊 Migrating articles data...")
    
    # Load existing articles from both files
    old_articles = []
    new_articles = []
    
    if os.path.exists(OLD_ARTICLES_FILE):
        try:
            with open(OLD_ARTICLES_FILE, 'r', encoding='utf-8') as f:
                old_articles = json.load(f)
            print(f"   📖 Loaded {len(old_articles)} articles from {OLD_ARTICLES_FILE}")
        except Exception as e:
            print(f"   ❌ Error loading {OLD_ARTICLES_FILE}: {e}")
    
    if os.path.exists(NEW_ARTICLES_FILE):
        try:
            with open(NEW_ARTICLES_FILE, 'r', encoding='utf-8') as f:
                new_articles = json.load(f)
            print(f"   📖 Loaded {len(new_articles)} articles from {NEW_ARTICLES_FILE}")
        except Exception as e:
            print(f"   ❌ Error loading {NEW_ARTICLES_FILE}: {e}")
    
    # Merge articles, avoiding duplicates
    merged_articles = {}
    
    # Add new articles first (they're likely more complete)
    for article in new_articles:
        slug = article.get('slug')
        if slug:
            merged_articles[slug] = article
    
    # Add old articles, but don't overwrite newer ones
    for article in old_articles:
        slug = article.get('slug')
        if slug and slug not in merged_articles:
            # Ensure old articles have the new required fields
            article = normalize_article_structure(article)
            merged_articles[slug] = article
    
    final_articles = list(merged_articles.values())
    
    # Save merged articles
    try:
        with open(NEW_ARTICLES_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_articles, f, indent=4, ensure_ascii=False)
        print(f"   ✅ Saved {len(final_articles)} merged articles to {NEW_ARTICLES_FILE}")
        return True
    except Exception as e:
        print(f"   ❌ Error saving merged articles: {e}")
        return False

def normalize_article_structure(article: Dict) -> Dict:
    """Normalize old article structure to new format"""
    # Default values for missing fields
    defaults = {
        "generationMethod": "legacy",
        "region": "India",
        "sourceKeyword": None,
        "relatedTopics": [],
        "keyTakeaways": [],
        "socialMediaHashtags": [], 
        "callToActionText": "",
        "structuredData": "",
        "inlineImages": [],
        "thumbnailImageUrl": "",
        "adDensity": "medium",
        "sponsorName": None,
        "isSponsoredContent": False,
        "factCheckedBy": "AI Content Review",
        "editorReviewedBy": "AI Editor",
        "viewsCount": 0,
        "sharesCount": 0,
        "commentsCount": 0,
        "averageRating": 0.0,
        "language": "en-IN",
        "schemaType": "NewsArticle"
    }
    
    # Add missing fields
    for key, value in defaults.items():
        if key not in article:
            article[key] = value
    
    # Ensure lists are actually lists
    list_fields = ["keywords", "tags", "targetAudience", "adPlacementKeywords", 
                   "relatedTopics", "keyTakeaways", "socialMediaHashtags", "inlineImages"]
    for field in list_fields:
        if field in article and not isinstance(article[field], list):
            article[field] = []
    
    return article

def create_wrapper_scripts():
    """Create wrapper scripts for backward compatibility"""
    print("\n🔧 Creating backward compatibility wrappers...")
    
    wrappers = {
        "generateArticles.py": '''#!/usr/bin/env python3
"""
Legacy wrapper for generateArticles.py
Redirects to the new consolidated article_generator.py
"""
import subprocess
import sys

print("⚠️  This script has been replaced by article_generator.py")
print("🔄 Redirecting to: python article_generator.py trends --count 3")
print()

subprocess.run([sys.executable, "article_generator.py", "trends", "--count", "3"] + sys.argv[1:])
''',
        
        "quickKeywordGen.py": '''#!/usr/bin/env python3
"""
Legacy wrapper for quickKeywordGen.py
Redirects to the new consolidated article_generator.py
"""
import subprocess
import sys

print("⚠️  This script has been replaced by article_generator.py")
print("🔄 Redirecting to: python article_generator.py keywords")
print()

if len(sys.argv) > 1:
    subprocess.run([sys.executable, "article_generator.py", "keywords"] + sys.argv[1:])
else:
    subprocess.run([sys.executable, "article_generator.py", "interactive"])
''',
        
        "batchKeywordGen.py": '''#!/usr/bin/env python3
"""
Legacy wrapper for batchKeywordGen.py
Redirects to the new consolidated article_generator.py
"""
import subprocess
import sys

print("⚠️  This script has been replaced by article_generator.py")
print("🔄 Redirecting to: python article_generator.py batch")
print()

subprocess.run([sys.executable, "article_generator.py", "batch"] + sys.argv[1:])
''',
        
        "keywordBasedArticleGen.py": '''#!/usr/bin/env python3
"""
Legacy wrapper for keywordBasedArticleGen.py
Redirects to the new consolidated article_generator.py
"""
import subprocess
import sys

print("⚠️  This script has been replaced by article_generator.py")
print("🔄 Use: python article_generator.py keywords [keywords...]")
print("    or: python article_generator.py interactive")
print()

# Note: This was primarily used as a module, so we just show help
subprocess.run([sys.executable, "article_generator.py", "--help"])
''',
        
        "perplexitySEOArticleGen.py": '''#!/usr/bin/env python3
"""
Legacy wrapper for perplexitySEOArticleGen.py
Redirects to the new consolidated article_generator.py
"""
import subprocess
import sys

print("⚠️  This script has been replaced by article_generator.py")
print("🔄 Redirecting to: python article_generator.py trends")
print()

subprocess.run([sys.executable, "article_generator.py", "trends"] + sys.argv[1:])
'''
    }
    
    for filename, content in wrappers.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        os.chmod(filename, 0o755)  # Make executable
        print(f"   ✅ Created wrapper: {filename}")

def create_migration_summary():
    """Create a summary of the migration"""
    summary = f"""
# Article Generation System Migration Summary

Migration completed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## What Changed

### Old System (Multiple Files)
- `generateArticles.py` - Legacy trend-based generation
- `keywordBasedArticleGen.py` - Keyword-based generation core
- `perplexitySEOArticleGen.py` - Advanced trend-based generation  
- `quickKeywordGen.py` - Interactive/command-line interface
- `batchKeywordGen.py` - Batch processing

### New System (Single File)
- `article_generator.py` - **Consolidated system with all functionality**

## New Usage

### Basic Commands
```bash
# Generate from trending keywords (replaces perplexitySEOArticleGen.py)
python article_generator.py trends --count 5

# Generate from specific keywords (replaces quickKeywordGen.py)
python article_generator.py keywords "AI technology" "machine learning"

# Interactive mode (replaces quickKeywordGen.py --interactive) 
python article_generator.py interactive

# Batch processing (replaces batchKeywordGen.py)
python article_generator.py batch technology health business

# Show statistics
python article_generator.py stats
```

### Advanced Options
```bash
# Custom region and prompts
python article_generator.py keywords --region "USA" --prompt "Focus on business" "startup funding"

# Force regeneration (skip duplicate check)
python article_generator.py keywords --no-skip "existing keyword"

# Use different articles file
python article_generator.py trends --file "my_articles.json"
```

## Benefits

1. **Single Entry Point** - One script handles all generation methods
2. **Consistent Interface** - Unified command-line interface
3. **Better Error Handling** - Improved error messages and recovery
4. **Enhanced Features** - All best features from each old script combined
5. **Easier Maintenance** - One codebase instead of five separate files

## Backward Compatibility

- All old script names still work (they redirect to the new system)
- Existing workflows continue to function
- Data files are automatically migrated and merged

## Migration Notes

- Your old files have been backed up for safety
- Article data has been merged from all sources
- Configuration files (`keyword_config.json`) work unchanged
- All image generation and processing remains the same

## Next Steps

1. Test the new system: `python article_generator.py --help`
2. Try generating some articles: `python article_generator.py interactive`
3. Check your data: `python article_generator.py stats`
4. Update any automation scripts to use the new commands
5. Remove old wrapper files when you're confident everything works

For questions or issues, check the consolidated code in `article_generator.py`.
"""
    
    with open("MIGRATION_SUMMARY.md", 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"   ✅ Created MIGRATION_SUMMARY.md")

def main():
    """Main migration function"""
    print("🚀 Article Generation System Migration")
    print("=" * 50)
    print()
    
    # Step 1: Backup old files
    backup_dir, backed_up = backup_old_files()
    
    if not backed_up:
        print("ℹ️  No files to backup - this looks like a fresh installation")
    else:
        print(f"✅ Backed up {len(backed_up)} files to {backup_dir}/")
    
    # Step 2: Migrate article data
    if migrate_articles_data():
        print("✅ Article data migration completed")
    else:
        print("⚠️  Article data migration had issues - check manually")
    
    # Step 3: Create wrapper scripts for backward compatibility
    create_wrapper_scripts()
    
    # Step 4: Create migration summary
    create_migration_summary()
    
    print("\n🎉 Migration Complete!")
    print("=" * 50)
    print()
    print("Next steps:")
    print("1. Test the new system: python article_generator.py --help")
    print("2. Try interactive mode: python article_generator.py interactive") 
    print("3. Check your stats: python article_generator.py stats")
    print("4. Read MIGRATION_SUMMARY.md for full details")
    print()
    print("Your old files are safely backed up in:", backup_dir)

if __name__ == "__main__":
    main()
