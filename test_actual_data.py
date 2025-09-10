#!/usr/bin/env python3
"""
Test the enhanced categorization on actual article data
"""

import json
import sys
import os
from collections import defaultdict

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced functions
from super_article_manager import normalize_category_enhanced, categorize_by_subcategory

def test_on_actual_data():
    """Test enhanced categorization on actual article data"""
    
    print("🔍 Testing Enhanced Categorization on Actual Data")
    print("=" * 60)
    
    # Load articles
    filename = 'perplexityArticles_eeat_enhanced.json'
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print(f"✅ Loaded {len(articles)} articles")
    except Exception as e:
        print(f"❌ Error loading articles: {e}")
        return
    
    # Track changes
    changes = []
    category_stats = defaultdict(int)
    subcategory_stats = defaultdict(int)
    
    print("\n🔄 Processing articles...")
    
    for i, article in enumerate(articles[:50]):  # Test first 50 articles
        original_category = article.get('category', 'World')
        subcategory = article.get('subCategory', '')
        
        # Apply enhanced categorization
        new_category = normalize_category_enhanced(original_category, subcategory)
        
        category_stats[original_category] += 1
        if subcategory:
            subcategory_stats[subcategory] += 1
        
        if new_category != original_category:
            changes.append({
                'id': article.get('id'),
                'title': article.get('title', 'No title')[:50] + '...',
                'subcategory': subcategory,
                'old_category': original_category,
                'new_category': new_category
            })
    
    print(f"\n📊 RESULTS FOR FIRST 50 ARTICLES:")
    print(f"   Articles processed: 50")
    print(f"   Categorization changes: {len(changes)}")
    
    if changes:
        print(f"\n🔄 CATEGORY CHANGES DETECTED:")
        for change in changes:
            print(f"   ID {change['id']}: {change['old_category']} → {change['new_category']}")
            print(f"      SubCategory: {change['subcategory']}")
            print(f"      Title: {change['title']}")
            print()
    else:
        print(f"\n✅ No categorization changes needed for first 50 articles!")
    
    print(f"\n📈 CATEGORY DISTRIBUTION (First 50):")
    for category, count in sorted(category_stats.items()):
        print(f"   {category}: {count}")
    
    print(f"\n🏷️  SUBCATEGORY DISTRIBUTION (Top 10):")
    top_subcategories = sorted(subcategory_stats.items(), key=lambda x: x[1], reverse=True)[:10]
    for subcategory, count in top_subcategories:
        print(f"   {subcategory}: {count}")

if __name__ == "__main__":
    test_on_actual_data()
