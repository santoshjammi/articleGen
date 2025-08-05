#!/usr/bin/env python3
"""
Article Enhancement Script
Enhances article metadata, fixes missing fields, and optimizes content for better SEO.
"""

import json
import os
import re
from datetime import datetime

def generate_slug(title):
    """Generate a URL-friendly slug from title."""
    if not title:
        return ""
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug.strip('-')

def calculate_reading_time(content):
    """Calculate estimated reading time in minutes (average 200 words per minute)."""
    if not content:
        return 1
    word_count = len(content.split())
    reading_time = max(1, round(word_count / 200))
    return reading_time

def generate_excerpt(content, max_length=160):
    """Generate an excerpt from content, optimized for meta descriptions."""
    if not content:
        return ""
    
    # Remove HTML tags if any
    clean_content = re.sub(r'<[^>]+>', '', content)
    
    # Take first paragraph or sentence
    sentences = clean_content.split('. ')
    excerpt = sentences[0]
    
    # If first sentence is too short, add more
    if len(excerpt) < 80 and len(sentences) > 1:
        excerpt += '. ' + sentences[1]
    
    # Ensure it's not too long
    if len(excerpt) > max_length:
        excerpt = excerpt[:max_length-3] + '...'
    
    return excerpt.strip()

def validate_and_enhance_articles(input_file='perplexityArticles.json', output_file=None, create_backup=True):
    """
    Validate and enhance article metadata for better SEO and functionality.
    """
    
    if output_file is None:
        output_file = input_file
    
    try:
        # Load articles
        with open(input_file, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        
        print(f"🔧 ARTICLE ENHANCEMENT PROCESS")
        print(f"{'='*50}")
        print(f"Loaded {len(articles_data)} articles from {input_file}")
        
        # Create backup if requested
        if create_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"perplexityArticles_pre_enhancement_{timestamp}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(articles_data, f, ensure_ascii=False, indent=2)
            print(f"📁 Backup created: {backup_file}")
        
        # Enhancement statistics
        stats = {
            'slugs_generated': 0,
            'excerpts_generated': 0,
            'meta_descriptions_added': 0,
            'reading_times_calculated': 0,
            'word_counts_calculated': 0,
            'categories_fixed': 0,
            'dates_formatted': 0,
            'missing_ids_fixed': 0
        }
        
        print(f"\n🔍 Analyzing and enhancing articles...")
        
        for i, article in enumerate(articles_data):
            enhanced = False
            
            # 1. Ensure article has an ID
            if not article.get('id'):
                article['id'] = f"article_{i+1}"
                stats['missing_ids_fixed'] += 1
                enhanced = True
                print(f"   ✅ Added missing ID for article {i+1}: '{article.get('title', 'No title')}'")
            
            # 2. Generate missing slug
            if not article.get('slug') and article.get('title'):
                article['slug'] = generate_slug(article['title'])
                stats['slugs_generated'] += 1
                enhanced = True
                print(f"   🔗 Generated slug for: '{article['title']}'")
            
            # 3. Calculate word count
            content = article.get('content', '')
            if content:
                word_count = len(content.split())
                if not article.get('wordCount') or article.get('wordCount') != word_count:
                    article['wordCount'] = word_count
                    stats['word_counts_calculated'] += 1
                    enhanced = True
            
            # 4. Calculate reading time
            if not article.get('readingTimeMinutes') or not isinstance(article.get('readingTimeMinutes'), int):
                reading_time = calculate_reading_time(content)
                article['readingTimeMinutes'] = reading_time
                stats['reading_times_calculated'] += 1
                enhanced = True
            
            # 5. Generate excerpt if missing
            if not article.get('excerpt') and content:
                excerpt = generate_excerpt(content, 160)
                if excerpt:
                    article['excerpt'] = excerpt
                    stats['excerpts_generated'] += 1
                    enhanced = True
                    print(f"   📝 Generated excerpt for: '{article.get('title', 'No title')}'")
            
            # 6. Add meta description
            if not article.get('metaDescription'):
                if article.get('excerpt'):
                    meta_desc = article['excerpt']
                elif content:
                    meta_desc = generate_excerpt(content, 155)
                else:
                    meta_desc = article.get('title', '')
                
                if meta_desc:
                    article['metaDescription'] = meta_desc
                    stats['meta_descriptions_added'] += 1
                    enhanced = True
            
            # 7. Ensure proper category
            if not article.get('category') or article['category'].strip() == "":
                article['category'] = "News"  # Default category
                stats['categories_fixed'] += 1
                enhanced = True
            
            # 8. Format dates consistently
            for date_field in ['datePublished', 'dateModified']:
                if article.get(date_field):
                    date_str = article[date_field]
                    # Ensure date is in ISO format
                    if not re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', date_str):
                        try:
                            # Try to parse and reformat
                            if 'T' not in date_str and ' ' in date_str:
                                date_str = date_str.replace(' ', 'T')
                            if not date_str.endswith('Z') and '+' not in date_str:
                                date_str += 'Z'
                            article[date_field] = date_str
                            stats['dates_formatted'] += 1
                            enhanced = True
                        except:
                            pass  # Keep original if can't parse
            
            # 9. Ensure tags is a list
            if article.get('tags') and isinstance(article['tags'], str):
                article['tags'] = [tag.strip() for tag in article['tags'].split(',')]
                enhanced = True
        
        # Save enhanced articles
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles_data, f, ensure_ascii=False, indent=2)
        
        # Summary
        print(f"\n✅ ENHANCEMENT COMPLETE!")
        print(f"{'='*30}")
        print(f"Total articles processed: {len(articles_data)}")
        print(f"\nEnhancements made:")
        for enhancement, count in stats.items():
            if count > 0:
                print(f"  - {enhancement.replace('_', ' ').title()}: {count}")
        
        total_enhancements = sum(stats.values())
        if total_enhancements > 0:
            print(f"\nTotal enhancements: {total_enhancements}")
            if create_backup:
                print(f"\n📁 Files:")
                print(f"  - Original backed up to: {backup_file}")
                print(f"  - Enhanced articles saved to: {output_file}")
        else:
            print(f"\n✅ All articles were already properly formatted!")
        
        print(f"\n🚀 Next steps:")
        print(f"  1. Run: python generateSite.py")
        print(f"  2. Test the generated website")
        print(f"  3. Deploy to hosting")
        
        return total_enhancements
        
    except FileNotFoundError:
        print(f"❌ Error: {input_file} file not found!")
        return 0
    except json.JSONDecodeError as e:
        print(f"❌ Error: Could not decode JSON: {e}")
        return 0
    except Exception as e:
        print(f"❌ Error during enhancement: {e}")
        return 0

def validate_articles_integrity(input_file='perplexityArticles.json'):
    """
    Validate article data integrity and report any issues.
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            articles_data = json.load(f)
        
        print(f"\n🔍 ARTICLE INTEGRITY CHECK")
        print(f"{'='*40}")
        
        required_fields = ['id', 'title', 'slug', 'content']
        recommended_fields = ['excerpt', 'category', 'datePublished', 'author']
        
        issues = []
        
        for i, article in enumerate(articles_data):
            article_issues = []
            
            # Check required fields
            for field in required_fields:
                if not article.get(field):
                    article_issues.append(f"Missing required field: {field}")
            
            # Check recommended fields
            for field in recommended_fields:
                if not article.get(field):
                    article_issues.append(f"Missing recommended field: {field}")
            
            # Check content length
            content = article.get('content', '')
            if len(content) < 500:
                article_issues.append(f"Content too short ({len(content)} chars)")
            
            # Check title length
            title = article.get('title', '')
            if len(title) > 60:
                article_issues.append(f"Title too long for SEO ({len(title)} chars)")
            
            if article_issues:
                issues.append((i, article.get('title', 'No title'), article_issues))
        
        if issues:
            print(f"❌ Found {len(issues)} articles with issues:")
            for idx, title, article_issues in issues[:10]:  # Show first 10
                print(f"\nArticle {idx}: '{title}'")
                for issue in article_issues:
                    print(f"  - {issue}")
            
            if len(issues) > 10:
                print(f"\n... and {len(issues) - 10} more articles with issues")
        else:
            print(f"✅ All articles pass integrity check!")
        
        return len(issues)
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return -1

if __name__ == "__main__":
    print("Starting article enhancement process...\n")
    
    # First validate current state
    validate_articles_integrity()
    
    # Then enhance articles
    enhanced_count = validate_and_enhance_articles()
    
    if enhanced_count > 0:
        print(f"\n🎉 Successfully enhanced {enhanced_count} article fields!")
        
        # Validate again after enhancement
        print(f"\nRunning post-enhancement validation...")
        validate_articles_integrity()
    else:
        print(f"\n✅ Articles were already optimized!")
