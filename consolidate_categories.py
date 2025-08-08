#!/usr/bin/env python3
"""
Category Consolidation Script
Consolidates fragmented categories into clean, main categories.
"""

import json
import os
from collections import defaultdict

# Category mapping - consolidate similar categories
CATEGORY_MAPPING = {
    # Business consolidation
    'Business': 'Business',
    'Finance': 'Business', 
    'Economy': 'Business',
    'Business & Finance': 'Business',
    'Business & Economy': 'Business',
    'Business & International Relations': 'Business',
    'Business and Technology': 'Business',
    
    # Health consolidation
    'Health': 'Health',
    'Health & Wellness': 'Health',
    'Health & Safety': 'Health',
    
    # World/News consolidation
    'News': 'World',
    'World Affairs': 'World',
    'Defence': 'World',
    'Defense': 'World',
    
    # Lifestyle consolidation
    'Travel': 'Lifestyle',
    'Travel News': 'Lifestyle', 
    'Food & Drink': 'Lifestyle',
    'Career Development': 'Lifestyle',
    
    # Keep as-is
    'Sports': 'Sports',
    'Technology': 'Technology',
    'Entertainment': 'Entertainment',
    'Environment': 'Environment',
}

def consolidate_categories(articles_file: str = "perplexityArticles_eeat_enhanced.json"):
    """Consolidate article categories"""
    
    if not os.path.exists(articles_file):
        print(f"❌ {articles_file} not found!")
        return
    
    # Load articles
    with open(articles_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"📊 Processing {len(articles)} articles...")
    
    # Track changes
    category_changes = defaultdict(int)
    unchanged_count = 0
    
    # Process each article
    for article in articles:
        original_category = article.get('category', 'World')
        
        # Map to new category
        new_category = CATEGORY_MAPPING.get(original_category, 'World')
        
        if original_category != new_category:
            print(f"🔄 '{original_category}' → '{new_category}': {article.get('title', 'No title')[:50]}")
            article['category'] = new_category
            category_changes[f"{original_category} → {new_category}"] += 1
        else:
            unchanged_count += 1
    
    # Show summary
    print(f"\n📈 Category Consolidation Summary:")
    print(f"   Unchanged: {unchanged_count} articles")
    for change, count in category_changes.items():
        print(f"   {change}: {count} articles")
    
    # Show final category distribution
    final_categories = defaultdict(int)
    for article in articles:
        final_categories[article.get('category', 'World')] += 1
    
    print(f"\n✅ Final Category Distribution:")
    for category, count in sorted(final_categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   {category}: {count} articles")
    
    # Save updated articles
    backup_file = f"perplexityArticles_category_backup_{int(__import__('time').time())}.json"
    print(f"\n📁 Creating backup: {backup_file}")
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    with open(articles_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Updated {articles_file} with consolidated categories")
    print(f"🎉 Reduced from ~18 categories to {len(final_categories)} main categories")

if __name__ == "__main__":
    consolidate_categories()
