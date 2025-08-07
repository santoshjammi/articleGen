#!/usr/bin/env python3
"""
Fix date formats in perplexityArticles.json
Removes invalid 'Z' suffix from dates
"""

import json
from datetime import datetime
import os

def main():
    print("🔧 Fixing date formats in articles...")
    
    # Load articles
    with open('perplexityArticles.json', 'r') as f:
        articles = json.load(f)
    
    # Create backup
    backup_filename = f'perplexityArticles_datefix_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(backup_filename, 'w') as f:
        json.dump(articles, f, indent=2)
    print(f"📁 Backup created: {backup_filename}")
    
    # Fix date formats
    fixed_count = 0
    for i, article in enumerate(articles):
        # Fix dateModified
        if 'dateModified' in article and article['dateModified'].endswith('Z'):
            old_date = article['dateModified']
            article['dateModified'] = article['dateModified'][:-1]  # Remove 'Z'
            print(f"Fixed article {i+1} dateModified: {old_date} -> {article['dateModified']}")
            fixed_count += 1
        
        # Ensure publishDate doesn't have 'Z'
        if 'publishDate' in article and article['publishDate'].endswith('Z'):
            old_date = article['publishDate']
            article['publishDate'] = article['publishDate'][:-1]  # Remove 'Z'
            print(f"Fixed article {i+1} publishDate: {old_date} -> {article['publishDate']}")
            fixed_count += 1
    
    # Save fixed articles
    with open('perplexityArticles.json', 'w') as f:
        json.dump(articles, f, indent=2)
    
    print(f"✅ Fixed {fixed_count} date format issues")
    print(f"✅ Updated perplexityArticles.json")
    print(f"📊 Total articles processed: {len(articles)}")

if __name__ == "__main__":
    main()
