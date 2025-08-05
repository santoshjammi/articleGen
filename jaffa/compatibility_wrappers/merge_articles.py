#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for merge_articles.py
This file has been consolidated into super_article_manager.py
"""

import sys
from super_article_manager import SuperArticleManager

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py enhance --merge-legacy")
    
    manager = SuperArticleManager()
    manager.load_articles()
    manager.create_backup("merge")
    
    # Run merge
    merged = manager.merge_legacy_articles()
    
    if merged > 0:
        manager.save_articles()
        print(f"✅ Merged {merged} legacy articles")
    else:
        print("ℹ️  No legacy articles to merge")

if __name__ == "__main__":
    main()
