#!/usr/bin/env python3
"""
Article Duplicate Analysis Script
Analyzes perplexityArticles.json for duplicate articles based on multiple criteria.
"""

import json
import os
from collections import defaultdict

def analyze_duplicates(input_file='perplexityArticles.json'):
    """
    Comprehensive duplicate analysis of articles.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        
        print(f"📊 DUPLICATE ANALYSIS REPORT")
        print(f"{'='*50}")
        print(f"Total articles loaded: {len(articles_data)}")
        
        # Track duplicates
        duplicates_found = False
        duplicate_details = {
            'by_id': {},
            'by_title': {},
            'by_slug': {},
            'by_content': {}
        }
        
        # 1. Check for duplicate IDs
        print(f"\n🔍 Checking for duplicate IDs...")
        id_counts = defaultdict(list)
        for i, article in enumerate(articles_data):
            article_id = article.get('id')
            if article_id:
                id_counts[article_id].append((i, article.get('title', 'No title')))
        
        duplicate_ids = {id_val: articles for id_val, articles in id_counts.items() if len(articles) > 1}
        if duplicate_ids:
            print(f"❌ Found {len(duplicate_ids)} duplicate IDs:")
            for id_val, articles_list in duplicate_ids.items():
                print(f"  ID '{id_val}':")
                for idx, title in articles_list:
                    print(f"    - Article {idx}: '{title}'")
                duplicate_details['by_id'][id_val] = articles_list
            duplicates_found = True
        else:
            print(f"✅ No duplicate IDs found")
        
        # 2. Check for duplicate titles
        print(f"\n🔍 Checking for duplicate titles...")
        title_counts = defaultdict(list)
        for i, article in enumerate(articles_data):
            title = article.get('title', '').strip()
            if title:
                title_counts[title.lower()].append((i, title, article.get('id', 'No ID')))
        
        duplicate_titles = {title: articles for title, articles in title_counts.items() if len(articles) > 1}
        if duplicate_titles:
            print(f"❌ Found {len(duplicate_titles)} duplicate titles:")
            for title, articles_list in duplicate_titles.items():
                print(f"  Title '{title}':")
                for idx, orig_title, article_id in articles_list:
                    print(f"    - Article {idx} (ID: {article_id}): '{orig_title}'")
                duplicate_details['by_title'][title] = articles_list
            duplicates_found = True
        else:
            print(f"✅ No duplicate titles found")
        
        # 3. Check for duplicate slugs
        print(f"\n🔍 Checking for duplicate slugs...")
        slug_counts = defaultdict(list)
        for i, article in enumerate(articles_data):
            slug = article.get('slug', '').strip()
            if slug:
                slug_counts[slug].append((i, article.get('title', 'No title'), article.get('id', 'No ID')))
        
        duplicate_slugs = {slug: articles for slug, articles in slug_counts.items() if len(articles) > 1}
        if duplicate_slugs:
            print(f"❌ Found {len(duplicate_slugs)} duplicate slugs:")
            for slug, articles_list in duplicate_slugs.items():
                print(f"  Slug '{slug}':")
                for idx, title, article_id in articles_list:
                    print(f"    - Article {idx} (ID: {article_id}): '{title}'")
                duplicate_details['by_slug'][slug] = articles_list
            duplicates_found = True
        else:
            print(f"✅ No duplicate slugs found")
        
        # 4. Check for similar content (first 200 characters)
        print(f"\n🔍 Checking for similar content...")
        content_counts = defaultdict(list)
        for i, article in enumerate(articles_data):
            content = article.get('content', '').strip()
            if content:
                # Use first 200 characters as content fingerprint
                content_preview = content[:200].lower()
                content_counts[content_preview].append((i, article.get('title', 'No title'), article.get('id', 'No ID')))
        
        duplicate_content = {preview: articles for preview, articles in content_counts.items() if len(articles) > 1}
        if duplicate_content:
            print(f"❌ Found {len(duplicate_content)} groups with similar content:")
            for i, (preview, articles_list) in enumerate(duplicate_content.items()):
                print(f"  Content Group {i+1}:")
                for idx, title, article_id in articles_list:
                    print(f"    - Article {idx} (ID: {article_id}): '{title}'")
                duplicate_details['by_content'][preview] = articles_list
            duplicates_found = True
        else:
            print(f"✅ No similar content found")
        
        # 5. Summary
        print(f"\n📈 SUMMARY:")
        print(f"{'='*30}")
        print(f"Total articles: {len(articles_data)}")
        print(f"Unique IDs: {len(set(a.get('id') for a in articles_data if a.get('id')))}")
        print(f"Unique titles: {len(set(a.get('title', '').strip().lower() for a in articles_data if a.get('title')))}")
        print(f"Unique slugs: {len(set(a.get('slug', '').strip() for a in articles_data if a.get('slug')))}")
        
        if duplicates_found:
            print(f"\n❌ DUPLICATES DETECTED!")
            print(f"Duplicate IDs: {len(duplicate_details['by_id'])}")
            print(f"Duplicate titles: {len(duplicate_details['by_title'])}")
            print(f"Duplicate slugs: {len(duplicate_details['by_slug'])}")
            print(f"Similar content groups: {len(duplicate_details['by_content'])}")
            print(f"\n💡 Run deduplicate_articles.py to clean up duplicates.")
        else:
            print(f"\n✅ NO DUPLICATES FOUND! Your article data is clean.")
        
        return duplicates_found, duplicate_details
        
    except FileNotFoundError:
        print(f"❌ Error: {input_file} file not found!")
        return False, {}
    except json.JSONDecodeError as e:
        print(f"❌ Error: Could not decode JSON: {e}")
        return False, {}
    except Exception as e:
        print(f"❌ Error analyzing articles: {e}")
        return False, {}

if __name__ == "__main__":
    analyze_duplicates()
