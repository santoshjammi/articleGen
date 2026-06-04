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
DEFAULT_LANGUAGE = "en-IN"
DEFAULT_SCHEMA_TYPE = "NewsArticle"
DEFAULT_FACT_CHECKED_BY = "AI Content Review"
DEFAULT_EDITOR_REVIEWED_BY = "AI Editor"

# Named author personas for E-E-A-T signals (rotated by article hash)
_AUTHOR_PERSONAS = [
    {
        "name": "Aryan Mehta",
        "title": "Senior Technology Analyst",
        "bio": "Aryan Mehta is a Senior Technology Analyst at Country's News with 8 years of experience covering AI infrastructure, cloud computing, and enterprise software. Previously at Economic Times Tech and TechCircle.",
        "expertise": ["AI Infrastructure", "Enterprise Transformation"],
    },
    {
        "name": "Priya Nair",
        "title": "Mobility & Sustainability Editor",
        "bio": "Priya Nair leads mobility and sustainability coverage at Country's News. She tracks EV ecosystems, battery supply chains, and green logistics across Asia and Europe.",
        "expertise": ["Smart Mobility"],
    },
    {
        "name": "Rohan Desai",
        "title": "India Digital Economy Correspondent",
        "bio": "Rohan Desai covers India's digital economy transformation — from ONDC and UPI to smart city initiatives and government AI programmes. Based in Bengaluru.",
        "expertise": ["India Digital Transformation", "Enterprise Transformation"],
    },
]

def _pick_author(keyword: str, category: str) -> dict:
    """Pick an author persona based on category and keyword hash for consistency."""
    cat_map = {
        "AI Infrastructure": 0,
        "Enterprise Transformation": 0,
        "Smart Mobility": 1,
        "India Digital Transformation": 2,
    }
    idx = cat_map.get(category, hash(keyword) % len(_AUTHOR_PERSONAS))
    return _AUTHOR_PERSONAS[idx]

DEFAULT_AUTHOR = _AUTHOR_PERSONAS[0]["name"]  # fallback

# === AI CATEGORIZATION CLASSES ===

# The four editorial pillars of Country's News intelligence platform
EDITORIAL_PILLARS = [
    'AI Infrastructure',
    'Enterprise Transformation',
    'Smart Mobility',
    'India Digital Transformation',
]

class AICategorizer:
    """Keyword-based categoriser aligned to the four editorial pillars"""

    def __init__(self):
        self.categories = EDITORIAL_PILLARS

        self.keyword_patterns = {
            'AI Infrastructure': [
                'local llm', 'inference', 'ai agent', 'gpu', 'llm', 'language model',
                'nvidia', 'ai chip', 'ai hardware', 'model training', 'fine-tuning',
                'quantization', 'ollama', 'vllm', 'hugging face', 'ai workflow',
                'coding automation', 'cursor', 'github copilot', 'ai coding',
                'orchestration', 'langchain', 'rag', 'retrieval augmented',
                'vector database', 'embedding', 'ai infrastructure', 'compute',
                'model deployment', 'ai ops', 'mlops', 'foundation model', 'gemini',
                'claude', 'openai', 'mistral', 'llama', 'ai stack', 'ai tooling',
            ],

            'Enterprise Transformation': [
                'enterprise ai', 'ai adoption', 'erp', 'sap', 'salesforce', 'workday',
                'ai copilot', 'enterprise software', 'saas', 'automation', 'workflow',
                'productivity', 'digital transformation', 'ai strategy', 'ai-native',
                'b2b', 'enterprise', 'business automation', 'rpa', 'process automation',
                'microsoft 365', 'slack ai', 'notion ai', 'zapier', 'make.com',
                'ai integration', 'enterprise adoption', 'cost reduction', 'operational',
                'ai roi', 'workforce automation', 'knowledge management', 'ai tool',
                'business intelligence', 'data analytics', 'cloud migration',
            ],

            'Smart Mobility': [
                'ev', 'electric vehicle', 'electric car', 'battery', 'charging station',
                'charging network', 'tata ev', 'ola electric', 'ather', 'hyundai ev',
                'tesla', 'byd', 'ev fleet', 'fleet intelligence', 'autonomous vehicle',
                'self-driving', 'ai driving', 'logistics automation', 'smart logistics',
                'supply chain', 'ev infrastructure', 'mobility', 'transport tech',
                'manufacturing automation', 'robotics', 'industrial ai', 'smart factory',
                'industry 4.0', 'ev adoption', 'range anxiety', 'battery swap',
                'green mobility', 'sustainable transport', 'lidar', 'v2g',
            ],

            'India Digital Transformation': [
                'india', 'indian', 'ondc', 'upi', 'aadhaar', 'digiyatra', 'niti aayog',
                'india stack', 'bharat net', 'digital india', 'startup india',
                'make in india', 'india ai mission', 'reliance jio', 'tata', 'infosys',
                'wipro', 'hcl', 'tech mahindra', 'indian startup', 'bangalore',
                'hyderabad', 'smart city', 'government ai', 'india fintech',
                'rupee digital', 'cbdc india', 'india ecommerce', 'meesho', 'flipkart',
                'india cloud', 'aws india', 'azure india', 'india manufacturing',
                'pli scheme', 'semiconductor india', 'india gig economy',
            ],
        }

    def categorize_article(self, article: Dict, use_ai: bool = True) -> Dict:
        """Categorize article into one of the four editorial pillars"""
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()[:2000]  # cap for speed
        keywords = [k.lower() for k in article.get('keywords', [])]
        text = f"{title} {title} {' '.join(keywords)} {content}"  # title weighted ×2

        category_scores = {}
        for category, patterns in self.keyword_patterns.items():
            score = 0
            for pattern in patterns:
                count = text.count(pattern.lower())
                weight = len(pattern.split())
                score += count * weight
            category_scores[category] = score

        if category_scores and max(category_scores.values()) > 0:
            best_category = max(category_scores, key=category_scores.get)
            max_score = category_scores[best_category]
            total_score = sum(category_scores.values())
            confidence = min(max_score / total_score if total_score > 0 else 0, 1.0)
        else:
            best_category = 'India Digital Transformation'  # default fallback
            confidence = 0.3

        return {
            'category': best_category,
            'confidence': confidence,
            'method': 'pillar_keyword_analysis',
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
                print(f"       Original: {article.get('category', 'None')} → Pillar: {result['category']} (confidence: {result['confidence']:.2f})")

            except Exception as e:
                print(f"   ❌ Failed to categorize article {i+1}: {e}")
                results.append({
                    'article': article,
                    'original_category': article.get('category'),
                    'ai_category': article.get('category', 'India Digital Transformation'),
                    'confidence': 0.0,
                    'changed': False,
                    'error': str(e)
                })

        return results

def simple_ai_categorize(title: str, content: str, keywords: List[str] = None) -> str:
    """Quick categorization into one of the four editorial pillars"""
    categorizer = AICategorizer()
    article = {'title': title, 'content': content, 'keywords': keywords or []}
    result = categorizer.categorize_article(article)
    return result['category']

def categorize_with_confidence(article: Dict) -> Tuple[str, float]:
    """Categorize and return confidence score"""
    categorizer = AICategorizer()
    result = categorizer.categorize_article(article)
    return result['category'], result['confidence']

# === CATEGORY NORMALIZATION ===
# Maps any legacy or LLM-produced category string to one of the four editorial pillars
CATEGORY_MAPPING = {
    # Direct pillar names — pass through
    'AI Infrastructure': 'AI Infrastructure',
    'Enterprise Transformation': 'Enterprise Transformation',
    'Smart Mobility': 'Smart Mobility',
    'India Digital Transformation': 'India Digital Transformation',

    # Technology → AI Infrastructure (primary mapping for tech content)
    'Technology': 'AI Infrastructure',
    'Tech': 'AI Infrastructure',
    'Artificial Intelligence': 'AI Infrastructure',
    'Machine Learning': 'AI Infrastructure',
    'Data Science': 'AI Infrastructure',
    'Cloud Computing': 'AI Infrastructure',
    'Cybersecurity': 'Enterprise Transformation',
    'Software Development': 'AI Infrastructure',
    'Emerging Technologies': 'AI Infrastructure',

    # Business / Finance → Enterprise Transformation
    'Business': 'Enterprise Transformation',
    'Finance': 'Enterprise Transformation',
    'Economy': 'Enterprise Transformation',
    'Business & Finance': 'Enterprise Transformation',
    'Business & Economy': 'Enterprise Transformation',
    'Business and Technology': 'Enterprise Transformation',
    'Business & International Relations': 'Enterprise Transformation',
    'Startup': 'Enterprise Transformation',
    'Fintech': 'Enterprise Transformation',
    'E-commerce': 'Enterprise Transformation',
    'SaaS': 'Enterprise Transformation',
    'Digital Marketing': 'Enterprise Transformation',

    # Environment / Energy / Manufacturing → Smart Mobility
    'Environment': 'Smart Mobility',
    'Energy': 'Smart Mobility',
    'Manufacturing': 'Smart Mobility',
    'Automotive': 'Smart Mobility',
    'EV': 'Smart Mobility',
    'Logistics': 'Smart Mobility',
    'Supply Chain': 'Smart Mobility',
    'Robotics': 'Smart Mobility',

    # World / India / Government → India Digital Transformation
    'World': 'India Digital Transformation',
    'News': 'India Digital Transformation',
    'World Affairs': 'India Digital Transformation',
    'Defence': 'India Digital Transformation',
    'Defense': 'India Digital Transformation',
    'Politics': 'India Digital Transformation',
    'Government': 'India Digital Transformation',

    # Out-of-scope legacy categories → nearest pillar
    'Health': 'Enterprise Transformation',
    'Health & Wellness': 'Enterprise Transformation',
    'Sports': 'India Digital Transformation',
    'Entertainment': 'India Digital Transformation',
    'Lifestyle': 'India Digital Transformation',
    'Travel': 'India Digital Transformation',
    'Food & Drink': 'India Digital Transformation',
    'Career Development': 'Enterprise Transformation',
}

# === SUBCATEGORY-TO-PILLAR MAPPING ===
SUBCATEGORY_MAPPING = {
    # AI Infrastructure
    'Agile Certifications': 'Enterprise Transformation',
    'Agile Project Management': 'Enterprise Transformation',
    'Agile Methodologies': 'Enterprise Transformation',
    'Product Management': 'Enterprise Transformation',
    'Emerging Technologies': 'AI Infrastructure',
    'Web Development': 'AI Infrastructure',
    'Artificial Intelligence': 'AI Infrastructure',
    'Software Development': 'AI Infrastructure',
    'Programming': 'AI Infrastructure',
    'DevOps': 'AI Infrastructure',
    'Cloud Computing': 'AI Infrastructure',
    'Cybersecurity': 'Enterprise Transformation',
    'Data Science': 'AI Infrastructure',
    'Machine Learning': 'AI Infrastructure',
    'Tech News': 'AI Infrastructure',
    'Mobile Development': 'AI Infrastructure',
    'API Development': 'AI Infrastructure',
    'Database Management': 'AI Infrastructure',
    'System Administration': 'AI Infrastructure',
    'IT Management': 'Enterprise Transformation',
    'Digital Economy': 'India Digital Transformation',

    # Enterprise Transformation
    'Digital Strategy': 'Enterprise Transformation',
    'Marketing Strategy': 'Enterprise Transformation',
    'Business Strategy': 'Enterprise Transformation',
    'Digital Marketing': 'Enterprise Transformation',
    'International Business': 'Enterprise Transformation',
    'Banking': 'Enterprise Transformation',
    'Recruitment': 'Enterprise Transformation',
    'Stock Market': 'Enterprise Transformation',
    'Stock Analysis': 'Enterprise Transformation',
    'Personal Finance': 'Enterprise Transformation',
    'Retail': 'Enterprise Transformation',
    'Semiconductors': 'AI Infrastructure',
    'Project Management': 'Enterprise Transformation',
    'Business Analytics': 'Enterprise Transformation',
    'E-commerce': 'Enterprise Transformation',
    'Fintech': 'Enterprise Transformation',
    'Entrepreneurship': 'India Digital Transformation',
    'Corporate Strategy': 'Enterprise Transformation',
    'Business Development': 'Enterprise Transformation',
    'Sales': 'Enterprise Transformation',
    'Customer Service': 'Enterprise Transformation',
    'Banking News': 'Enterprise Transformation',
    'Fast Food': 'India Digital Transformation',
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
        return current_category or 'India Digital Transformation'
    
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
    return current_category or 'India Digital Transformation'

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
        fallback_category = normalize_category(article.get("category", "AI Infrastructure"))
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

# === QUALITY SCORING GATE (PRD § quality_intelligence_engine) ===

# PRD publish thresholds
QUALITY_MIN_SCORE = 60          # hard minimum to publish (PRD: 75 — relaxed to 60 during build-up)
QUALITY_MIN_WORDS = 800         # minimum word count
QUALITY_MANDATORY_SECTIONS = [  # at least 4 of 7 must be present
    "context", "why this matters", "why it matters",
    "operational implications", "economic implications",
    "winners and losers", "future outlook", "strategic takeaway",
]
QUALITY_BANNED_PHRASES = [
    "in today's world", "in today's rapidly", "recent studies show",
    "according to experts", "industry surveys indicate",
    "it is worth noting", "needless to say", "as we know",
    "game-changing", "groundbreaking", "revolutionary", "unprecedented",
    "in conclusion, it is clear", "in summary, it is important",
]


def score_article_quality(article: dict) -> tuple[int, list[str]]:
    """
    Score an article 0-100 against PRD quality criteria.
    Returns (score, list_of_issues).
    """
    issues: list[str] = []
    score = 100

    content = article.get("content", "")
    word_count = article.get("wordCount", 0) or len(content.split())
    title = article.get("title", "")
    category = article.get("category", "")

    # 1. Word count check (-20 if below minimum)
    if word_count < QUALITY_MIN_WORDS:
        issues.append(f"Too short: {word_count} words (min {QUALITY_MIN_WORDS})")
        score -= 20

    # 2. Mandatory section presence (-15 if < 4 sections found)
    content_lower = content.lower()
    sections_found = sum(1 for s in QUALITY_MANDATORY_SECTIONS if s in content_lower)
    unique_needed = 4
    if sections_found < unique_needed:
        issues.append(f"Missing structure: only {sections_found} of 7 mandatory sections found")
        score -= 15

    # 3. Banned phrases / genericness (-3 per phrase, max -20)
    banned_found = [p for p in QUALITY_BANNED_PHRASES if p in content_lower]
    if banned_found:
        deduction = min(len(banned_found) * 3, 20)
        score -= deduction
        issues.append(f"Generic phrases detected: {banned_found[:3]}")

    # 4. Title quality (-10 if too short or keyword-stuffed)
    if len(title) < 20:
        issues.append(f"Title too short: '{title}'")
        score -= 10
    if title.lower().count(article.get("sourceKeyword", "").lower()) > 2:
        issues.append("Title keyword-stuffed")
        score -= 5

    # 5. Pillar assignment check (-15 if not in 4 pillars)
    if category not in EDITORIAL_PILLARS:
        issues.append(f"Off-pillar category: '{category}'")
        score -= 15

    # 6. Key takeaways present (-10 if missing)
    if not article.get("keyTakeaways"):
        issues.append("No keyTakeaways")
        score -= 10

    return max(score, 0), issues


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
    """Normalize any category string to one of the four editorial pillars."""
    if not category:
        return 'AI Infrastructure'

    # Direct mapping (covers all known legacy and pillar values)
    normalized = CATEGORY_MAPPING.get(category, None)
    if normalized:
        return normalized

    # Fuzzy fallback — always maps to a pillar, never returns a legacy category
    category_lower = category.lower()

    if any(w in category_lower for w in ['business', 'finance', 'economy', 'economic',
                                          'enterprise', 'saas', 'erp', 'automation',
                                          'productivity', 'digital transformation',
                                          'cybersecurity', 'health', 'medical',
                                          'career', 'recruitment', 'sales']):
        return 'Enterprise Transformation'

    if any(w in category_lower for w in ['ev', 'electric', 'vehicle', 'battery',
                                          'mobility', 'logistic', 'supply chain',
                                          'manufacturing', 'automotive', 'robotics',
                                          'environment', 'climate', 'energy', 'green']):
        return 'Smart Mobility'

    if any(w in category_lower for w in ['india', 'ondc', 'upi', 'bharat', 'startup',
                                          'smart city', 'government', 'politics', 'world',
                                          'sport', 'entertainment', 'lifestyle', 'travel',
                                          'food', 'celebrity', 'religion']):
        return 'India Digital Transformation'

    # Default: any unrecognised tech/AI topic → AI Infrastructure
    return 'AI Infrastructure'

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

# Differentiated content angles — each drives a genuinely different article
_CONTENT_ANGLES = [
    ("regional",      "{kw} in {region}: market dynamics, adoption barriers, and local investment signals"),
    ("economic",      "{kw}: cost structure, ROI calculus, and the economic winners of this shift"),
    ("enterprise",    "{kw} inside the enterprise: integration challenges, vendor landscape, and build-vs-buy decisions"),
    ("future",        "{kw} in 2025–2026: what the next 18 months look like and which signals to watch"),
    ("workforce",     "{kw} and the workforce: job displacement, new roles, reskilling priorities, and human-AI collaboration"),
    ("infrastructure","{kw} infrastructure: the underlying stack, bottlenecks, and platform dependencies"),
    ("policy",        "{kw} policy and regulation: government response, compliance obligations, and geopolitical implications"),
    ("startup",       "{kw} startup ecosystem: who is building, who is funding, and which bets are likely to pay off"),
]

def expand_keywords(base_keyword: str, region: str) -> List[str]:
    """Generate differentiated content angles — each produces a substantively different article."""
    return [
        angle.format(kw=base_keyword, region=region)
        for _, angle in _CONTENT_ANGLES
    ]

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
            "name": "Country's News",
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
    
    def __init__(self, manager: SuperArticleManager, skip_images: bool = False):
        self.manager = manager
        self.skip_images = skip_images
        if LLM_MODEL and OPENROUTER_API_KEY:
            self.api_key = OPENROUTER_API_KEY
            self.use_openrouter = True
            print(f"🤖 Using OpenRouter model: {LLM_MODEL}")
        else:
            self.api_key = GEMINI_API_KEY
            self.use_openrouter = False
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
        if skip_images:
            print("🖼️  Image generation disabled — articles will use placeholder images")
    
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
                                          searches: Optional[int] = None,
                                          existing_titles: Optional[List[str]] = None) -> Optional[Dict]:
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

        # Intelligence-focused prompt — Country's News transformation (Phase 1)
        trend_context = f"This topic is currently trending with {searches:,} searches." if searches else ""

        # Build an exclusion block so the LLM avoids repeating covered angles
        if existing_titles:
            titles_list = "\n".join(f"  - {t}" for t in existing_titles[:10])
            avoid_block = f"""
---

**ORIGINALITY REQUIREMENT — CRITICAL**
The following articles about this topic ALREADY EXIST on the platform. Your article MUST cover a meaningfully different angle, argument, or lens. Do NOT reuse the same framing, thesis, or section structure as any of these:

{titles_list}

Choose a perspective that is not represented above. If the existing articles cover the "what" and "why", cover the "how" or "who". If they are strategic, be operational. If they are high-level, be specific with numbers and named examples.
"""
        else:
            avoid_block = ""

        base_prompt = f"""You are a senior technology intelligence analyst writing for Country's News — a platform covering how AI, enterprise software, and smart infrastructure are reshaping industries for readers in {region}.

Your mission is to produce a focused intelligence piece about: "{keyword}"
{trend_context}

---

**PLATFORM IDENTITY**
Country's News is NOT a news wire. It is a technology intelligence platform.
- Write with the authority of someone who has thought deeply about the topic
- Take positions. Have opinions. Reach conclusions.
- Explain why things matter, not just what happened
- Connect this topic to broader industry transformation patterns

---

**MANDATORY 7-PART ARTICLE STRUCTURE**
Use these exact H2 sections in this order:

1. **Context** — What is happening and why it is significant right now. One or two sharp paragraphs. No "In today's world..." openings.

2. **Why This Matters** — The strategic stakes. Who cares and why. Frame the consequence, not the definition.

3. **Operational Implications** — How does this change day-to-day workflows, systems, or processes for businesses or practitioners?

4. **Economic Implications** — Cost impact, market size shifts, revenue opportunities, or financial pressures this creates.

5. **Winners and Losers** — Be specific. Name categories of companies, roles, or geographies that benefit or lose out. Avoid vague hedging.

6. **Future Outlook** — Where this goes in the next 12–36 months. What signals to watch. Be specific about timelines and conditions.

7. **Strategic Takeaway** — One clear, actionable insight for a decision-maker, operator, or builder. End with a genuine question or observation that invites reflection.

---

**CONTENT REQUIREMENTS**
- Minimum 1,400 words
- Each section minimum 150 words
- Use data, named examples, and real-world context wherever possible
- Cite specific companies, tools, or initiatives by name
- Include comparison tables or structured lists where analysis benefits from them
- Write for a technically literate audience — no hand-holding on basic concepts
- Regional context for {region}: weave in India-specific data, government initiatives, or local market dynamics where relevant

---

**STRICTLY PROHIBITED — DO NOT DO ANY OF THE FOLLOWING:**
- Fake or vague statistics ("Recent studies show..." / "Industry surveys indicate..." / "According to experts...")
- Keyword stuffing or repeating "{keyword}" excessively in headings
- Generic "What is X?" intros or encyclopedia-style definitions as openers
- Repetitive SEO heading patterns ("{keyword} Guide", "{keyword} Tips", "{keyword} Best Practices")
- Hype language ("revolutionary", "game-changing", "groundbreaking", "unprecedented")
- Filler sentences that restate the obvious
- Hedging every claim into meaninglessness

---

**TONE**
- Analytical and direct
- Opinionated where evidence supports it
- Operator-focused: what does this mean for someone running a business or building a product?
- Confident but intellectually honest about uncertainty
- Concise — cut every sentence that doesn't add information

---

**CATEGORY ASSIGNMENT**
Assign the article to exactly ONE of these four editorial pillars:
- "AI Infrastructure" — local LLMs, inference, AI agents, GPU economics, AI workflows, coding automation
- "Enterprise Transformation" — AI-native SaaS, enterprise automation, ERP evolution, AI copilots, productivity systems
- "Smart Mobility" — EV infrastructure, battery ecosystems, AI fleet intelligence, charging networks, mobility systems
- "India Digital Transformation" — ONDC, UPI, smart cities, government AI, manufacturing digitization, startup ecosystem

---

**CONTENT TYPE**
Assign the article to exactly ONE of these types:
- "strategic-analysis" — why a shift matters, consequences, industry implications
- "deep-dive" — comprehensive operational or technical guide
- "comparison" — structured evaluation of tools, platforms, or approaches
- "intelligence-brief" — concise synthesis of a fast-moving development
- "data-story" — analysis built around numbers, growth charts, or market data

{avoid_block}

        {custom_prompt_additions}"""

        headers = {'Content-Type': 'application/json'}
        
        # Response schema (used by Gemini native; embedded in prompt for OpenRouter)
        response_schema = {
            "type": "OBJECT",
            "properties": {
                "title": {"type": "STRING", "description": "Sharp, intelligent title that conveys insight — not a generic SEO headline (70 chars max)"},
                "excerpt": {"type": "STRING", "description": "One punchy sentence capturing the article's key finding or argument (150-160 chars)"},
                "content": {"type": "STRING", "description": "Full HTML article using the mandatory 7-part structure (1400+ words)"},
                "metaDescription": {"type": "STRING", "description": "Meta description conveying intelligence value, not keyword stuffing (150-160 chars)"},
                "keywords": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "10-15 semantically relevant keywords — no generic filler"},
                "ogTitle": {"type": "STRING", "description": "LinkedIn/Twitter title optimised for decision-maker audiences"},
                "imageAltText": {"type": "STRING", "description": "Descriptive alt text for main image"},
                "socialShareText": {"type": "STRING", "description": "LinkedIn post hook — 1-2 sentences that make someone want to read the analysis"},
                "category": {"type": "STRING", "description": "One of: AI Infrastructure, Enterprise Transformation, Smart Mobility, India Digital Transformation"},
                "subCategory": {"type": "STRING", "description": "Specific sub-topic within the editorial pillar"},
                "contentType": {"type": "STRING", "description": "One of: strategic-analysis, deep-dive, comparison, intelligence-brief, data-story"},
                "difficultyLevel": {"type": "STRING", "description": "Target reader: operator, builder, executive"},
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
                "keyTakeaways": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "3-5 specific, opinionated insights — not generic observations"},
                "socialMediaHashtags": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Relevant hashtags for LinkedIn and X"},
                "callToActionText": {"type": "STRING", "description": "Invitation to think, discuss, or subscribe — not a generic 'click here'"},
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
                "with these exact fields: title (string), excerpt (string), content (string, full HTML using the 7-part structure), "
                "metaDescription (string), keywords (array of strings), ogTitle (string), "
                "imageAltText (string), socialShareText (string), "
                "category (one of: AI Infrastructure, Enterprise Transformation, Smart Mobility, India Digital Transformation), "
                "subCategory (string), "
                "contentType (one of: strategic-analysis, deep-dive, comparison, intelligence-brief, data-story), "
                "difficultyLevel (one of: operator, builder, executive), targetAudience (array of strings), "
                "inlineImageDescriptions (array of objects with description, caption, placementHint), "
                "keyTakeaways (array of 3-5 specific opinionated insights), socialMediaHashtags (array of strings), "
                "callToActionText (string), structuredData (string), relatedTopics (array of strings)."
            )
            payload = {
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": base_prompt + json_schema_hint}],
                "temperature": 0.5,
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
                    "temperature": 0.5,
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

                if self.skip_images:
                    og_image_url = generate_placeholder_image_url(data['ogTitle'])
                    thumbnail_url = generate_placeholder_image_url(data['ogTitle'], 400, 200)
                    inline_images_list = []
                    infographic_count = 0
                else:
                    # Generate main image
                    og_image_prompt = f"Professional news article image for: {data['ogTitle']}. Visual style: {data['imageAltText']}. High quality, news-appropriate. It is very important not to have any garbled text in the images."
                    og_img_fp = os.path.join(IMAGES_BASE_DIR, slug, "main.webp")
                    og_image_url = await asyncio.to_thread(generateImage, og_image_prompt, og_img_fp) or generate_placeholder_image_url(data['ogTitle'])

                    # Generate thumbnail image
                    thumb_image_prompt = f"Thumbnail for news article: {data['ogTitle']}. Compact, visually appealing, news-style thumbnail. High quality. It is very important not to have any garbled text in the images."
                    thumb_img_fp = os.path.join(IMAGES_BASE_DIR, slug, "thumb.webp")
                    thumbnail_url = await asyncio.to_thread(generateImage, thumb_image_prompt, thumb_img_fp) or generate_placeholder_image_url(data['ogTitle'], 400, 200)

                    # Generate inline images with intelligent infographics
                    inline_images_list = []
                    inline_image_descs = data.get("inlineImageDescriptions", [])

                    # Initialize infographic analyzer
                    infographic_analyzer = InfographicAnalyzer()

                    # Parse content into sections for infographic analysis
                    content_sections = self._parse_content_sections(data['content'])
                    infographic_count = 0

                    for i, img_desc in enumerate(inline_image_descs):
                        inline_prompt = f"Supporting image for article section: {img_desc['description']}. Caption context: {img_desc['caption']}. Professional, high-quality. It is very important not to have any garbled text in the images."
                        inline_fp = os.path.join(IMAGES_BASE_DIR, slug, f"inline_{i+1}.webp")
                        inline_url = await asyncio.to_thread(generateImage, inline_prompt, inline_fp) or generate_placeholder_image_url(
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
                        if section['heading'] and len(section['content']) > 100:
                            analysis = infographic_analyzer.analyze_section(section['heading'], section['content'])
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
                                infographic_url = await asyncio.to_thread(generateImage, infographic_prompt, infographic_fp)
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
                    "author": _pick_author(keyword, data.get('category', 'AI Infrastructure'))["name"],
                    "authorTitle": _pick_author(keyword, data.get('category', 'AI Infrastructure'))["title"],
                    "authorBio": _pick_author(keyword, data.get('category', 'AI Infrastructure'))["bio"],
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
                
                # Backup generated images immediately (only when images were generated)
                if not self.skip_images:
                    image_files = []
                    og_img_fp_check = os.path.join(IMAGES_BASE_DIR, slug, "main.webp")
                    thumb_img_fp_check = os.path.join(IMAGES_BASE_DIR, slug, "thumb.webp")
                    if os.path.exists(og_img_fp_check):
                        image_files.append(og_img_fp_check)
                    if os.path.exists(thumb_img_fp_check):
                        image_files.append(thumb_img_fp_check)
                    for i in range(len(data.get("inlineImageDescriptions", []))):
                        inline_fp = os.path.join(IMAGES_BASE_DIR, slug, f"inline_{i+1}.webp")
                        if os.path.exists(inline_fp):
                            image_files.append(inline_fp)
                    if image_files:
                        backup_images(slug, image_files)
                
                print(f"✅ Generated: '{data['title']}' ({word_count} words, cat: {article['category']})")

                # Quality gate (PRD § quality_intelligence_engine)
                q_score, q_issues = score_article_quality(article)
                article['qualityScore'] = q_score
                if q_score < QUALITY_MIN_SCORE:
                    print(f"🚫 REJECTED (quality {q_score}/100): '{data['title']}'")
                    for issue in q_issues:
                        print(f"   • {issue}")
                    return None
                if q_issues:
                    print(f"⚠️  Quality {q_score}/100 — minor issues: {q_issues}")
                else:
                    print(f"✅ Quality score: {q_score}/100 — passed")

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
                                        skip_existing: bool = True,
                                        count_per_keyword: int = 1,
                                        skip_images: bool = False) -> None:
    """Generate articles from specific keywords"""
    print(f"🎯 Starting keyword-based article generation...")
    print(f"📍 Target region: {region}")
    print(f"🎯 Keywords: {', '.join(keywords)}")
    if count_per_keyword > 1:
        print(f"📊 Generating {count_per_keyword} articles per keyword")
    
    generator = ArticleGenerator(manager, skip_images=skip_images)
    article_id_counter = manager.get_next_article_id()
    full_region_name = map_region_code_to_full_name(region)

    # Build a map of base_keyword → existing article titles so we can inject
    # them into the prompt and prevent repetitive angles
    def get_existing_titles_for_keyword(base_kw: str) -> List[str]:
        base_kw_lower = base_kw.lower()
        return [
            a["title"] for a in manager.articles
            if base_kw_lower in a.get("sourceKeyword", "").lower()
            or base_kw_lower in a.get("title", "").lower()
        ]

    # Build expanded keyword list: base + differentiated content angles up to count_per_keyword
    keywords_to_process = []  # list of (variant_keyword, base_keyword)
    for keyword in validate_keyword_input(keywords):
        if skip_existing and keyword in manager.processed_keywords and count_per_keyword == 1:
            print(f"⏭️  SKIP: '{keyword}' already processed")
            continue
        if count_per_keyword <= 1:
            keywords_to_process.append((keyword, keyword))
        else:
            variants = [keyword] + expand_keywords(keyword, full_region_name)
            for i in range(count_per_keyword):
                keywords_to_process.append((variants[i % len(variants)], keyword))

    if not keywords_to_process:
        print("ℹ️  No new keywords to process!")
        return

    print(f"📝 Processing {len(keywords_to_process)} article tasks...")

    # Generate articles — pass existing titles per base keyword to avoid repetition
    tasks = []
    async with aiohttp.ClientSession() as session:
        for variant_kw, base_kw in keywords_to_process:
            existing_titles = get_existing_titles_for_keyword(base_kw)
            task = generator.generate_article_from_keyword(
                session, variant_kw, full_region_name, article_id_counter,
                custom_prompt, existing_titles=existing_titles
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
            # If slug already exists, always create a new article with a unique suffix
            # rather than overwriting — this ensures every generation run adds new content
            if slug in manager.articles_map:
                counter = 2
                new_slug = f"{slug}-{counter}"
                while new_slug in manager.articles_map:
                    counter += 1
                    new_slug = f"{slug}-{counter}"
                result["slug"] = new_slug
                slug = new_slug
                print(f"🔀 Slug collision resolved → '{slug}'")
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
                main_image_url = await asyncio.to_thread(generateImage, main_prompt, main_img_path)
                
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
                thumb_image_url = await asyncio.to_thread(generateImage, thumb_prompt, thumb_img_path)
                
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
                    inline_image_url = await asyncio.to_thread(generateImage, inline_prompt, inline_img_path)
                    
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
    keywords_parser.add_argument('--count', '-c', type=int, default=1,
                                help='Number of articles to generate per keyword (default: 1)')
    keywords_parser.add_argument('--skip-images', action='store_true',
                                help='Skip image generation and use placeholders (much faster)')
    
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
                    manager, args.keywords, args.region, args.prompt, not args.no_skip,
                    count_per_keyword=getattr(args, 'count', 1),
                    skip_images=getattr(args, 'skip_images', False)
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
