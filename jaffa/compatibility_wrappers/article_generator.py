#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for article_generator.py
This file has been consolidated into super_article_manager.py
"""

import sys
import asyncio
from super_article_manager import SuperArticleManager, generate_articles_from_trends, generate_articles_from_keywords

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py generate --help")
    
    # For basic compatibility, assume trends generation
    manager = SuperArticleManager()
    manager.load_articles()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_articles_from_trends(manager, 3))
    manager.save_articles()

if __name__ == "__main__":
    main()
