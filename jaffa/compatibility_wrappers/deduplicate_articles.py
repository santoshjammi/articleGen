#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for deduplicate_articles.py
This file has been consolidated into super_article_manager.py
"""

import sys
from super_article_manager import SuperArticleManager

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py enhance --deduplicate")
    
    manager = SuperArticleManager()
    manager.load_articles()
    manager.create_backup("dedupe")
    
    # Run deduplication
    duplicates = manager.analyze_duplicates()
    removed = manager.deduplicate_articles(duplicates)
    
    if removed > 0:
        manager.save_articles()
        print(f"✅ Removed {removed} duplicate articles")
    else:
        print("ℹ️  No duplicates found")

if __name__ == "__main__":
    main()
