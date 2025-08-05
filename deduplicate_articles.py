#!/usr/bin/env python3
"""
Article Deduplication Script
Removes duplicate articles from perplexityArticles.json based on multiple criteria.
Prioritizes keeping the article with more complete data.
"""

import json
import os
from datetime import datetime
from collections import defaultdict

def generate_slug(title):
    """Generate a URL-friendly slug from title."""
    import re
    if not title:
        return ""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug.strip('-')

def calculate_article_score(article):
    """
    Calculate a quality score for an article to determine which one to keep.
    Higher score = better article to keep.
    """
    score = 0
    
    # Content length (more content is generally better)
    content = article.get('content', '')
    score += min(len(content) / 100, 50)  # Max 50 points for content
    
    # Presence of important fields
    if article.get('title'): score += 10
    if article.get('excerpt'): score += 5
    if article.get('category'): score += 5
    if article.get('tags'): score += 3
    if article.get('datePublished'): score += 3
    if article.get('author'): score += 2
    if article.get('ogImage'): score += 2
    if article.get('thumbnailImageUrl'): score += 2
    if article.get('metaDescription'): score += 2
    
    # Penalize articles with missing essential fields
    if not article.get('slug'): score -= 20
    if not article.get('id'): score -= 15
    
    return score

def deduplicate_articles(input_file='perplexityArticles.json', output_file=None, create_backup=True):
    """
    Remove duplicate articles from the JSON file based on multiple criteria.
    Keeps the article with the highest quality score for each duplicate group.
    """
    
    if output_file is None:
        output_file = input_file
    
    try:
        # Load articles
        with open(input_file, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        
        print(f"🔄 ARTICLE DEDUPLICATION PROCESS")
        print(f"{'='*50}")
        print(f"Loaded {len(articles_data)} articles from {input_file}")
        
        # Create backup if requested
        if create_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"perplexityArticles_backup_{timestamp}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(articles_data, f, ensure_ascii=False, indent=2)
            print(f"📁 Backup created: {backup_file}")
        
        # Group articles by potential duplicate criteria
        groups_by_id = defaultdict(list)
        groups_by_title = defaultdict(list)
        groups_by_slug = defaultdict(list)
        groups_by_content = defaultdict(list)
        
        # First, add all articles to groups
        for i, article in enumerate(articles_data):
            article['_original_index'] = i  # Track original position
            
            # Group by ID
            article_id = article.get('id')
            if article_id:
                groups_by_id[article_id].append(article)
            
            # Group by title (case-insensitive)
            title = article.get('title', '').strip()
            if title:
                groups_by_title[title.lower()].append(article)
            
            # Group by slug
            slug = article.get('slug', '').strip()
            if slug:
                groups_by_slug[slug].append(article)
            
            # Group by content preview (first 200 chars)
            content = article.get('content', '').strip()
            if content:
                content_preview = content[:200].lower()
                groups_by_content[content_preview].append(article)
        
        # Collect all duplicate groups
        all_duplicate_groups = []
        processed_indices = set()
        
        # Process ID duplicates
        for article_id, group in groups_by_id.items():
            if len(group) > 1:
                indices = [a['_original_index'] for a in group]
                if not any(idx in processed_indices for idx in indices):
                    all_duplicate_groups.append(('ID', article_id, group))
                    processed_indices.update(indices)
        
        # Process title duplicates (skip if already processed)
        for title, group in groups_by_title.items():
            if len(group) > 1:
                indices = [a['_original_index'] for a in group]
                if not any(idx in processed_indices for idx in indices):
                    all_duplicate_groups.append(('Title', title, group))
                    processed_indices.update(indices)
        
        # Process slug duplicates (skip if already processed)
        for slug, group in groups_by_slug.items():
            if len(group) > 1:
                indices = [a['_original_index'] for a in group]
                if not any(idx in processed_indices for idx in indices):
                    all_duplicate_groups.append(('Slug', slug, group))
                    processed_indices.update(indices)
        
        # Process content duplicates (skip if already processed)
        for content_preview, group in groups_by_content.items():
            if len(group) > 1:
                indices = [a['_original_index'] for a in group]
                if not any(idx in processed_indices for idx in indices):
                    all_duplicate_groups.append(('Content', content_preview[:50] + '...', group))
                    processed_indices.update(indices)
        
        # Deduplicate each group
        articles_to_keep = []
        articles_to_remove = []
        
        print(f"\n🔍 Found {len(all_duplicate_groups)} duplicate groups:")
        
        for duplicate_type, identifier, group in all_duplicate_groups:
            print(f"\n📍 {duplicate_type} duplicate: '{identifier}'")
            print(f"   Articles in group: {len(group)}")
            
            # Calculate scores for each article in the group
            scored_articles = []
            for article in group:
                score = calculate_article_score(article)
                scored_articles.append((score, article))
                print(f"   - Article {article['_original_index']}: '{article.get('title', 'No title')}' (Score: {score:.1f})")
            
            # Sort by score (highest first) and keep the best one
            scored_articles.sort(key=lambda x: x[0], reverse=True)
            best_article = scored_articles[0][1]
            articles_to_keep.append(best_article)
            
            # Mark others for removal
            for score, article in scored_articles[1:]:
                articles_to_remove.append(article)
            
            print(f"   ✅ Keeping: Article {best_article['_original_index']} (Score: {scored_articles[0][0]:.1f})")
            print(f"   ❌ Removing: {len(scored_articles) - 1} duplicates")
        
        # Create final list of unique articles
        remove_indices = set(article['_original_index'] for article in articles_to_remove)
        unique_articles = []
        
        for i, article in enumerate(articles_data):
            if i not in remove_indices:
                # Clean up temporary field
                if '_original_index' in article:
                    del article['_original_index']
                
                # Fix missing slugs
                if not article.get('slug') and article.get('title'):
                    article['slug'] = generate_slug(article['title'])
                    print(f"🔧 Generated missing slug for: '{article['title']}'")
                
                unique_articles.append(article)
        
        # Save deduplicated articles
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_articles, f, ensure_ascii=False, indent=2)
        
        # Final summary
        duplicates_removed = len(articles_data) - len(unique_articles)
        print(f"\n✅ DEDUPLICATION COMPLETE!")
        print(f"{'='*30}")
        print(f"Original articles: {len(articles_data)}")
        print(f"Unique articles: {len(unique_articles)}")
        print(f"Duplicates removed: {duplicates_removed}")
        print(f"Duplicate groups processed: {len(all_duplicate_groups)}")
        
        if create_backup:
            print(f"\n📁 Files:")
            print(f"  - Original backed up to: {backup_file}")
            print(f"  - Clean articles saved to: {output_file}")
        
        print(f"\n🚀 Next steps:")
        print(f"  1. Review the cleaned data")
        print(f"  2. Run: python generateSite.py")
        print(f"  3. Test the generated website")
        
        return duplicates_removed
        
    except FileNotFoundError:
        print(f"❌ Error: {input_file} file not found!")
        return 0
    except json.JSONDecodeError as e:
        print(f"❌ Error: Could not decode JSON: {e}")
        return 0
    except Exception as e:
        print(f"❌ Error during deduplication: {e}")
        return 0

if __name__ == "__main__":
    # Run deduplication
    removed_count = deduplicate_articles()
    
    if removed_count > 0:
        print(f"\n🎉 Successfully removed {removed_count} duplicate articles!")
        print(f"💡 Your articles are now ready for site generation.")
    else:
        print(f"\n✅ No duplicates found or removed.")
