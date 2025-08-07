#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for enhance_articles.py
This file has been consolidated into super_article_manager.py
"""

import sys
from super_article_manager import SuperArticleManager

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py enhance --all")
    
    manager = SuperArticleManager()
    manager.load_articles()
    manager.create_backup("enhance")
    
    # Run enhancement
    enhanced = manager.enhance_articles()
    if enhanced > 0:
        manager.save_articles()
        print(f"✅ Enhanced {enhanced} articles")
    else:
        print("ℹ️  No articles needed enhancement")

if __name__ == "__main__":
    main()
