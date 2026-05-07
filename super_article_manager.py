#!/usr/bin/env python3
"""
SUPER-CONSOLIDATED Article Management System
Combines ALL article generation, enhancement, deduplication, and management functionality.

This module consolidates:
1. Article Generation (from article_generator.py)  
2. Article Enhancement (from enhance_articles.py)
3. Article Deduplication (from deduplicate_articles.py)
4. Article Merging (from merge_articles.py)
5. Article Fixing (from fix_articles.py)
6. Workflow Management (from workflow_deduplication.py)

One script to rule them all! 🚀
"""

import os
import re
import json
import math
import uuid
import aiohttp
import asyncio
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional, Union
from urllib.parse import quote
from collections import defaultdict
import random

# Local imports
from getTrendInput import get_top_region_keywords
from generateImage import generateImage

# === CONFIGURATION ===
DEFAULT_ARTICLES_FILE = "perplexityArticles_eeat_enhanced.json"
LEGACY_ARTICLES_FILE = "articles.json"
DEFAULT_AUTHOR = "JAMSA - Country's News"
DEFAULT_LANGUAGE = "en-IN"
DEFAULT_SCHEMA_TYPE = "NewsArticle"
DEFAULT_FACT_CHECKED_BY = "AI Content Review"
DEFAULT_EDITOR_REVIEWED_BY = "AI Editor"

# === AI CATEGORIZATION CLASSES ===

class AICategorizer:
    """Simple AI-powered categorization using content analysis"""
    
    def __init__(self):
        # Standard categories - simple and clean
        self.categories = [
            'Technology', 'Business', 'Health', 'Sports', 
            'Entertainment', 'Lifestyle', 'Environment', 'World'
        ]
        
        # Simple keyword patterns for basic categorization
        self.keyword_patterns = {
            'Technology': ['technology', 'tech', 'ai', 'artificial intelligence', 'software', 'app', 
                          'digital', 'computer', 'internet', 'cyber', 'data', 'algorithm', 'coding',
                          'programming', 'development', 'innovation', 'startup tech'],
            
            'Business': ['business', 'finance', 'financial', 'economy', 'economic', 'market',
                        'investment', 'banking', 'trade', 'commerce', 'corporate', 'company',
                        'industry', 'profit', 'revenue', 'startup', 'entrepreneur'],
            
            'Health': ['health', 'medical', 'medicine', 'doctor', 'hospital', 'healthcare',
                      'wellness', 'fitness', 'diet', 'nutrition', 'therapy', 'treatment',
                      'disease', 'mental health', 'vaccine'],
            
            'Sports': ['sports', 'sport', 'game', 'match', 'tournament', 'player', 'team',
                      'football', 'cricket', 'basketball', 'tennis', 'olympic', 'championship'],
            
            'Entertainment': ['movie', 'film', 'music', 'celebrity', 'entertainment', 'show',
                             'actor', 'actress', 'singer', 'concert', 'album', 'streaming'],
            
            'Lifestyle': ['lifestyle', 'fashion', 'food', 'travel', 'recipe', 'cooking',
                         'beauty', 'style', 'home', 'decoration', 'relationship'],
            
            'Environment': ['environment', 'climate', 'green', 'eco', 'sustainability',
                           'pollution', 'renewable', 'conservation', 'carbon', 'emission'],
            
            'World': ['news', 'politics', 'political', 'government', 'international',
                     'global', 'country', 'nation', 'war', 'peace', 'election', 'policy']
        }
    
    def categorize_article(self, article: Dict, use_ai: bool = True) -> Dict:
        """Categorize article based on content"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        keywords = [k.lower() for k in article.get('keywords', [])]
        
        # Combine all text for analysis
        text = f"{title} {content} {' '.join(keywords)}"
        
        # Score each category
        category_scores = {}
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                # Count occurrences of each pattern
                count = text.count(pattern.lower())
                # Weight by pattern importance (longer patterns = more specific)
                weight = len(pattern.split())
                score += count * weight
            
            category_scores[category] = score
        
        # Find best category
        if category_scores and max(category_scores.values()) > 0:
            best_category = max(category_scores, key=category_scores.get)
            max_score = category_scores[best_category]
            total_score = sum(category_scores.values())
            confidence = min(max_score / total_score if total_score > 0 else 0, 1.0)
        else:
            best_category = 'World'  # Default fallback
            confidence = 0.3
        
        return {
            'category': best_category,
            'confidence': confidence,
            'method': 'ai_keyword_analysis',
            'scores': category_scores
        }
    
    def batch_categorize(self, articles: List[Dict], use_ai: bool = True, max_ai_calls: int = 10) -> List[Dict]:
        """Categorize multiple articles efficiently"""
        results = []
        
        for i, article in enumerate(articles[:max_ai_calls]):
            try:
                result = self.categorize_article(article, use_ai)
                results.append({
                    'article': article,
                    'original_category': article.get('category'),
                    'ai_category': result['category'],
                    'confidence': result['confidence'],
                    'changed': article.get('category') != result['category'],
                    'scores': result.get('scores', {})
                })
                
                print(f"   [{i+1}/{min(len(articles), max_ai_calls)}] {article.get('title', 'Untitled')[:50]}...")
                print(f"       Original: {article.get('category', 'None')} → AI: {result['category']} (confidence: {result['confidence']:.2f})")
                
            except Exception as e:
                print(f"   ❌ Failed to categorize article {i+1}: {e}")
                results.append({
                    'article': article,
                    'original_category': article.get('category'),
                    'ai_category': article.get('category', 'World'),
                    'confidence': 0.0,
                    'changed': False,
                    'error': str(e)
                })
        
        return results

def simple_ai_categorize(title: str, content: str, keywords: List[str] = None) -> str:
    """Simple function for quick categorization"""
    categorizer = AICategorizer()
    article = {
        'title': title,
        'content': content,
        'keywords': keywords or []
    }
    result = categorizer.categorize_article(article)
    return result['category']

def categorize_with_confidence(article: Dict) -> Tuple[str, float]:
    """Categorize and return confidence score"""
    categorizer = AICategorizer()
    result = categorizer.categorize_article(article)
    return result['category'], result['confidence']

# === CATEGORY NORMALIZATION ===
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
    'Energy': 'World',
    
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

# === ENHANCED SUBCATEGORY-TO-CATEGORY MAPPING ===
SUBCATEGORY_MAPPING = {
    # Technology subcategories
    'Agile Certifications': 'Technology',
    'Agile Project Management': 'Technology',
    'Agile Methodologies': 'Technology',
    'Product Management': 'Technology',
    'Emerging Technologies': 'Technology',
    'Web Development': 'Technology',
    'Digital Economy': 'Technology',
    'Artificial Intelligence': 'Technology',
    'Software Development': 'Technology',
    'Programming': 'Technology',
    'DevOps': 'Technology',
    'Cloud Computing': 'Technology',
    'Cybersecurity': 'Technology',
    'Data Science': 'Technology',
    'Machine Learning': 'Technology',
    'Tech News': 'Technology',
    'Mobile Development': 'Technology',
    'API Development': 'Technology',
    'Database Management': 'Technology',
    'System Administration': 'Technology',
    'IT Management': 'Technology',
    
    # Business subcategories
    'Digital Strategy': 'Business',
    'Marketing Strategy': 'Business',
    'Business Strategy': 'Business',
    'Digital Marketing': 'Business',
    'International Business': 'Business',
    'Banking': 'Business',
    'Recruitment': 'Business',
    'Stock Market': 'Business',
    'Stock Analysis': 'Business',
    'Personal Finance': 'Business',
    'Retail': 'Business',
    'Fast Food': 'Business',
    'Semiconductors': 'Business',
    'Project Management': 'Business',
    'Business Analytics': 'Business',
    'E-commerce': 'Business',
    'Fintech': 'Business',
    'Startup': 'Business',
    'Entrepreneurship': 'Business',
    'Corporate Strategy': 'Business',
    'Business Development': 'Business',
    'Sales': 'Business',
    'Customer Service': 'Business',
    'Banking News': 'Business',
}

def categorize_by_subcategory(subcategory: str, current_category: str = None) -> str:
    """
    Determine the correct main category based on subcategory.
    This function prevents miscategorization by using subcategory information.
    
    Args:
        subcategory: The subcategory of the article
        current_category: The currently assigned category (for logging)
    
    Returns:
        str: The correct main category based on subcategory mapping
    """
    if not subcategory:
        return current_category or 'World'
    
    # Check if subcategory has a specific mapping
    mapped_category = SUBCATEGORY_MAPPING.get(subcategory)
    
    if mapped_category:
        # Log category changes for monitoring
        if current_category and current_category != mapped_category:
            print(f"🔄 Category corrected based on subcategory:")
            print(f"   Subcategory: '{subcategory}'")
            print(f"   Old Category: '{current_category}' → New Category: '{mapped_category}'")
        elif not current_category:
            print(f"✅ Category assigned based on subcategory:")
            print(f"   Subcategory: '{subcategory}' → Category: '{mapped_category}'")
        
        return mapped_category
    
    # No specific mapping found, return current category or default
    return current_category or 'World'

def normalize_category_enhanced(category: str, subcategory: str = None) -> str:
    """
    Enhanced category normalization that considers both category and subcategory.
    This is the main function to prevent miscategorization issues.
    
    Args:
        category: The main category
        subcategory: The subcategory (used for enhanced mapping)
    
    Returns:
        str: Normalized and corrected category
    """
    # Step 1: Check if subcategory provides a definitive category mapping
    if subcategory:
        subcategory_result = categorize_by_subcategory(subcategory, category)
        # If subcategory mapping found a specific category, use it
        if subcategory_result and subcategory_result != 'World':
            return subcategory_result
    
    # Step 2: Apply existing category normalization
    normalized_by_category = normalize_category(category) if category else None
    
    # Step 3: If subcategory suggests a category but main category normalization differs, 
    # prefer subcategory (it's more specific)
    if subcategory:
        subcategory_category = SUBCATEGORY_MAPPING.get(subcategory)
        if subcategory_category and normalized_by_category and subcategory_category != normalized_by_category:
            print(f"🔀 Subcategory override:")
            print(f"   Main category '{category}' → '{normalized_by_category}'")
            print(f"   But subcategory '{subcategory}' → '{subcategory_category}'")
            print(f"   Using subcategory mapping: '{subcategory_category}'")
            return subcategory_category
    
    # Step 4: Return normalized category or default
    return normalized_by_category or 'World'

# === SIMPLE AI CATEGORIZATION INTEGRATION ===

# Global AI categorizer
_AI_CATEGORIZER = None

def get_ai_categorizer():
    """Get or create AI categorizer"""
    global _AI_CATEGORIZER
    if _AI_CATEGORIZER is None:
        _AI_CATEGORIZER = AICategorizer()
    return _AI_CATEGORIZER

def categorize_with_ai(article: Dict, use_ai: bool = True) -> Dict:
    """Use AI to categorize article based on content"""
    try:
        categorizer = get_ai_categorizer()
        result = categorizer.categorize_article(article, use_ai)
        
        original_category = article.get('category', 'Unknown')
        if result['category'] != original_category:
            print(f"� AI categorization: {original_category} → {result['category']} (confidence: {result['confidence']:.2f}, method: {result['method']})")
        
        return {
            "category": result["category"] if result["confidence"] > 0.8 else article.get('category', result["category"]),
            "confidence": result["confidence"], 
            "method": result["method"],
            "changed": result["confidence"] > 0.8 and (article.get('category', 'Unknown') != result["category"])
        }
    except Exception as e:
        print(f"⚠️  AI categorization failed: {e}")
        # Fallback to existing normalization
        fallback_category = normalize_category(article.get("category", "World"))
        return {
            "category": fallback_category,
            "confidence": 0.3,
            "method": "fallback",
            "changed": False
        }

def normalize_category_with_ai(category: str, article: Dict = None) -> str:
    """Enhanced category normalization using AI when article data is available"""
    
    # If we have full article data, use AI categorization
    if article and (article.get('title') or article.get('content')):
        try:
            result = categorize_with_ai(article, use_ai=True)
            return result["category"]
        except Exception as e:
            print(f"⚠️  AI categorization failed: {e}")
    
    # Fallback to simple normalization
    return normalize_category(category) if category else 'World'

DEFAULT_VIEWS_COUNT = 0
DEFAULT_SHARES_COUNT = 0
DEFAULT_COMMENTS_COUNT = 0
DEFAULT_AVERAGE_RATING = 0.0
OUTPUT_DIR = "dist"
IMAGES_BASE_DIR = os.path.join(OUTPUT_DIR, "images")

# Image backup configuration
IMAGES_BACKUP_DIR = "images_backup"  # Local backup directory outside dist/

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = os.getenv("LLM_MODEL")  # e.g. "google/gemma-4-26b-a4b-it"

# === UTILITY FUNCTIONS ===

def sanitize_date_format(date_str):
    """Ensure date is in proper YYYY-MM-DD format for sitemaps"""
    if not date_str:
        return datetime.now().strftime('%Y-%m-%d')
    
    # Remove 'Z' suffix if present
    if date_str.endswith('Z'):
        date_str = date_str[:-1]
    
    # Check if it's already in correct format
    if len(date_str) == 10 and date_str.count('-') == 2:
        try:
            # Validate it's a real date
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            pass
    
    # Fallback to current date if invalid
    return datetime.now().strftime('%Y-%m-%d')

def normalize_category(category: str) -> str:
    """Normalize category to one of the consolidated main categories"""
    if not category:
        return 'World'
    
    # Direct mapping
    normalized = CATEGORY_MAPPING.get(category, None)
    if normalized:
        return normalized
    
    # Fuzzy matching for variations
    category_lower = category.lower()
    
    # Business variations
    if any(word in category_lower for word in ['business', 'finance', 'economy', 'economic']):
        return 'Business'
    
    # Health variations  
    if any(word in category_lower for word in ['health', 'medical', 'wellness', 'fitness']):
        return 'Health'
    
    # Tech variations
    if any(word in category_lower for word in ['technology', 'tech', 'digital', 'ai', 'software']):
        return 'Technology'
    
    # Sports variations
    if any(word in category_lower for word in ['sports', 'sport', 'athletics', 'games']):
        return 'Sports'
    
    # Entertainment variations
    if any(word in category_lower for word in ['entertainment', 'movie', 'music', 'celebrity', 'bollywood']):
        return 'Entertainment'
    
    # Lifestyle variations
    if any(word in category_lower for word in ['travel', 'food', 'lifestyle', 'career']):
        return 'Lifestyle'
    
    # Environment variations
    if any(word in category_lower for word in ['environment', 'climate', 'green', 'sustainability']):
        return 'Environment'
    
    # Default to World for news, politics, international affairs, etc.
    return 'World'

def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title"""
    if not title:
        return ""
    slug = re.sub(r"[^\w\s-]", "", title).strip().lower()
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug.strip('-')

def estimate_reading_time(content: str) -> Tuple[int, int]:
    """Estimate reading time and word count from HTML content"""
    clean_content = re.sub(r"<[^>]+>", "", content)
    words = len(clean_content.split())
    reading_time = math.ceil(words / 200)  # 200 words per minute
    return reading_time, words

def generate_placeholder_image_url(text: str, width: int = 1200, height: int = 630, 
                                 bg_color: str = "1f2937", text_color: str = "ffffff") -> str:
    """Generate placeholder image URL"""
    encoded = quote(text)
    return f"https://placehold.co/{width}x{height}/{bg_color}/{text_color}?text={encoded}"

def embed_inline_images(html_content: str, inline_images: List[Dict]) -> str:
    """Embed inline images and infographics into HTML content"""
    content = html_content
    
    # Separate regular images from infographics
    regular_images = [img for img in inline_images if img.get('type') != 'infographic']
    infographics = [img for img in inline_images if img.get('type') == 'infographic']
    
    # Embed regular images using paragraph placement
    for img in regular_images:
        paragraphs = list(re.finditer(r'(<p[^>]*>.*?</p>)', content, re.IGNORECASE | re.DOTALL))
        match = re.search(r"paragraph\s*(\d+)", img.get("placementHint", ""))
        n = int(match.group(1)) if match else 2
        insert_at = paragraphs[n-1].end() if len(paragraphs) >= n else len(content)
        img_tag = f'<img src="{img["url"]}" alt="{img["alt"]}" style="max-width:100%;" />'
        content = content[:insert_at] + img_tag + content[insert_at:]
    
    # Embed infographics using section placement
    for infographic in infographics:
        placement_hint = infographic.get("placementHint", "")
        if "infographic for section:" in placement_hint:
            section_name = placement_hint.replace("infographic for section:", "").strip()
            
            # Find the section heading and place infographic after it
            section_pattern = f"<h2>{re.escape(section_name)}</h2>"
            match = re.search(section_pattern, content, re.IGNORECASE)
            
            if match:
                # Insert after the first paragraph following the heading
                after_heading = content[match.end():]
                first_p_match = re.search(r'(<p[^>]*>.*?</p>)', after_heading, re.IGNORECASE | re.DOTALL)
                
                if first_p_match:
                    insert_pos = match.end() + first_p_match.end()
                else:
                    insert_pos = match.end()
                
                # Create enhanced infographic HTML with caption
                infographic_html = f'''
<div class="infographic-container" style="margin: 20px 0; text-align: center; background: #f8f9fa; padding: 15px; border-radius: 8px;">
    <img src="{infographic['url']}" alt="{infographic['alt']}" style="max-width: 100%; height: auto; border-radius: 4px;" />
    <p style="margin-top: 10px; font-style: italic; color: #666; font-size: 0.9em;">{infographic.get('caption', '')}</p>
</div>'''
                
                content = content[:insert_pos] + infographic_html + content[insert_pos:]
            else:
                # Fallback: place at the end if section not found
                img_tag = f'<img src="{infographic["url"]}" alt="{infographic["alt"]}" style="max-width:100%;" />'
                content = content + img_tag
    
    return content

def add_internal_links(content_html: str, all_titles_map: Dict[str, str], 
                      current_slug: str, max_links: int = 3) -> str:
    """Add internal links to other articles"""
    linked_content = content_html
    links_added = 0
    sorted_titles = sorted([t for t in all_titles_map if all_titles_map[t] != current_slug], 
                          key=len, reverse=True)
    
    for title in sorted_titles:
        if links_added >= max_links:
            break
        pattern = r"\b" + re.escape(title) + r"\b"
        if re.search(pattern, linked_content, re.IGNORECASE):
            slug = all_titles_map[title]
            link_tag = f'<a href="/articles/{slug}.html" class="text-blue-600 hover:underline font-semibold">{title}</a>'
            linked_content, count = re.subn(pattern, link_tag, linked_content, 
                                          count=1, flags=re.IGNORECASE)
            if count > 0:
                links_added += 1
    return linked_content

def expand_keywords(base_keyword: str, region: str) -> List[str]:
    """Expand keywords for better SEO"""
    expanded = [
        f"{base_keyword} in {region}",
        f"{base_keyword} news",
        f"{base_keyword} trends 2025",
        f"what is {base_keyword}",
        f"{base_keyword} analysis"
    ]
    return [kw for kw in expanded if kw not in [base_keyword]]

def validate_keyword_input(keywords: List[str]) -> List[str]:
    """Validate and clean keyword input"""
    valid_keywords = []
    for keyword in keywords:
        keyword = keyword.strip()
        if keyword and len(keyword) > 2:
            valid_keywords.append(keyword)
        else:
            print(f"⚠️  Skipping invalid keyword: '{keyword}'")
    return valid_keywords

def generate_excerpt(content: str, max_length: int = 160) -> str:
    """Generate an excerpt from content, optimized for meta descriptions"""
    if not content:
        return ""
    clean_content = re.sub(r'<[^>]+>', '', content)
    sentences = clean_content.split('. ')
    excerpt = sentences[0]
    if len(excerpt) < 80 and len(sentences) > 1:
        excerpt += '. ' + sentences[1]
    if len(excerpt) > max_length:
        excerpt = excerpt[:max_length-3] + '...'
    return excerpt

def map_region_code_to_full_name(region_code: str) -> str:
    """Map 2-letter country codes to full region names for AI prompts"""
    region_mapping = {
        "IN": "India",
        "US": "United States", 
        "GB": "United Kingdom",
        "CA": "Canada",
        "AU": "Australia",
        "DE": "Germany",
        "FR": "France",
        "JP": "Japan",
        "BR": "Brazil",
        "MX": "Mexico"
    }
    
    # If it's already a full name or not in mapping, return as is
    if len(region_code) > 2 or region_code not in region_mapping:
        return region_code
    
    return region_mapping[region_code].strip()

def generate_structured_data(article: Dict) -> str:
    """Generate JSON-LD structured data for an article"""
    structured_data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": article.get("title", ""),
        "image": [article.get("ogImage", "")],
        "datePublished": f"{article.get('publishDate', '2025-08-05')}T12:00:00+00:00",
        "dateModified": f"{article.get('dateModified', '2025-08-05')}T12:00:00+00:00",
        "author": [{
            "@type": "Person",
            "name": article.get("author", DEFAULT_AUTHOR)
        }],
        "publisher": {
            "@type": "Organization", 
            "name": "JAMSA - Country's News",
            "logo": {
                "@type": "ImageObject",
                "url": "https://countrysnews.com/logo.webp"
            }
        },
        "description": article.get("metaDescription", article.get("excerpt", ""))
    }
    return json.dumps(structured_data, separators=(',', ':'))

# === INTELLIGENT INFOGRAPHIC SYSTEM ===

class InfographicAnalyzer:
    """Intelligent system for analyzing content and generating appropriate infographics"""
    
    def __init__(self):
        self.section_patterns = {
            'process': [
                r'how does.*work',
                r'how to create',
                r'how to use',
                r'step-by-step',
                r'process',
                r'workflow'
            ],
            'comparison': [
                r'vs alternatives',
                r'comparison',
                r'pros and cons',
                r'advantages',
                r'disadvantages',
                r'benefits'
            ],
            'examples': [
                r'best.*examples',
                r'case studies',
                r'real-world',
                r'success stories',
                r'use cases'
            ],
            'data': [
                r'statistics',
                r'trends',
                r'future of',
                r'market data',
                r'research',
                r'surveys'
            ],
            'tools': [
                r'tools for',
                r'software',
                r'platforms',
                r'applications',
                r'resources'
            ],
            'mistakes': [
                r'mistakes to avoid',
                r'common errors',
                r'pitfalls',
                r'challenges'
            ]
        }
    
    def analyze_section(self, heading: str, content: str) -> Dict[str, any]:
        """Analyze a section and determine the best infographic type"""
        heading_lower = heading.lower()
        content_lower = content.lower()
        
        # Detect section type
        section_type = self._detect_section_type(heading_lower)
        
        # Analyze content structure
        has_numbered_list = bool(re.search(r'\d+\.\s', content))
        has_bullet_points = bool(re.search(r'[•\-\*]\s', content))
        has_statistics = bool(re.search(r'\d+%|\d+\s*(million|billion|thousand)', content_lower))
        has_comparisons = bool(re.search(r'vs\.|versus|compared to|better than', content_lower))
        has_steps = bool(re.search(r'step\s+\d+|first|second|third|finally|next', content_lower))
        
        return {
            'section_type': section_type,
            'infographic_type': self._determine_infographic_type(section_type, {
                'has_numbered_list': has_numbered_list,
                'has_bullet_points': has_bullet_points,
                'has_statistics': has_statistics,
                'has_comparisons': has_comparisons,
                'has_steps': has_steps
            }),
            'content_elements': {
                'numbered_lists': self._extract_numbered_lists(content),
                'bullet_points': self._extract_bullet_points(content),
                'statistics': self._extract_statistics(content),
                'comparisons': self._extract_comparisons(content)
            }
        }
    
    def _detect_section_type(self, heading: str) -> str:
        """Detect the type of section based on heading patterns"""
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, heading):
                    return section_type
        return 'general'
    
    def _determine_infographic_type(self, section_type: str, content_features: Dict) -> str:
        """Determine the best infographic type based on section and content analysis"""
        if section_type == 'process' or content_features['has_steps']:
            return 'flowchart'
        elif section_type == 'comparison' or content_features['has_comparisons']:
            return 'comparison_chart'
        elif section_type == 'examples':
            return 'case_study_layout'
        elif section_type == 'data' or content_features['has_statistics']:
            return 'data_visualization'
        elif section_type == 'tools':
            return 'tool_comparison'
        elif section_type == 'mistakes':
            return 'warning_infographic'
        elif content_features['has_numbered_list']:
            return 'numbered_infographic'
        elif content_features['has_bullet_points']:
            return 'bullet_infographic'
        else:
            return 'concept_diagram'
    
    def _extract_numbered_lists(self, content: str) -> List[str]:
        """Extract numbered list items"""
        pattern = r'\d+\.\s+(.+?)(?=\d+\.\s|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        return [match.strip() for match in matches]
    
    def _extract_bullet_points(self, content: str) -> List[str]:
        """Extract bullet point items"""
        pattern = r'[•\-\*]\s+(.+?)(?=[•\-\*]\s|$)'
        matches = re.findall(pattern, content, re.DOTALL)
        return [match.strip() for match in matches]
    
    def _extract_statistics(self, content: str) -> List[str]:
        """Extract statistical information"""
        pattern = r'(\d+%|\d+\s*(?:million|billion|thousand|times|increase|decrease))'
        matches = re.findall(pattern, content, re.IGNORECASE)
        return matches
    
    def _extract_comparisons(self, content: str) -> List[Dict]:
        """Extract comparison information"""
        # This is a simplified extraction - could be enhanced
        comparisons = []
        if 'vs.' in content.lower() or 'versus' in content.lower():
            comparisons.append({'type': 'versus', 'content': 'comparison detected'})
        return comparisons

def generate_infographic_prompt(keyword: str, section_heading: str, infographic_type: str, 
                               content_elements: Dict, section_content: str) -> str:
    """Generate AI prompt for creating infographics based on analysis"""
    
    base_prompt = f"Create a professional, clean infographic for the article section '{section_heading}' about '{keyword}'. It is very important not to have any garbled text in the images."
    
    if infographic_type == 'flowchart':
        elements = content_elements.get('numbered_lists', [])
        if elements:
            steps_text = " → ".join(elements[:5])  # Limit to 5 steps for clarity
            prompt = f"{base_prompt}Design a horizontal flowchart showing the process: {steps_text}. Use clean boxes connected by arrows, professional colors (blues and grays), and include the keyword '{keyword}' in the title. Make it suitable for a business article. Avoid clutter."
        else:
            prompt = f"{base_prompt}Create a process flowchart infographic showing how {keyword} works. Use connected boxes with arrows, clean typography, and professional styling. Include the keyword '{keyword}' prominently in the title."
    
    elif infographic_type == 'comparison_chart':
        prompt = f"{base_prompt}Design a comparison chart/table infographic comparing {keyword} with its alternatives. Use a clean table format or side-by-side comparison with pros/cons, checkmarks and X marks. Include the keyword '{keyword}' prominently in the title. Use professional colors."
    
    elif infographic_type == 'data_visualization':
        stats = content_elements.get('statistics', [])
        if stats:
            stats_text = ", ".join(stats[:3])
            prompt = f"{base_prompt}Create a data visualization infographic featuring these key statistics: {stats_text}. Use bar charts, pie charts, or statistical callouts. Include '{keyword}' in the title and use professional color scheme. Avoid clutter."
        else:
            prompt = f"{base_prompt}Design a statistical infographic about {keyword} trends and data. Include charts, graphs, and key numbers with clean, professional styling. Make sure to feature the keyword '{keyword}' prominently."
    
    elif infographic_type == 'case_study_layout':
        prompt = f"{base_prompt}Create a case study layout infographic showing successful examples of {keyword} implementation. Use before/after sections, success metrics, and clean professional design with the keyword '{keyword}' featured prominently."
    
    elif infographic_type == 'tool_comparison':
        prompt = f"{base_prompt}Design a tools and resources infographic for {keyword}. Show different software/platforms in a grid layout with icons, names, and key features. Include '{keyword}' in the title. Use clean, professional colors."
    
    elif infographic_type == 'warning_infographic':
        prompt = f"{base_prompt}Create a 'mistakes to avoid' infographic for {keyword}. Use warning icons, red accent colors for don'ts, and green for do's. List common pitfalls in a clean, organized layout. Include the keyword '{keyword}' in the title."
    
    elif infographic_type == 'numbered_infographic':
        elements = content_elements.get('numbered_lists', [])
        if elements:
            prompt = f"{base_prompt}Design a numbered list infographic with these key points: {'; '.join(elements[:5])}. Use numbered circles, clean typography, and include '{keyword}' in the title. Use professional colors."
        else:
            prompt = f"{base_prompt}Create a numbered steps infographic for {keyword}. Use clean numbered design with professional styling. Include the keyword '{keyword}' prominently in the title."
    
    else:  # concept_diagram
        prompt = f"{base_prompt}Design a concept diagram infographic explaining {keyword}. Use interconnected elements, clean typography, and professional color scheme with the keyword prominently displayed. Avoid clutter."
    
    return prompt

def calculate_article_score(article: Dict) -> float:
    """Calculate quality score for article ranking/deduplication"""
    score = 0
    content = article.get('content', '')
    score += min(len(content) / 100, 50)  # Max 50 points for content
    
    # Presence of important fields
    if article.get('title'): score += 10
    if article.get('excerpt'): score += 5
    if article.get('category'): score += 5
    if article.get('tags'): score += 3
    if article.get('publishDate'): score += 3
    if article.get('author'): score += 2
    if article.get('ogImage'): score += 2
    if article.get('thumbnailImageUrl'): score += 2
    if article.get('metaDescription'): score += 2
    
    # Penalize missing essential fields
    if not article.get('slug'): score -= 20
    if not article.get('id'): score -= 15
    
    return score

def backup_images(slug: str, image_files: List[str]) -> List[str]:
    """Backup generated images to local backup directory outside dist/"""
    if not image_files:
        return []
    
    backup_dir = os.path.join(IMAGES_BACKUP_DIR, slug)
    os.makedirs(backup_dir, exist_ok=True)
    
    backed_up_files = []
    
    for image_file in image_files:
        if os.path.exists(image_file):
            filename = os.path.basename(image_file)
            backup_path = os.path.join(backup_dir, filename)
            
            try:
                import shutil
                shutil.copy2(image_file, backup_path)
                backed_up_files.append(backup_path)
                print(f"📁 Backed up image: {filename} → {backup_path}")
            except Exception as e:
                print(f"⚠️  Failed to backup {filename}: {e}")
    
    return backed_up_files

def backup_all_article_images(articles: List[Dict]) -> None:
    """Backup all images from all articles to local backup directory"""
    print(f"\n📁 Backing up all article images to {IMAGES_BACKUP_DIR}/...")
    
    total_backed_up = 0
    
    for article in articles:
        slug = article.get('slug')
        if not slug:
            continue
            
        # Collect all image files for this article
        image_files = []
        
        # Main image
        if article.get('ogImage'):
            main_img_path = os.path.join(IMAGES_BASE_DIR, slug, "main.webp")
            if os.path.exists(main_img_path):
                image_files.append(main_img_path)
        
        # Thumbnail image
        if article.get('thumbnailImageUrl'):
            thumb_img_path = os.path.join(IMAGES_BASE_DIR, slug, "thumb.webp")
            if os.path.exists(thumb_img_path):
                image_files.append(thumb_img_path)
        
        # Inline images
        inline_images = article.get('inlineImages', [])
        for i, _ in enumerate(inline_images):
            inline_img_path = os.path.join(IMAGES_BASE_DIR, slug, f"inline_{i+1}.webp")
            if os.path.exists(inline_img_path):
                image_files.append(inline_img_path)
        
        # Backup images for this article
        if image_files:
            backed_up = backup_images(slug, image_files)
            total_backed_up += len(backed_up)
    
    print(f"✅ Backed up {total_backed_up} images to {IMAGES_BACKUP_DIR}/")

# === SUPER-CONSOLIDATED ARTICLE MANAGER ===

class SuperArticleManager:
    """The ultimate article management system"""
    
    def __init__(self, articles_file: str = DEFAULT_ARTICLES_FILE):
        self.articles_file = articles_file
        self.articles: List[Dict] = []
        self.articles_map: Dict[str, Dict] = {}
        self.processed_keywords: set = set()
        self.titles_map: Dict[str, str] = {}
        self.backup_files: List[str] = []
        self.stats = {
            'original_count': 0,
            'duplicates_removed': 0,
            'enhancements_applied': 0,
            'articles_generated': 0,
            'final_count': 0
        }
        
    def print_header(self, title: str, char: str = '=') -> None:
        """Print formatted header"""
        print(f"\n{char * 60}")
        print(f"🎯 {title}")
        print(f"{char * 60}")
    
    def _parse_content_sections(self, content: str) -> List[Dict]:
        """Parse content into sections based on headings"""
        sections = []
        
        # Split content by H2 headings
        h2_pattern = r'<h2>(.*?)</h2>'
        h2_matches = list(re.finditer(h2_pattern, content, re.IGNORECASE))
        
        for i, match in enumerate(h2_matches):
            heading = match.group(1)
            start_pos = match.end()
            
            # Find the end of this section (next H2 or end of content)
            if i + 1 < len(h2_matches):
                end_pos = h2_matches[i + 1].start()
            else:
                end_pos = len(content)
            
            section_content = content[start_pos:end_pos]
            
            # Clean up the content (remove HTML tags for analysis)
            clean_content = re.sub(r'<[^>]+>', '', section_content)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            sections.append({
                'heading': heading,
                'content': clean_content,
                'html_content': section_content
            })
        
        return sections
    
    def _should_generate_infographic(self, analysis: Dict, heading: str) -> bool:
        """Determine if a section should get an infographic"""
        # Skip very basic sections
        if 'what is' in heading.lower() and len(analysis['content_elements']['numbered_lists']) == 0:
            return False
        
        # Always generate for these types
        priority_types = ['comparison_chart', 'flowchart', 'data_visualization', 'tool_comparison']
        if analysis['infographic_type'] in priority_types:
            return True
        
        # Generate if content has structured elements
        elements = analysis['content_elements']
        if (len(elements['numbered_lists']) >= 3 or 
            len(elements['bullet_points']) >= 4 or 
            len(elements['statistics']) >= 2):
            return True
        
        # Generate for key process sections
        key_phrases = ['how does', 'how to', 'best practices', 'examples', 'tools', 'vs alternatives']
        if any(phrase in heading.lower() for phrase in key_phrases):
            return True
        
        return False
    
    def create_backup(self, suffix: str = "backup") -> Optional[str]:
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "perplexityArticles")
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"perplexityArticles_{suffix}_{timestamp}.json")
        
        try:
            if os.path.exists(self.articles_file):
                with open(self.articles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                with open(backup_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.backup_files.append(backup_file)
                print(f"📁 Backup created: {backup_file}")
                return backup_file
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
        return None
    
    def load_articles(self) -> Tuple[List[Dict], Dict[str, Dict], set]:
        """Load existing articles with all mappings"""
        if not os.path.exists(self.articles_file):
            print(f"ℹ️  {self.articles_file} not found. Starting fresh.")
            return [], {}, set()
            
        try:
            with open(self.articles_file, 'r', encoding='utf-8') as f:
                self.articles = json.load(f)
                
            print(f"✅ Loaded {len(self.articles)} existing articles")
            self.stats['original_count'] = len(self.articles)
            
            # Build mappings
            for article in self.articles:
                if "slug" in article:
                    self.articles_map[article["slug"]] = article
                if "sourceKeyword" in article and article["sourceKeyword"]:
                    self.processed_keywords.add(article["sourceKeyword"])
                if "title" in article and "slug" in article:
                    self.titles_map[article["title"]] = article["slug"]
                    
            return self.articles, self.articles_map, self.processed_keywords
            
        except json.JSONDecodeError as e:
            print(f"❌ Error decoding {self.articles_file}: {e}")
            return [], {}, set()
        except Exception as e:
            print(f"❌ Error loading articles: {e}")
            return [], {}, set()
    
    def save_articles(self, articles_map: Dict[str, Dict] = None) -> bool:
        """Save articles to JSON file"""
        try:
            if articles_map is None:
                articles_map = self.articles_map
            
            articles_list = list(articles_map.values())
            with open(self.articles_file, 'w', encoding='utf-8') as f:
                json.dump(articles_list, f, indent=4, ensure_ascii=False)
            print(f"💾 Saved {len(articles_list)} articles to {self.articles_file}")
            self.stats['final_count'] = len(articles_list)
            return True
        except Exception as e:
            print(f"❌ Error saving articles: {e}")
            return False
    
    def get_next_article_id(self) -> int:
        """Get the next available article ID"""
        if not self.articles:
            return 1
        
        max_id = 0
        for article in self.articles:
            if 'id' in article and str(article['id']).isdigit():
                max_id = max(max_id, int(article['id']))
        
        return max_id + 1
    
    def analyze_duplicates(self) -> Dict:
        """Analyze articles for duplicates"""
        print("\n🔍 Analyzing articles for duplicates...")
        
        duplicates = {
            'by_id': defaultdict(list),
            'by_title': defaultdict(list),
            'by_slug': defaultdict(list),
            'by_content_hash': defaultdict(list)
        }
        
        for i, article in enumerate(self.articles):
            # Group by ID
            if article.get('id'):
                duplicates['by_id'][article['id']].append(i)
            
            # Group by title
            if article.get('title'):
                title_key = article['title'].lower().strip()
                duplicates['by_title'][title_key].append(i)
            
            # Group by slug
            if article.get('slug'):
                duplicates['by_slug'][article['slug']].append(i)
            
            # Group by content hash (simplified)
            content = article.get('content', '')
            if content:
                content_hash = hash(content[:500])  # First 500 chars
                duplicates['by_content_hash'][content_hash].append(i)
        
        # Filter to actual duplicates
        actual_duplicates = {}
        for dup_type, groups in duplicates.items():
            actual_duplicates[dup_type] = {k: v for k, v in groups.items() if len(v) > 1}
        
        total_dups = sum(len(v) - 1 for groups in actual_duplicates.values() for v in groups.values())
        print(f"📊 Found {total_dups} potential duplicates across all categories")
        
        return actual_duplicates
    
    def deduplicate_articles(self, duplicates: Dict) -> int:
        """Remove duplicate articles, keeping the best ones"""
        print("\n🗑️  Removing duplicate articles...")
        
        articles_to_remove = set()
        
        for dup_type, groups in duplicates.items():
            for key, indices in groups.items():
                if len(indices) <= 1:
                    continue
                
                # Score each article and keep the best one
                scored_articles = []
                for idx in indices:
                    score = calculate_article_score(self.articles[idx])
                    scored_articles.append((score, idx, self.articles[idx]))
                
                # Sort by score (descending) and keep the best
                scored_articles.sort(reverse=True, key=lambda x: x[0])
                best_article = scored_articles[0]
                
                # Mark others for removal
                for score, idx, article in scored_articles[1:]:
                    articles_to_remove.add(idx)
                    print(f"   Removing duplicate: {article.get('title', 'No title')[:50]}...")
        
        # Remove duplicates (in reverse order to maintain indices)
        for idx in sorted(articles_to_remove, reverse=True):
            del self.articles[idx]
        
        removed_count = len(articles_to_remove)
        self.stats['duplicates_removed'] = removed_count
        print(f"✅ Removed {removed_count} duplicate articles")
        
        return removed_count
    
    def enhance_articles(self) -> int:
        """Enhance articles with missing fields and better metadata"""
        print("\n✨ Enhancing articles...")
        
        enhanced_count = 0
        base_date = datetime.now() - timedelta(days=30)
        
        for i, article in enumerate(self.articles):
            original_article = article.copy()
            
            # Generate missing slug
            if not article.get('slug') and article.get('title'):
                article['slug'] = generate_slug(article['title'])
            
            # AI-powered category assignment
            if article.get('category'):
                # Use AI categorization with full article context
                ai_result = normalize_category_with_ai(
                    article['category'],
                    article  # Pass full article for AI analysis
                )
                
                if ai_result != article.get('category'):
                    print(f"� AI enhancement: '{article.get('category')}' → '{ai_result}'")
                    article['category'] = ai_result
            else:
                # Use AI categorization to assign missing category
                article['category'] = normalize_category_with_ai(None, article)
            
            # Generate missing excerpt
            if not article.get('excerpt') and article.get('content'):
                article['excerpt'] = generate_excerpt(article['content'])
            
            # Add missing dates
            if not article.get('publishDate'):
                # Random date within last 30 days
                random_days = random.randint(0, 30)
                pub_date = base_date + timedelta(days=random_days)
                article['publishDate'] = pub_date.strftime('%Y-%m-%d')
            
            if not article.get('dateModified'):
                article['dateModified'] = sanitize_date_format(article.get('publishDate', datetime.now().strftime('%Y-%m-%d')))
            else:
                article['dateModified'] = sanitize_date_format(article['dateModified'])
            
            # Ensure publishDate is also properly formatted
            if article.get('publishDate'):
                article['publishDate'] = sanitize_date_format(article['publishDate'])
            
            # Add missing author
            if not article.get('author'):
                article['author'] = DEFAULT_AUTHOR
            
            # Calculate reading time
            if article.get('content'):
                reading_time, word_count = estimate_reading_time(article['content'])
                article['readingTimeMinutes'] = reading_time
                article['wordCount'] = word_count
            
            # Generate missing meta description
            if not article.get('metaDescription') and article.get('excerpt'):
                article['metaDescription'] = article['excerpt'][:160]
            
            # Add missing structured data
            if not article.get('structuredData'):
                article['structuredData'] = generate_structured_data(article)
            
            # Add missing fields with defaults
            defaults = {
                'keyTakeaways': [],
                'socialMediaHashtags': [],
                'callToActionText': 'Stay informed with the latest news and updates!',
                'language': DEFAULT_LANGUAGE,
                'viewsCount': DEFAULT_VIEWS_COUNT,
                'sharesCount': DEFAULT_SHARES_COUNT,
                'commentsCount': DEFAULT_COMMENTS_COUNT,
                'averageRating': DEFAULT_AVERAGE_RATING,
                'featured': False,
                'factCheckedBy': DEFAULT_FACT_CHECKED_BY,
                'editorReviewedBy': DEFAULT_EDITOR_REVIEWED_BY
            }
            
            for field, default_value in defaults.items():
                if field not in article:
                    article[field] = default_value
            
            # Check if article was actually enhanced
            if article != original_article:
                enhanced_count += 1
        
        self.stats['enhancements_applied'] = enhanced_count
        print(f"✅ Enhanced {enhanced_count} articles")
        return enhanced_count
    
    def fix_article_issues(self) -> int:
        """Fix specific article issues like long titles, missing IDs, etc."""
        print("\n🔧 Fixing article issues...")
        
        fixed_count = 0
        used_ids = set()
        
        for article in self.articles:
            original_article = article.copy()
            
            # Fix missing or duplicate IDs
            if not article.get('id') or article['id'] in used_ids:
                new_id = 1
                while str(new_id) in used_ids:
                    new_id += 1
                article['id'] = str(new_id)
            used_ids.add(article['id'])
            
            # Fix overly long titles
            if article.get('title') and len(article['title']) > 100:
                article['title'] = article['title'][:97] + '...'
            
            # Ensure canonical URLs
            if article.get('slug'):
                article['ogUrl'] = f"https://countrysnews.com/articles/{article['slug']}.html"
                article['canonicalUrl'] = article['ogUrl']
            
            if article != original_article:
                fixed_count += 1
        
        print(f"✅ Fixed issues in {fixed_count} articles")
        return fixed_count
    
    def merge_legacy_articles(self) -> int:
        """Merge articles from legacy articles.json file"""
        if not os.path.exists(LEGACY_ARTICLES_FILE):
            print("ℹ️  No legacy articles.json file found")
            return 0
        
        print("\n🔄 Merging legacy articles...")
        
        try:
            with open(LEGACY_ARTICLES_FILE, 'r', encoding='utf-8') as f:
                legacy_articles = json.load(f)
            
            merged_count = 0
            existing_slugs = {a.get('slug') for a in self.articles if a.get('slug')}
            
            for legacy_article in legacy_articles:
                slug = legacy_article.get('slug')
                if slug and slug not in existing_slugs:
                    # Add generation method marker
                    legacy_article['generationMethod'] = 'legacy'
                    self.articles.append(legacy_article)
                    existing_slugs.add(slug)
                    merged_count += 1
            
            print(f"✅ Merged {merged_count} legacy articles")
            return merged_count
            
        except Exception as e:
            print(f"❌ Error merging legacy articles: {e}")
            return 0
    
    def show_statistics(self) -> None:
        """Show comprehensive article statistics"""
        print(f"\n📊 Article Statistics")
        print("=" * 40)
        print(f"Total articles: {len(self.articles)}")
        print(f"Processed keywords: {len(self.processed_keywords)}")
        
        # Category breakdown
        categories = {}
        generation_methods = {}
        authors = {}
        
        for article in self.articles:
            cat = article.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
            
            method = article.get('generationMethod', 'legacy')
            generation_methods[method] = generation_methods.get(method, 0) + 1
            
            author = article.get('author', 'Unknown')
            authors[author] = authors.get(author, 0) + 1
        
        print(f"\n📁 Categories:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {cat}: {count}")
        
        print(f"\n🛠️  Generation Methods:")
        for method, count in sorted(generation_methods.items(), key=lambda x: x[1], reverse=True):
            print(f"   {method}: {count}")
        
        print(f"\n✍️  Authors:")
        for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {author}: {count}")
        
        # Recent articles
        recent_articles = sorted(self.articles, key=lambda x: x.get('publishDate', ''), reverse=True)[:5]
        print(f"\n📰 Recent Articles:")
        for article in recent_articles:
            print(f"   • {article.get('title', 'No title')[:60]} ({article.get('publishDate', 'No date')})")
        
        # Workflow stats
        if any(self.stats.values()):
            print(f"\n🔄 Workflow Statistics:")
            for key, value in self.stats.items():
                if value > 0:
                    print(f"   {key.replace('_', ' ').title()}: {value}")

# === ARTICLE GENERATION (from original article_generator.py) ===

class ArticleGenerator:
    """Core article generation engine"""
    
    def __init__(self, manager: SuperArticleManager):
        self.manager = manager
        if LLM_MODEL and OPENROUTER_API_KEY:
            self.api_key = OPENROUTER_API_KEY
            self.use_openrouter = True
            print(f"🤖 Using OpenRouter model: {LLM_MODEL}")
        else:
            self.api_key = GEMINI_API_KEY
            self.use_openrouter = False
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
    
    def _parse_content_sections(self, content: str) -> List[Dict]:
        """Parse content into sections based on headings"""
        sections = []
        
        # Split content by H2 headings
        h2_pattern = r'<h2>(.*?)</h2>'
        h2_matches = list(re.finditer(h2_pattern, content, re.IGNORECASE))
        
        for i, match in enumerate(h2_matches):
            heading = match.group(1)
            start_pos = match.end()
            
            # Find the end of this section (next H2 or end of content)
            if i + 1 < len(h2_matches):
                end_pos = h2_matches[i + 1].start()
            else:
                end_pos = len(content)
            
            section_content = content[start_pos:end_pos]
            
            # Clean up the content (remove HTML tags for analysis)
            clean_content = re.sub(r'<[^>]+>', '', section_content)
            clean_content = re.sub(r'\s+', ' ', clean_content).strip()
            
            sections.append({
                'heading': heading,
                'content': clean_content,
                'html_content': section_content
            })
        
        return sections
    
    def _should_generate_infographic(self, analysis: Dict, heading: str) -> bool:
        """Determine if a section should get an infographic"""
        # Skip very basic sections
        if 'what is' in heading.lower() and len(analysis['content_elements']['numbered_lists']) == 0:
            return False
        
        # Always generate for these types
        priority_types = ['comparison_chart', 'flowchart', 'data_visualization', 'tool_comparison']
        if analysis['infographic_type'] in priority_types:
            return True
        
        # Generate if content has structured elements
        elements = analysis['content_elements']
        if (len(elements['numbered_lists']) >= 3 or 
            len(elements['bullet_points']) >= 4 or 
            len(elements['statistics']) >= 2):
            return True
        
        # Generate for key process sections
        key_phrases = ['how does', 'how to', 'best practices', 'examples', 'tools', 'vs alternatives']
        if any(phrase in heading.lower() for phrase in key_phrases):
            return True
        
        return False
    
    async def generate_article_from_keyword(self, session: aiohttp.ClientSession,
                                          keyword: str, region: str,
                                          article_id_counter: int,
                                          custom_prompt_additions: str = "",
                                          searches: Optional[int] = None) -> Optional[Dict]:
        """Generate a single article from a keyword"""
        
        # Create enhanced prompt
        # if searches:
        #     base_prompt = f"""Generate a comprehensive news article about "{keyword}" for readers in {region}. 
        #     This keyword is trending with {searches} searches.
            
        #     Requirements:
        #     - 1200+ words of high-quality, informative content
        #     - SEO-optimized with natural keyword integration
        #     - Include current trends and recent developments
        #     - Professional journalistic tone
        #     - Well-structured with clear headings and paragraphs
        #     - Include quotes, statistics, or expert opinions where relevant
        #     - Ensure content is accurate and factual
            
        #     {custom_prompt_additions}"""
        # else:
        #     base_prompt = f"""Generate a comprehensive, engaging news article about "{keyword}" specifically for readers in {region}.
            
        #     Requirements:
        #     - 1200+ words of high-quality, informative content
        #     - SEO-optimized with natural keyword integration
        #     - Include current trends and recent developments
        #     - Professional journalistic tone
        #     - Well-structured with clear headings and paragraphs
        #     - Include quotes, statistics, or expert opinions where relevant
        #     - Ensure content is accurate and factual
            
        #     {custom_prompt_additions}"""

        # Update the base_prompt section in the generate_article_from_keyword method
        if searches:
            base_prompt = f"""You are a content strategist and AI search optimization expert. Your goal is to generate a comprehensive, keyword-optimized article about "{keyword}" for readers in {region}. This article must be strategically structured with high keyword density and optimized to be easily summarized and cited by AI answer engines like Perplexity.

            This keyword is trending with {searches} searches.

            **CRITICAL KEYWORD INTEGRATION REQUIREMENTS:**
            - The EXACT phrase "{keyword}" MUST appear in EVERY major heading (H2/H3)
            - Use creative variations like: "What is {keyword}?", "{keyword} - Complete Guide", "How {keyword} Works", "Best {keyword} Practices"
            - Achieve HIGH DENSITY: Mention "{keyword}" at least 15-20 times throughout the article
            - Never miss including the keyword in header sections - this is mandatory

            **COMPREHENSIVE QUESTION-BASED STRUCTURE:**
            You must address ALL of these question categories with keyword-optimized headings:

            **FOUNDATIONAL QUESTIONS (Search Intent Analysis):**
            1. "What is {keyword}?" - Define and explain the core concept
            2. "Why Do You Need {keyword}?" - Address the problem it solves
            3. "How Does {keyword} Work?" - Explain the process/methodology
            
            **PRACTICAL APPLICATION QUESTIONS (Related Queries):**
            4. "Best {keyword} Examples" - Show real-world applications
            5. "How to Create/Use {keyword}" - Step-by-step implementation
            6. "Common {keyword} Mistakes to Avoid" - Troubleshooting and pitfalls
            
            **ADVANCED QUESTIONS (Industry Standards):**
            7. "Advanced {keyword} Techniques" - Expert-level insights
            8. "Tools for {keyword}" - Software, resources, platforms
            9. "{keyword} Best Practices in {region}" - Regional/contextual considerations
            
            **FUTURE-FOCUSED QUESTIONS:**
            10. "Future of {keyword}" - Trends and evolution
            11. "{keyword} vs Alternatives" - Competitive analysis

            **LOGICAL INFORMATION ARCHITECTURE:**
            - **Foundation Layer**: What → Why (Problem/Solution fit)
            - **Application Layer**: How → Examples (Implementation)
            - **Optimization Layer**: Best Practices → Advanced Techniques
            - **Strategic Layer**: Tools → Future Trends → Regional Context

            **CONTENT REQUIREMENTS:**
            - Article must be over 1500 words (increased from 1200)
            - Each section minimum 100-150 words
            - Include bullet points, numbered lists, and bold text
            - Add hypothetical data: "Recent studies show...", "Industry surveys indicate..."
            - Use conversational but authoritative tone
            - Include current 2025 trends and developments
            - End with engagement question for comments

            **SCANNABLE FORMATTING:**
            - Bold the keyword phrase in the first paragraph
            - Use bullet points for benefits/features
            - Include numbered steps for processes
            - Add comparison tables where relevant
            - Use subheadings for better readability

            {custom_prompt_additions}"""
        else:
            base_prompt = f"""You are a content strategist and AI search optimization expert. Your goal is to generate a comprehensive, keyword-optimized article about "{keyword}" specifically for readers in {region}. This article must be strategically structured with high keyword density and optimized to be easily summarized and cited by AI answer engines like Perplexity.

            **CRITICAL KEYWORD INTEGRATION REQUIREMENTS:**
            - The EXACT phrase "{keyword}" MUST appear in EVERY major heading (H2/H3)
            - Use creative variations like: "What is {keyword}?", "{keyword} - Complete Guide", "How {keyword} Works", "Best {keyword} Practices"
            - Achieve HIGH DENSITY: Mention "{keyword}" at least 15-20 times throughout the article
            - Never miss including the keyword in header sections - this is mandatory

            **COMPREHENSIVE QUESTION-BASED STRUCTURE:**
            You must address ALL of these question categories with keyword-optimized headings:

            **FOUNDATIONAL QUESTIONS (Search Intent Analysis):**
            1. "What is {keyword}?" - Define and explain the core concept
            2. "Why Do You Need {keyword}?" - Address the problem it solves
            3. "How Does {keyword} Work?" - Explain the process/methodology
            
            **PRACTICAL APPLICATION QUESTIONS (Related Queries):**
            4. "Best {keyword} Examples" - Show real-world applications
            5. "How to Create/Use {keyword}" - Step-by-step implementation
            6. "Common {keyword} Mistakes to Avoid" - Troubleshooting and pitfalls
            
            **ADVANCED QUESTIONS (Industry Standards):**
            7. "Advanced {keyword} Techniques" - Expert-level insights
            8. "Tools for {keyword}" - Software, resources, platforms
            9. "{keyword} Best Practices in {region}" - Regional/contextual considerations
            
            **FUTURE-FOCUSED QUESTIONS:**
            10. "Future of {keyword}" - Trends and evolution
            11. "{keyword} vs Alternatives" - Competitive analysis

            **LOGICAL INFORMATION ARCHITECTURE:**
            - **Foundation Layer**: What → Why (Problem/Solution fit)
            - **Application Layer**: How → Examples (Implementation)
            - **Optimization Layer**: Best Practices → Advanced Techniques
            - **Strategic Layer**: Tools → Future Trends → Regional Context

            **CONTENT REQUIREMENTS:**
            - Article must be over 1500 words (increased from 1200)
            - Each section minimum 100-150 words
            - Include bullet points, numbered lists, and bold text
            - Add hypothetical data: "Recent studies show...", "Industry surveys indicate..."
            - Use conversational but authoritative tone
            - Include current 2025 trends and developments
            - End with engagement question for comments

            **SCANNABLE FORMATTING:**
            - Bold the keyword phrase in the first paragraph
            - Use bullet points for benefits/features
            - Include numbered steps for processes
            - Add comparison tables where relevant
            - Use subheadings for better readability

            {custom_prompt_additions}"""

        headers = {'Content-Type': 'application/json'}
        
        # Response schema (used by Gemini native; embedded in prompt for OpenRouter)
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING", "description": "Compelling, SEO-optimized title (60 chars max)"},
                "excerpt": {"type": "STRING", "description": "Engaging summary (150-160 chars)"},
                "content": {"type": "STRING", "description": "Full HTML article content (1200+ words)"},
                "metaDescription": {"type": "STRING", "description": "SEO meta description (150-160 chars)"},
                "keywords": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "10-15 relevant SEO keywords"},
                "ogTitle": {"type": "STRING", "description": "Social media optimized title"},
                "imageAltText": {"type": "STRING", "description": "Descriptive alt text for main image"},
                "socialShareText": {"type": "STRING", "description": "Compelling social media share text"},
                "category": {"type": "STRING", "description": "Main article category"},
                "subCategory": {"type": "STRING", "description": "Specific subcategory"},
                "contentType": {"type": "STRING", "description": "Content type (news, analysis, guide, etc.)"},
                "difficultyLevel": {"type": "STRING", "description": "Reading difficulty (beginner, intermediate, advanced)"},
                "targetAudience": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Target audience segments"},
                "inlineImageDescriptions": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "description": {"type": "STRING", "description": "Image content description"},
                            "caption": {"type": "STRING", "description": "Image caption"},
                            "placementHint": {"type": "STRING", "description": "Where to place (e.g., 'after paragraph 3')"}
                        },
                        "required": ["description", "caption"]
                    },
                    "description": "2-4 inline images for the article"
                },
                "keyTakeaways": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "3-5 key points"},
                "socialMediaHashtags": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Relevant hashtags"},
                "callToActionText": {"type": "STRING", "description": "Engaging CTA for readers"},
                "structuredData": {"type": "STRING", "description": "JSON-LD structured data for SEO"},
                "relatedTopics": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Related topics for further reading"}
            },
            "required": [
                "title", "excerpt", "content", "metaDescription", "keywords",
                "ogTitle", "imageAltText", "socialShareText",
                "category", "contentType", "difficultyLevel", "targetAudience",
                "inlineImageDescriptions", "keyTakeaways", "socialMediaHashtags",
                "callToActionText", "structuredData","subCategory"
            ]
        }

        if self.use_openrouter:
            json_schema_hint = (
                "\n\nRespond with ONLY a valid JSON object (no markdown, no code fences) "
                "with these exact fields: title (string), excerpt (string), content (string, full HTML), "
                "metaDescription (string), keywords (array of strings), ogTitle (string), "
                "imageAltText (string), socialShareText (string), category (string), subCategory (string), "
                "contentType (string), difficultyLevel (string), targetAudience (array of strings), "
                "inlineImageDescriptions (array of objects with description, caption, placementHint), "
                "keyTakeaways (array of strings), socialMediaHashtags (array of strings), "
                "callToActionText (string), structuredData (string), relatedTopics (array of strings)."
            )
            payload = {
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": base_prompt + json_schema_hint}],
                "temperature": 0.7,
                "max_tokens": 8192,
            }
            headers['Authorization'] = f'Bearer {self.api_key}'
            url = OPENROUTER_API_URL
        else:
            payload = {
                "contents": [{"role": "user", "parts": [{"text": base_prompt}]}],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "responseSchema": response_schema,
                    "temperature": 0.7,
                    "maxOutputTokens": 8192
                }
            }
            url = f"{GEMINI_API_URL}?key={self.api_key}"

        try:
            async with session.post(url, headers=headers, data=json.dumps(payload)) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"❌ API error {resp.status} for '{keyword}': {error_text}")
                    return None

                result = await resp.json()

                if self.use_openrouter:
                    if not (result.get("choices") and result["choices"][0].get("message")):
                        print(f"❌ Invalid OpenRouter response structure for '{keyword}'")
                        return None
                    gen_str = result["choices"][0]["message"]["content"]
                else:
                    if not (result.get("candidates") and
                           result["candidates"][0].get("content") and
                           result["candidates"][0]["content"].get("parts")):
                        print(f"❌ Invalid API response structure for '{keyword}'")
                        return None
                    gen_str = result["candidates"][0]["content"]["parts"][0]["text"]

                data = json.loads(gen_str)
                
                # Generate article metadata
                now = sanitize_date_format(datetime.now().strftime("%Y-%m-%d"))
                slug = generate_slug(data['title'])
                reading_time, word_count = estimate_reading_time(data['content'])
                
                # Create images directory
                os.makedirs(os.path.join(IMAGES_BASE_DIR, slug), exist_ok=True)
                
                # Generate main image
                og_image_prompt = f"Professional news article image for: {data['ogTitle']}. Visual style: {data['imageAltText']}. High quality, news-appropriate. It is very important not to have any garbled text in the images."
                og_img_fp = os.path.join(IMAGES_BASE_DIR, slug, "main.webp")
                og_image_url = generateImage(og_image_prompt, og_img_fp) or generate_placeholder_image_url(data['ogTitle'])
                
                # Generate thumbnail image
                thumb_image_prompt = f"Thumbnail for news article: {data['ogTitle']}. Compact, visually appealing, news-style thumbnail. High quality. It is very important not to have any garbled text in the images."
                thumb_img_fp = os.path.join(IMAGES_BASE_DIR, slug, "thumb.webp")
                thumbnail_url = generateImage(thumb_image_prompt, thumb_img_fp) or generate_placeholder_image_url(data['ogTitle'], 400, 200)
                
                # Generate inline images with intelligent infographics
                inline_images_list = []
                inline_image_descs = data.get("inlineImageDescriptions", [])
                
                # Initialize infographic analyzer
                infographic_analyzer = InfographicAnalyzer()
                
                # Parse content into sections for infographic analysis
                content_sections = self._parse_content_sections(data['content'])
                infographic_count = 0
                
                for i, img_desc in enumerate(inline_image_descs):
                    # Standard inline image generation
                    inline_prompt = f"Supporting image for article section: {img_desc['description']}. Caption context: {img_desc['caption']}. Professional, high-quality. It is very important not to have any garbled text in the images."
                    inline_fp = os.path.join(IMAGES_BASE_DIR, slug, f"inline_{i+1}.webp")
                    inline_url = generateImage(inline_prompt, inline_fp) or generate_placeholder_image_url(
                        img_desc.get("description", f"Article Image {i+1}")
                    )
                    
                    if inline_url:
                        inline_images_list.append({
                            "url": inline_url,
                            "alt": img_desc.get('description', f'Article illustration {i+1}'),
                            "caption": img_desc.get('caption', ''),
                            "placementHint": img_desc.get('placementHint', f'after paragraph {i+2}')
                        })
                
                # Generate intelligent infographics for key sections
                for section_idx, section in enumerate(content_sections):
                    if section['heading'] and len(section['content']) > 100:  # Only for substantial sections
                        analysis = infographic_analyzer.analyze_section(section['heading'], section['content'])
                        
                        # Determine if this section warrants an infographic
                        if self._should_generate_infographic(analysis, section['heading']):
                            infographic_count += 1
                            infographic_prompt = generate_infographic_prompt(
                                keyword, 
                                section['heading'], 
                                analysis['infographic_type'], 
                                analysis['content_elements'],
                                section['content']
                            )
                            
                            infographic_fp = os.path.join(IMAGES_BASE_DIR, slug, f"infographic_{infographic_count}.webp")
                            infographic_url = generateImage(infographic_prompt, infographic_fp)
                            
                            if infographic_url:
                                inline_images_list.append({
                                    "url": infographic_url,
                                    "alt": f"Infographic: {section['heading']} - {keyword}",
                                    "caption": f"Visual guide: {section['heading']}",
                                    "placementHint": f"infographic for section: {section['heading']}",
                                    "type": "infographic"
                                })
                
                print(f"📊 Generated {infographic_count} intelligent infographics for '{keyword}'")
                
                # Process content
                content_html = embed_inline_images(data['content'], inline_images_list)
                content_html = add_internal_links(content_html, self.manager.titles_map, slug)
                
                # Expand keywords for better SEO
                expanded_keywords = expand_keywords(keyword, region)
                all_keywords = list(set(data['keywords'] + expanded_keywords))
                
                # Build complete article object (with initial category)
                article = {
                    "id": str(article_id_counter),
                    "slug": slug,
                    "title": data['title'],
                    "author": DEFAULT_AUTHOR,
                    "publishDate": now,
                    "dateModified": now,
                    "category": data['category'],  # Use original category first
                    "subCategory": data.get('subCategory', ''),
                    "tags": all_keywords,
                    "excerpt": data['excerpt'],
                    "content": content_html,
                    "metaDescription": data['metaDescription'],
                    "keywords": all_keywords,
                    "ogTitle": data['ogTitle'],
                    "ogImage": og_image_url,
                    "imageAltText": data['imageAltText'],
                    "ogUrl": f"https://countrysnews.com/articles/{slug}.html",
                    "canonicalUrl": f"https://countrysnews.com/articles/{slug}.html",
                    "schemaType": DEFAULT_SCHEMA_TYPE,
                    "readingTimeMinutes": reading_time,
                    "wordCount": word_count,
                    "lastReviewedDate": now,
                    "relatedArticleIds": [],
                    "socialShareText": data['socialShareText'],
                    "factCheckedBy": DEFAULT_FACT_CHECKED_BY,
                    "editorReviewedBy": DEFAULT_EDITOR_REVIEWED_BY,
                    "contentType": data['contentType'],
                    "difficultyLevel": data['difficultyLevel'],
                    "featured": False,
                    "thumbnailImageUrl": thumbnail_url,
                    "videoUrl": None,
                    "audioUrl": None,
                    "targetAudience": data['targetAudience'],
                    "language": DEFAULT_LANGUAGE,
                    "viewsCount": DEFAULT_VIEWS_COUNT,
                    "sharesCount": DEFAULT_SHARES_COUNT,
                    "commentsCount": DEFAULT_COMMENTS_COUNT,
                    "averageRating": DEFAULT_AVERAGE_RATING,
                    "inlineImages": inline_images_list,
                    "keyTakeaways": data.get('keyTakeaways', []),
                    "socialMediaHashtags": data.get('socialMediaHashtags', []),
                    "callToActionText": data.get('callToActionText', ''),
                    "structuredData": data.get('structuredData', ""),
                    "sourceKeyword": keyword,
                    "relatedTopics": data.get('relatedTopics', []),
                    "generationMethod": "keyword_based" if not searches else "trend_based",
                    "region": region
                }
                
                # Apply AI categorization to the complete article
                try:
                    ai_result = categorize_with_ai(article, use_ai=True)
                    article['category'] = ai_result['category']
                    print(f"� Applied AI categorization: {ai_result['category']} (confidence: {ai_result['confidence']:.2f}, method: {ai_result['method']})")
                except Exception as e:
                    # Fallback to simple normalization
                    article['category'] = normalize_category(article['category'])
                    print(f"⚠️  Fell back to simple categorization: {e}")
                
                # Backup generated images immediately
                image_files = []
                if os.path.exists(og_img_fp):
                    image_files.append(og_img_fp)
                if os.path.exists(thumb_img_fp):
                    image_files.append(thumb_img_fp)
                for i in range(len(inline_image_descs)):
                    inline_fp = os.path.join(IMAGES_BASE_DIR, slug, f"inline_{i+1}.webp")
                    if os.path.exists(inline_fp):
                        image_files.append(inline_fp)
                
                if image_files:
                    backup_images(slug, image_files)
                
                print(f"✅ Generated: '{data['title']}' ({word_count} words)")
                return article
                
        except Exception as e:
            print(f"❌ Error generating article for '{keyword}': {str(e)}")
            return None

# === HIGH-LEVEL OPERATIONS ===

async def generate_articles_from_trends(manager: SuperArticleManager, top_n: int = 3) -> None:
    """Generate articles from trending keywords"""
    print("🔥 Starting trend-based article generation...")
    
    generator = ArticleGenerator(manager)
    article_id_counter = manager.get_next_article_id()
    
    # Get trending keywords
    keywords = get_top_region_keywords(top_n=top_n)
    if not keywords:
        print("❌ No trending keywords found!")
        return
    
    print(f"📊 Found {len(keywords)} trending keywords")
    
    # Filter already processed keywords
    keywords_to_process = []
    for region, keyword, searches in keywords:
        if keyword in manager.processed_keywords:
            print(f"⏭️  SKIP: '{keyword}' already processed")
            continue
        keywords_to_process.append((region, keyword, searches))
    
    if not keywords_to_process:
        print("ℹ️  No new trending keywords to process!")
        return
    
    # Generate articles
    tasks = []
    async with aiohttp.ClientSession() as session:
        for region, keyword, searches in keywords_to_process:
            # Convert 2-letter region code to full region name
            full_region_name = map_region_code_to_full_name(region)
            task = generator.generate_article_from_keyword(
                session, keyword, full_region_name, article_id_counter, "", searches
            )
            tasks.append(task)
            article_id_counter += 1
        
        print("⏳ Generating articles... This may take a few minutes.")
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_articles = 0
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Task failed with exception: {result}")
            continue
            
        if result:
            slug = result["slug"]
            if slug in manager.articles_map:
                manager.articles_map[slug].update(result)
                print(f"🔄 Updated: {result['title']}")
            else:
                manager.articles_map[slug] = result
                manager.articles.append(result)
                print(f"✨ Added: {result['title']}")
            successful_articles += 1
    
    manager.stats['articles_generated'] = successful_articles
    print(f"🎉 Success! Generated {successful_articles} articles from trends.")

async def generate_articles_from_trends_per_region(manager: SuperArticleManager, top_n: int = 3, target_regions: List[str] = None) -> None:
    """Generate articles from top trending keywords of each region separately"""
    print("🌍 Starting per-region trend-based article generation...")
    
    generator = ArticleGenerator(manager)
    article_id_counter = manager.get_next_article_id()
    
    # Get ALL trending keywords
    all_keywords = get_top_region_keywords(top_n=1000)  # Get many to separate by region
    if not all_keywords:
        print("❌ No trending keywords found!")
        return
    
    # Group keywords by region
    keywords_by_region = {}
    for region, keyword, searches in all_keywords:
        if region not in keywords_by_region:
            keywords_by_region[region] = []
        keywords_by_region[region].append((keyword, searches))
    
    print(f"📊 Found keywords from {len(keywords_by_region)} regions")
    
    # Get top N keywords from each region
    keywords_to_process = []
    for region, region_keywords in keywords_by_region.items():
        # Sort by searches and take top N for this region
        region_keywords.sort(key=lambda x: x[1], reverse=True)
        top_keywords = region_keywords[:top_n]
        
        print(f"🎯 {region} Region - Top {len(top_keywords)} keywords:")
        for keyword, searches in top_keywords:
            if keyword in manager.processed_keywords:
                print(f"   ⏭️  SKIP: '{keyword}' already processed")
                continue
            print(f"   • {keyword} ({searches:,} searches)")
            
            # Use target regions if specified, otherwise use original region
            if target_regions:
                for target_region in target_regions:
                    keywords_to_process.append((target_region, keyword, searches))
            else:
                keywords_to_process.append((region, keyword, searches))
    
    if not keywords_to_process:
        print("ℹ️  No new trending keywords to process!")
        return
    
    total_regions = len(target_regions) if target_regions else len(keywords_by_region)
    unique_keywords = len(set(k[1] for k in keywords_to_process))
    print(f"📝 Will generate {len(keywords_to_process)} articles ({total_regions} regions × {unique_keywords} unique keywords)")
    
    # Generate articles
    tasks = []
    async with aiohttp.ClientSession() as session:
        for region, keyword, searches in keywords_to_process:
            # Convert 2-letter region code to full region name
            full_region_name = map_region_code_to_full_name(region)
            task = generator.generate_article_from_keyword(
                session, keyword, full_region_name, article_id_counter, "", searches
            )
            tasks.append(task)
            article_id_counter += 1
        
        print("⏳ Generating articles... This may take a few minutes.")
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_articles = 0
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Task failed with exception: {result}")
            continue
            
        if result:
            slug = result["slug"]
            if slug in manager.articles_map:
                manager.articles_map[slug].update(result)
                print(f"🔄 Updated: {result['title']}")
            else:
                manager.articles_map[slug] = result
                manager.articles.append(result)
                print(f"✨ Added: {result['title']}")
            successful_articles += 1
    
    manager.stats['articles_generated'] = successful_articles
    print(f"🎉 Success! Generated {successful_articles} articles from top keywords per region.")

async def generate_articles_from_trends_multi_region(manager: SuperArticleManager, top_n: int = 3, target_regions: List[str] = None) -> None:
    """Generate articles from trending keywords for multiple target regions"""
    print("🌍 Starting multi-region trend-based article generation...")
    
    generator = ArticleGenerator(manager)
    article_id_counter = manager.get_next_article_id()
    
    # Get trending keywords
    keywords = get_top_region_keywords(top_n=top_n)
    if not keywords:
        print("❌ No trending keywords found!")
        return
    
    print(f"📊 Found {len(keywords)} trending keywords")
    
    # If no target regions specified, use original regions (fallback to existing behavior)
    if not target_regions:
        print("ℹ️  No target regions specified, using original keyword regions")
        await generate_articles_from_trends(manager, top_n)
        return
    
    print(f"🎯 Target regions: {', '.join(target_regions)}")
    
    # Filter already processed keywords and create combinations with target regions
    keywords_to_process = []
    for _, keyword, searches in keywords:
        if keyword in manager.processed_keywords:
            print(f"⏭️  SKIP: '{keyword}' already processed")
            continue
        
        # Generate articles for this keyword in each target region
        for target_region in target_regions:
            keywords_to_process.append((target_region, keyword, searches))
    
    if not keywords_to_process:
        print("ℹ️  No new trending keywords to process!")
        return
    
    print(f"📝 Will generate {len(keywords_to_process)} articles ({len(target_regions)} regions × {len(set(k[1] for k in keywords_to_process))} unique keywords)")
    
    # Generate articles
    tasks = []
    async with aiohttp.ClientSession() as session:
        for region, keyword, searches in keywords_to_process:
            # Convert 2-letter region code to full region name
            full_region_name = map_region_code_to_full_name(region)
            task = generator.generate_article_from_keyword(
                session, keyword, full_region_name, article_id_counter, "", searches
            )
            tasks.append(task)
            article_id_counter += 1
        
        print("⏳ Generating articles... This may take a few minutes.")
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_articles = 0
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Task failed with exception: {result}")
            continue
            
        if result:
            slug = result["slug"]
            if slug in manager.articles_map:
                manager.articles_map[slug].update(result)
                print(f"🔄 Updated: {result['title']}")
            else:
                manager.articles_map[slug] = result
                manager.articles.append(result)
                print(f"✨ Added: {result['title']}")
            successful_articles += 1
    
    manager.stats['articles_generated'] = successful_articles
    print(f"🎉 Success! Generated {successful_articles} articles from trends across {len(target_regions)} regions.")

async def generate_articles_from_keywords(manager: SuperArticleManager, keywords: List[str], 
                                        region: str = "India", custom_prompt: str = "", 
                                        skip_existing: bool = True) -> None:
    """Generate articles from specific keywords"""
    print(f"🎯 Starting keyword-based article generation...")
    print(f"📍 Target region: {region}")
    print(f"🎯 Keywords: {', '.join(keywords)}")
    
    generator = ArticleGenerator(manager)
    article_id_counter = manager.get_next_article_id()
    
    # Filter keywords
    keywords_to_process = []
    for keyword in validate_keyword_input(keywords):
        if skip_existing and keyword in manager.processed_keywords:
            print(f"⏭️  SKIP: '{keyword}' already processed")
            continue
        keywords_to_process.append(keyword)
    
    if not keywords_to_process:
        print("ℹ️  No new keywords to process!")
        return
    
    print(f"📝 Processing {len(keywords_to_process)} keywords...")
    
    # Generate articles
    tasks = []
    async with aiohttp.ClientSession() as session:
        for keyword in keywords_to_process:
            # Ensure region is in full name format
            full_region_name = map_region_code_to_full_name(region)
            task = generator.generate_article_from_keyword(
                session, keyword, full_region_name, article_id_counter, custom_prompt
            )
            tasks.append(task)
            article_id_counter += 1
        
        print("⏳ Generating articles... This may take a few minutes.")
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful_articles = 0
    for result in results:
        if isinstance(result, Exception):
            print(f"❌ Task failed with exception: {result}")
            continue
            
        if result:
            slug = result["slug"]
            if slug in manager.articles_map:
                manager.articles_map[slug].update(result)
                print(f"🔄 Updated: {result['title']}")
            else:
                manager.articles_map[slug] = result
                manager.articles.append(result)
                print(f"✨ Added: {result['title']}")
            successful_articles += 1
    
    manager.stats['articles_generated'] += successful_articles
    print(f"🎉 Success! Generated {successful_articles} articles.")

def load_keyword_config(config_file: str = "keyword_config.json") -> Optional[Dict]:
    """Load keyword configuration from JSON file"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Configuration file '{config_file}' not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing configuration file: {e}")
        return None

async def process_keyword_batches(manager: SuperArticleManager, batch_names: List[str] = None,
                                config_file: str = "keyword_config.json") -> None:
    """Process predefined keyword batches"""
    config = load_keyword_config(config_file)
    if not config:
        return
    
    settings = config.get("default_settings", {})
    region = settings.get("region", "India")
    max_batch = settings.get("max_articles_per_batch", 10)
    
    if not batch_names:
        # Show available batches
        print("\n📦 Available keyword batches:")
        print("-" * 40)
        for category, keywords in config["keyword_batches"].items():
            print(f"🏷️  {category.upper()}: {len(keywords)} keywords")
            print(f"   Keywords: {', '.join(keywords[:3])}{'...' if len(keywords) > 3 else ''}")
        print()
        return
    
    for batch_name in batch_names:
        if batch_name not in config["keyword_batches"]:
            print(f"❌ Batch '{batch_name}' not found in configuration")
            continue
        
        keywords = config["keyword_batches"][batch_name]
        
        # Limit batch size
        if len(keywords) > max_batch:
            keywords = keywords[:max_batch]
            print(f"⚠️  Limited batch '{batch_name}' to {max_batch} keywords")
        
        print(f"\n🚀 Processing batch: {batch_name.upper()}")
        print(f"📊 Keywords: {len(keywords)}")
        print(f"🌍 Region: {region}")
        
        custom_prompt = config.get("custom_prompts", {}).get(batch_name, "")
        
        await generate_articles_from_keywords(manager, keywords, region, custom_prompt, True)

def interactive_keyword_input() -> Tuple[List[str], str, str]:
    """Interactive mode for keyword input"""
    print("\n🎯 Interactive Keyword Input Mode")
    print("=" * 40)
    
    keywords = []
    print("Enter keywords (press Enter with empty input to finish):")
    
    while True:
        keyword = input(f"Keyword {len(keywords) + 1}: ").strip()
        if not keyword:
            break
        keywords.append(keyword)
    
    if not keywords:
        print("❌ No keywords entered!")
        return [], "", ""
    
    region = input(f"Target region (default: India): ").strip() or "India"
    custom_prompt = input("Custom instructions (optional): ").strip()
    
    return keywords, region, custom_prompt

async def generate_images_for_articles(manager: SuperArticleManager, specific_articles: List[str] = None, 
                                     regenerate: bool = False, image_types: List[str] = ['all']) -> None:
    """Generate images for existing articles"""
    print("🖼️  Starting image generation for existing articles...")
    
    if not manager.articles:
        print("❌ No articles found to generate images for!")
        return
    
    # Filter articles
    articles_to_process = []
    if specific_articles:
        # Generate for specific articles by slug
        for slug in specific_articles:
            article = manager.articles_map.get(slug)
            if article:
                articles_to_process.append(article)
            else:
                print(f"❌ Article with slug '{slug}' not found")
    else:
        # Process all articles
        articles_to_process = manager.articles
    
    if not articles_to_process:
        print("❌ No articles to process!")
        return
    
    print(f"📊 Processing {len(articles_to_process)} articles")
    
    images_generated = 0
    for i, article in enumerate(articles_to_process, 1):
        slug = article.get('slug')
        title = article.get('title', 'Untitled')
        
        if not slug:
            print(f"⏭️  SKIP: Article {i} - no slug")
            continue
        
        print(f"\n📸 [{i}/{len(articles_to_process)}] Processing: {title[:50]}...")
        
        # Create images directory
        article_images_dir = os.path.join(IMAGES_BASE_DIR, slug)
        os.makedirs(article_images_dir, exist_ok=True)
        
        # Track what images we generate
        generated_files = []
        
        # Generate main image
        if 'all' in image_types or 'main' in image_types:
            main_img_path = os.path.join(article_images_dir, "main.webp")
            if regenerate or not os.path.exists(main_img_path):
                og_title = article.get('ogTitle', title)
                image_alt = article.get('imageAltText', f'News image for {title}')
                
                main_prompt = f"Professional news article image for: {og_title}. Visual style: {image_alt}. High quality, news-appropriate. It is very important not to have any garbled text in the images. Only one image. No text overlays."
                main_image_url = generateImage(main_prompt, main_img_path)
                
                if main_image_url and os.path.exists(main_img_path):
                    # Update article with new image URL
                    article['ogImage'] = main_image_url
                    generated_files.append(main_img_path)
                    print(f"   ✅ Generated main image")
                else:
                    print(f"   ❌ Failed to generate main image")
            else:
                print(f"   ⏭️  Main image already exists")
        
        # Generate thumbnail image
        if 'all' in image_types or 'thumbnail' in image_types:
            thumb_img_path = os.path.join(article_images_dir, "thumb.webp")
            if regenerate or not os.path.exists(thumb_img_path):
                og_title = article.get('ogTitle', title)
                
                thumb_prompt = f"Thumbnail for news article: {og_title}. Compact, visually appealing, news-style thumbnail. It is very important not to have any garbled text in the images. Only one image. No text overlays."
                thumb_image_url = generateImage(thumb_prompt, thumb_img_path)
                
                if thumb_image_url and os.path.exists(thumb_img_path):
                    # Update article with new thumbnail URL
                    article['thumbnailImageUrl'] = thumb_image_url
                    generated_files.append(thumb_img_path)
                    print(f"   ✅ Generated thumbnail image")
                else:
                    print(f"   ❌ Failed to generate thumbnail image")
            else:
                print(f"   ⏭️  Thumbnail image already exists")
        
        # Generate inline images
        if 'all' in image_types or 'inline' in image_types:
            inline_images = article.get('inlineImages', [])
            if not inline_images:
                # Try to create some inline images based on content
                content = article.get('content', '')
                if content and len(content) > 1000:  # Only for substantial articles
                    # Create 2-3 inline images
                    inline_descriptions = [
                        {'description': f'Supporting illustration for {title}', 'caption': 'Related news illustration'},
                        {'description': f'Visual context for {title}', 'caption': 'News context image'}
                    ]
                    article['inlineImages'] = []
                else:
                    inline_descriptions = []
            else:
                # Use existing inline image descriptions
                inline_descriptions = [
                    {'description': img.get('alt', f'Inline image for {title}'), 
                     'caption': img.get('caption', 'Article illustration')}
                    for img in inline_images
                ]
            
            for j, img_desc in enumerate(inline_descriptions):
                inline_img_path = os.path.join(article_images_dir, f"inline_{j+1}.webp")
                if regenerate or not os.path.exists(inline_img_path):
                    inline_prompt = f"Supporting image for article: {img_desc['description']}. Caption context: {img_desc['caption']}. Professional, high-quality news illustration. It is very important not to have any garbled text in the images. Only one image. No text overlays."
                    inline_image_url = generateImage(inline_prompt, inline_img_path)
                    
                    if inline_image_url and os.path.exists(inline_img_path):
                        # Update or add to inline images
                        if j < len(article.get('inlineImages', [])):
                            article['inlineImages'][j]['url'] = inline_image_url
                        else:
                            if 'inlineImages' not in article:
                                article['inlineImages'] = []
                            article['inlineImages'].append({
                                'url': inline_image_url,
                                'alt': img_desc['description'],
                                'caption': img_desc['caption'],
                                'placementHint': f'after paragraph {j+2}'
                            })
                        generated_files.append(inline_img_path)
                        print(f"   ✅ Generated inline image {j+1}")
                    else:
                        print(f"   ❌ Failed to generate inline image {j+1}")
                else:
                    print(f"   ⏭️  Inline image {j+1} already exists")
        
        # Backup generated images
        if generated_files:
            backup_images(slug, generated_files)
            images_generated += len(generated_files)
            print(f"   💾 Backed up {len(generated_files)} images")
    
    # Save updated articles with new image URLs
    if images_generated > 0:
        manager.save_articles()
        print(f"\n🎉 Generated {images_generated} images for articles!")
    else:
        print(f"\nℹ️  No new images generated")

# === COMMAND-LINE INTERFACE ===

def create_parser() -> argparse.ArgumentParser:
    """Create command-line argument parser"""
    parser = argparse.ArgumentParser(
        description="Super-Consolidated Article Management System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate trends --count 5
  %(prog)s generate keywords "AI technology" "machine learning"
  %(prog)s generate batch technology health
  %(prog)s generate interactive
  %(prog)s enhance --deduplicate --fix-issues
  %(prog)s stats
  %(prog)s workflow --complete
  %(prog)s backup --images
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Management operations')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate new articles')
    gen_subparsers = gen_parser.add_subparsers(dest='gen_mode', help='Generation modes')
    
    # Generate -> Trends
    trends_parser = gen_subparsers.add_parser('trends', help='Generate from trending keywords')
    trends_parser.add_argument('--count', '-c', type=int, default=3,
                              help='Number of trending keywords to process (default: 3)')
    trends_parser.add_argument('--regions', nargs='*', 
                              help='Target regions for articles (e.g., India USA UK). If not specified, uses original keyword regions')
    trends_parser.add_argument('--per-region', action='store_true',
                              help='Get top N keywords from each region separately instead of global top N')
    
    # Generate -> Keywords
    keywords_parser = gen_subparsers.add_parser('keywords', help='Generate from specific keywords')
    keywords_parser.add_argument('keywords', nargs='+', help='Keywords to generate articles for')
    keywords_parser.add_argument('--region', '-r', default='India',
                                help='Target region (default: India)')
    keywords_parser.add_argument('--prompt', '-p', default='',
                                help='Custom prompt additions')
    keywords_parser.add_argument('--no-skip', action='store_true',
                                help='Generate even if keyword already processed')
    
    # Generate -> Batch
    batch_parser = gen_subparsers.add_parser('batch', help='Process keyword batches')
    batch_parser.add_argument('batches', nargs='*', 
                             help='Batch names to process (empty to list available)')
    batch_parser.add_argument('--config', '-c', default='keyword_config.json',
                             help='Configuration file (default: keyword_config.json)')
    
    # Generate -> Interactive
    interactive_parser = gen_subparsers.add_parser('interactive', help='Interactive keyword input')
    
    # Enhance command
    enhance_parser = subparsers.add_parser('enhance', help='Enhance existing articles')
    enhance_parser.add_argument('--deduplicate', action='store_true',
                               help='Remove duplicate articles')
    enhance_parser.add_argument('--fix-issues', action='store_true',
                               help='Fix article issues (IDs, titles, etc.)')
    enhance_parser.add_argument('--merge-legacy', action='store_true',
                               help='Merge articles from legacy articles.json')
    enhance_parser.add_argument('--headers-only', action='store_true',
                               help='Enhance headers with keywords (fast, no infographics)')
    enhance_parser.add_argument('--all', action='store_true',
                               help='Run all enhancement operations')
    enhance_parser.add_argument('--max-articles', type=int,
                               help='Maximum number of articles to process (for testing)')
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Complete workflow operations')
    workflow_parser.add_argument('--complete', action='store_true',
                                help='Run complete analysis and optimization workflow')
    workflow_parser.add_argument('--generate-first', action='store_true',
                                help='Generate articles first, then optimize')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show article statistics')
    
    # Images command
    images_parser = subparsers.add_parser('images', help='Generate images for existing articles')
    images_parser.add_argument('--regenerate', action='store_true',
                              help='Regenerate images even if they already exist')
    images_parser.add_argument('--missing-only', action='store_true',
                              help='Only generate images for articles missing them (default)')
    images_parser.add_argument('--articles', nargs='*',
                              help='Specific article slugs to generate images for (space-separated)')
    images_parser.add_argument('--type', choices=['main', 'thumbnail', 'inline', 'all'], default='all',
                              help='Type of images to generate (default: all)')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Backup operations')
    backup_parser.add_argument('--images', action='store_true',
                              help='Backup all article images to local directory')
    
    # AI Categorization command
    ai_parser = subparsers.add_parser('categorize', help='AI-powered article categorization')
    ai_subparsers = ai_parser.add_subparsers(dest='ai_mode', help='Categorization operations')
    
    # Categorize -> Test
    test_parser = ai_subparsers.add_parser('test', help='Test categorization on sample articles')
    test_parser.add_argument('--count', '-c', type=int, default=10,
                            help='Number of articles to test (default: 10)')
    
    # Categorize -> All
    all_parser = ai_subparsers.add_parser('all', help='Recategorize all articles using AI')
    all_parser.add_argument('--max-ai', type=int, default=100,
                           help='Maximum AI calls to make (default: 100)')
    all_parser.add_argument('--force', action='store_true',
                           help='Force recategorization even if already categorized')
    
    # Categorize -> Stats
    stats_ai_parser = ai_subparsers.add_parser('stats', help='Show categorization statistics')
    
    # Common arguments
    for p in [gen_parser, enhance_parser, workflow_parser, stats_parser, images_parser, backup_parser, ai_parser]:
        p.add_argument('--file', '-f', default=DEFAULT_ARTICLES_FILE,
                      help='Articles file to use')
        p.add_argument('--no-backup', action='store_true',
                      help='Skip creating backups')
    
    return parser

async def main():
    """Main entry point"""
    load_dotenv()
    
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🚀 Super-Consolidated Article Management System")
    print("=" * 60)
    
    # Initialize manager
    manager = SuperArticleManager(args.file)
    manager.load_articles()
    
    # Create backup unless disabled
    if not getattr(args, 'no_backup', False):
        manager.create_backup("operation")
    
    try:
        if args.command == 'generate':
            if not args.gen_mode:
                print("❌ Please specify a generation mode. Use --help for options.")
                return
                
            if args.gen_mode == 'trends':
                if args.per_region:
                    await generate_articles_from_trends_per_region(manager, args.count, args.regions)
                elif args.regions:
                    await generate_articles_from_trends_multi_region(manager, args.count, args.regions)
                else:
                    await generate_articles_from_trends(manager, args.count)
                
            elif args.gen_mode == 'keywords':
                await generate_articles_from_keywords(
                    manager, args.keywords, args.region, args.prompt, not args.no_skip
                )
                
            elif args.gen_mode == 'batch':
                await process_keyword_batches(
                    manager, args.batches if args.batches else None, args.config
                )
                
            elif args.gen_mode == 'interactive':
                keywords, region, custom_prompt = interactive_keyword_input()
                if keywords:
                    await generate_articles_from_keywords(
                        manager, keywords, region, custom_prompt, True
                    )
            
            # Save after generation
            manager.save_articles()
        
        elif args.command == 'enhance':
            operations_run = []
            
            if args.all or args.merge_legacy:
                merged = manager.merge_legacy_articles()
                if merged > 0:
                    operations_run.append(f"Merged {merged} legacy articles")
            
            if args.all or args.deduplicate:
                duplicates = manager.analyze_duplicates()
                removed = manager.deduplicate_articles(duplicates)
                if removed > 0:
                    operations_run.append(f"Removed {removed} duplicates")
            
            if args.all or args.fix_issues:
                fixed = manager.fix_article_issues()
                if fixed > 0:
                    operations_run.append(f"Fixed {fixed} articles")
            
            # Header enhancement with keywords (fast, cost-effective)
            if args.headers_only:
                try:
                    from enhance_existing_headers import ExistingArticleHeaderEnhancer
                    
                    enhancer = ExistingArticleHeaderEnhancer(manager.articles_file)
                    results = enhancer.enhance_all_articles(
                        max_articles=args.max_articles,
                        backup=True
                    )
                    
                    if results.get('success') and results.get('enhanced_count', 0) > 0:
                        enhanced_count = results.get('enhanced_count', 0)
                        operations_run.append(f"Enhanced headers for {enhanced_count} articles")
                        # Reload articles after header enhancement
                        manager.load_articles()
                    elif results.get('success'):
                        print("ℹ️  No articles needed header enhancement")
                    else:
                        print(f"❌ Header enhancement failed: {results.get('error', 'Unknown error')}")
                        
                except ImportError:
                    print("❌ Header enhancement module not found. Please ensure enhance_existing_headers.py exists.")
                except Exception as e:
                    print(f"❌ Error during header enhancement: {e}")
            
            # Full enhancement (with infographics) - only if not headers-only
            elif args.all or (not args.headers_only and not args.merge_legacy and not args.deduplicate and not args.fix_issues):
                enhanced = manager.enhance_articles()
                if enhanced > 0:
                    operations_run.append(f"Enhanced {enhanced} articles")
            
            if operations_run:
                manager.save_articles()
                print(f"\n✅ Operations completed: {', '.join(operations_run)}")
            else:
                print("ℹ️  No enhancements needed")
        
        elif args.command == 'workflow':
            if args.complete:
                manager.print_header("COMPLETE WORKFLOW", "=")
                
                # Step 1: Merge legacy if exists
                manager.merge_legacy_articles()
                
                # Step 2: Analyze and deduplicate
                duplicates = manager.analyze_duplicates()
                if any(duplicates.values()):
                    manager.deduplicate_articles(duplicates)
                
                # Step 3: Fix issues and enhance
                manager.fix_article_issues()
                manager.enhance_articles()
                
                # Step 4: Save results
                manager.save_articles()
                
                print("\n🎉 Complete workflow finished!")
            
            elif args.generate_first:
                manager.print_header("GENERATE-FIRST WORKFLOW", "=")
                
                # Generate from trends first
                await generate_articles_from_trends(manager, 3)
                
                # Then run complete workflow
                duplicates = manager.analyze_duplicates()
                if any(duplicates.values()):
                    manager.deduplicate_articles(duplicates)
                
                manager.fix_article_issues()
                manager.enhance_articles()
                manager.save_articles()
                
                print("\n🎉 Generate-first workflow finished!")
        
        elif args.command == 'stats':
            manager.show_statistics()
        
        elif args.command == 'images':
            # Determine image types to generate
            if args.type == 'all':
                image_types = ['main', 'thumbnail', 'inline']
            else:
                image_types = [args.type]
            
            # Generate images
            await generate_images_for_articles(
                manager, 
                args.articles, 
                args.regenerate,
                image_types
            )
        
        elif args.command == 'backup':
            if args.images:
                backup_all_article_images(manager.articles)
            else:
                print("❌ Please specify what to backup. Use --images to backup all article images.")
                print("   Example: python super_article_manager.py backup --images")
        
        elif args.command == 'categorize':
            if not args.ai_mode:
                print("❌ Please specify a categorization operation. Use --help for options.")
                return
            
            categorizer = get_ai_categorizer()
            
            if args.ai_mode == 'test':
                print(f"\n� Testing AI Categorization on {args.count} Articles")
                print("=" * 50)
                
                # Test on a sample of articles
                test_articles = manager.articles[:args.count]
                results = categorizer.batch_categorize(test_articles, use_ai=True, max_ai_calls=args.count)
                
                # Show results summary
                changed_count = sum(1 for r in results if r['changed'])
                print(f"\n📊 Test Results:")
                print(f"   Articles tested: {len(results)}")
                print(f"   Categories changed: {changed_count}")
                print(f"   Average confidence: {sum(r['confidence'] for r in results) / len(results):.2f}")
                
                # Show some examples
                print(f"\n� Sample Changes:")
                changes = [r for r in results if r['changed']][:5]
                for change in changes:
                    title = change['article'].get('title', 'Untitled')[:40]
                    print(f"   • {title}...")
                    print(f"     {change['original_category']} → {change['ai_category']} (confidence: {change['confidence']:.2f})")
                
                # Don't save changes for test mode
                print(f"\nℹ️  Test mode - changes not saved. Use 'categorize all' to apply changes.")
            
            elif args.ai_mode == 'all':
                print(f"\n🤖 Recategorizing All Articles with AI")
                print("=" * 40)
                
                if not args.force:
                    print("⚠️  This will recategorize all articles. Use --force to confirm.")
                    return
                
                # Batch categorize all articles
                results = categorizer.batch_categorize(
                    manager.articles, 
                    use_ai=True, 
                    max_ai_calls=args.max_ai
                )
                
                # Show results summary
                changed_count = sum(1 for r in results if r['changed'])
                print(f"\n📊 Final Results:")
                print(f"   Total articles: {len(results)}")
                print(f"   Categories changed: {changed_count}")
                print(f"   AI calls made: {min(args.max_ai, len([r for r in results if r['method'] == 'ai_analysis']))}")
                
                # Save the changes
                if changed_count > 0:
                    manager.save_articles()
                    print(f"💾 Saved {changed_count} category changes")
            
            elif args.ai_mode == 'stats':
                print(f"\n📊 AI Categorization Statistics")
                print("=" * 40)
                
                # Count categories
                category_counts = {}
                for article in manager.articles:
                    category = article.get('category', 'Unknown')
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                print(f"📁 Category Distribution:")
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {category}: {count} articles")
                
                print(f"\n🎯 Available Categories: {', '.join(categorizer.categories)}")
                print(f"📝 Total Articles: {len(manager.articles)}")
        
        elif args.command == 'intelligence':
            print("❌ Intelligence command has been replaced with 'categorize'")
            print("📝 Available commands:")
            print("   • python super_article_manager.py categorize test --count 10")
            print("   • python super_article_manager.py categorize all --force --max-ai 100")
            print("   • python super_article_manager.py categorize stats")
    
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
