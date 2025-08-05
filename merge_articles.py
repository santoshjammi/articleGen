#!/usr/bin/env python3
"""
Script to merge articles.json into perplexityArticles.json
This script takes all articles from articles.json and adds them to perplexityArticles.json
with the enhanced SEO schema, while avoiding ID conflicts.
"""

import json
import re
from datetime import datetime

def generate_default_values_for_missing_fields(article):
    """Generate default values for missing fields in perplexity schema"""
    defaults = {
        "keyTakeaways": [],
        "socialMediaHashtags": [],
        "callToActionText": "Stay informed with the latest news and updates. Subscribe to our newsletter for more exclusive content!",
        "structuredData": generate_structured_data(article),
        "sourceKeyword": extract_source_keyword(article)
    }
    return defaults

def extract_source_keyword(article):
    """Extract a likely source keyword from the article"""
    # Use the first tag or extract from title
    if article.get("tags") and len(article["tags"]) > 0:
        return article["tags"][0].lower()
    else:
        # Extract first meaningful word from title
        title_words = re.findall(r'\b\w+\b', article.get("title", "").lower())
        return title_words[0] if title_words else "news"

def generate_structured_data(article):
    """Generate basic structured data JSON-LD for an article"""
    structured_data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": article.get("title", ""),
        "image": [article.get("ogImage", "")],
        "datePublished": f"{article.get('publishDate', '2025-08-05')}T12:00:00+00:00",
        "dateModified": f"{article.get('dateModified', '2025-08-05')}T12:00:00+00:00",
        "author": [{
            "@type": "Person",
            "name": article.get("author", "AI News Generator")
        }],
        "publisher": {
            "@type": "Organization", 
            "name": "JAMSA - Country's News",
            "logo": {
                "@type": "ImageObject",
                "url": "https://countrysnews.com/logo.png"
            }
        },
        "description": article.get("metaDescription", ""),
        "keywords": article.get("keywords", []),
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": article.get("canonicalUrl", "")
        }
    }
    return json.dumps(structured_data, indent=2)

def generate_hashtags_from_tags(tags):
    """Generate social media hashtags from article tags"""
    if not tags:
        return ["#News", "#Update"]
    
    hashtags = []
    for tag in tags[:5]:  # Limit to first 5 tags
        # Clean tag and make it hashtag-friendly
        clean_tag = re.sub(r'[^\w\s]', '', tag)
        clean_tag = re.sub(r'\s+', '', clean_tag)
        if clean_tag:
            hashtags.append(f"#{clean_tag}")
    
    return hashtags

def generate_key_takeaways(article):
    """Generate key takeaways from article content"""
    # This is a simplified version - in practice you'd want more sophisticated extraction
    content = article.get("content", "")
    excerpt = article.get("excerpt", "")
    
    takeaways = []
    if excerpt:
        takeaways.append(excerpt)
    
    # Try to extract some key points from content
    if content:
        # Look for headers or numbered points
        headers = re.findall(r'#{1,3}\s+(.+)', content)
        if headers:
            takeaways.extend(headers[:3])  # Take up to 3 headers
    
    # If we don't have enough, add some generic ones
    if len(takeaways) < 3:
        takeaways.extend([
            f"This article covers {article.get('category', 'news')} updates and analysis.",
            f"Key insights into {article.get('subCategory', 'current events')} are discussed.",
            f"Stay informed about the latest developments in {article.get('category', 'news')}."
        ])
    
    return takeaways[:5]  # Limit to 5 takeaways

def merge_articles():
    """Main function to merge articles"""
    
    # Load both files
    with open('/Users/kgt/Desktop/Projects/articleGen/articles.json', 'r', encoding='utf-8') as f:
        articles_data = json.load(f)
    
    with open('/Users/kgt/Desktop/Projects/articleGen/perplexityArticles.json', 'r', encoding='utf-8') as f:
        perplexity_data = json.load(f)
    
    print(f"Loaded {len(articles_data)} articles from articles.json")
    print(f"Loaded {len(perplexity_data)} articles from perplexityArticles.json")
    
    # Find the highest ID in perplexity articles to avoid conflicts
    max_id = 0
    for article in perplexity_data:
        try:
            article_id = int(article.get("id", "0"))
            max_id = max(max_id, article_id)
        except ValueError:
            pass
    
    print(f"Highest existing ID in perplexityArticles.json: {max_id}")
    
    # Process articles from articles.json
    merged_articles = perplexity_data.copy()  # Start with existing perplexity articles
    
    for article in articles_data:
        # Create enhanced article with perplexity schema
        enhanced_article = article.copy()
        
        # Update the ID to avoid conflicts
        max_id += 1
        enhanced_article["id"] = str(max_id)
        
        # Update author to match perplexity style
        enhanced_article["author"] = "JAMSA - Country's News"
        
        # Add missing advanced fields
        defaults = generate_default_values_for_missing_fields(enhanced_article)
        
        # Add key takeaways
        enhanced_article["keyTakeaways"] = generate_key_takeaways(enhanced_article)
        
        # Add social media hashtags
        enhanced_article["socialMediaHashtags"] = generate_hashtags_from_tags(enhanced_article.get("tags", []))
        
        # Add other missing fields
        enhanced_article["callToActionText"] = defaults["callToActionText"]
        enhanced_article["structuredData"] = defaults["structuredData"]
        enhanced_article["sourceKeyword"] = defaults["sourceKeyword"]
        
        merged_articles.append(enhanced_article)
        print(f"Added article: {enhanced_article.get('title', 'Untitled')} (ID: {enhanced_article['id']})")
    
    # Write merged data to perplexityArticles.json
    with open('/Users/kgt/Desktop/Projects/articleGen/perplexityArticles.json', 'w', encoding='utf-8') as f:
        json.dump(merged_articles, f, indent=4, ensure_ascii=False)
    
    print(f"\nMerge completed successfully!")
    print(f"Total articles in merged file: {len(merged_articles)}")
    print(f"Original perplexity articles: {len(perplexity_data)}")
    print(f"Added from articles.json: {len(articles_data)}")

if __name__ == "__main__":
    merge_articles()
