#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for fix_articles.py
This file has been consolidated into super_article_manager.py
"""

import sys
from super_article_manager import SuperArticleManager

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py enhance --fix-issues")
    
    manager = SuperArticleManager()
    manager.load_articles()
    manager.create_backup("fix")
    
    # Run fixes
    fixed = manager.fix_article_issues()
    
    if fixed > 0:
        manager.save_articles()
        print(f"✅ Fixed issues in {fixed} articles")
    else:
        print("ℹ️  No issues found to fix")

if __name__ == "__main__":
    main()
