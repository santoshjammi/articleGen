#!/usr/bin/env python3
"""
AI-Powered Article Categorization System
Simple, intelligent categorization based on actual content analysis
"""

import os
import json
import re
from typing import Dict, List, Optional, Tuple
from collections import Counter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AICategorizer:
    """Simple AI-powered categorization using content analysis"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.categories = [
            "Technology",    # AI, software, tech news, gadgets, programming
            "Business",      # Finance, economy, marketing, startups, corporate
            "Health",        # Medical, wellness, fitness, healthcare
            "Sports",        # All sports, games, tournaments, athletes
            "Entertainment", # Movies, music, TV, celebrities, gaming
            "Lifestyle",     # Travel, food, fashion, home, personal
            "World",         # Politics, international news, government
            "Environment"    # Climate, sustainability, nature, ecology
        ]
        
        # Simple keyword hints for each category (much reduced)
        self.category_hints = {
            "Technology": ["tech", "ai", "software", "digital", "computer", "app", "internet", "cyber"],
            "Business": ["business", "finance", "economy", "market", "company", "startup", "trade"],
            "Health": ["health", "medical", "doctor", "wellness", "fitness", "medicine", "hospital"],
            "Sports": ["sport", "game", "team", "player", "match", "tournament", "athletic"],
            "Entertainment": ["movie", "music", "tv", "celebrity", "film", "entertainment", "show"],
            "Lifestyle": ["travel", "food", "fashion", "home", "lifestyle", "cooking", "recipe"],
            "World": ["politics", "government", "international", "country", "nation", "policy"],
            "Environment": ["environment", "climate", "green", "nature", "pollution", "sustainability"]
        }
    
    def analyze_content_simple(self, title: str, content: str, keywords: List[str]) -> Dict:
        """Simple content analysis without complex AI calls"""
        
        # Combine all text for analysis
        all_text = f"{title} {content} {' '.join(keywords)}".lower()
        
        # Clean and tokenize
        words = re.findall(r'\b\w+\b', all_text)
        word_freq = Counter(words)
        
        # Score each category
        category_scores = {}
        for category, hints in self.category_hints.items():
            score = 0
            for hint in hints:
                # Count exact matches and partial matches
                exact_count = word_freq.get(hint, 0)
                partial_count = sum(1 for word in words if hint in word and len(word) > len(hint))
                
                score += exact_count * 10 + partial_count * 5
            
            # Bonus for title matches (more important)
            title_lower = title.lower()
            for hint in hints:
                if hint in title_lower:
                    score += 20
            
            category_scores[category] = score
        
        # Find best category
        if not category_scores or max(category_scores.values()) == 0:
            return {"category": "World", "confidence": 0.3, "method": "fallback"}
        
        best_category = max(category_scores, key=category_scores.get)
        max_score = category_scores[best_category]
        total_score = sum(category_scores.values())
        
        confidence = min(max_score / (total_score + 1), 1.0) if total_score > 0 else 0.3
        
        return {
            "category": best_category,
            "confidence": confidence,
            "method": "content_analysis",
            "scores": category_scores
        }
    
    async def analyze_with_ai(self, title: str, content: str, keywords: List[str]) -> Dict:
        """Use AI (Gemini) for more sophisticated categorization when needed"""
        
        if not self.api_key:
            print("⚠️  No Gemini API key found, using simple analysis")
            return self.analyze_content_simple(title, content, keywords)
        
        try:
            import aiohttp
            
            # Create a focused prompt for categorization
            categories_str = ", ".join(self.categories)
            
            prompt = f"""You are an expert content categorizer. Analyze this article and determine the SINGLE most appropriate category.

Article Title: "{title}"
Article Content: {content[:1500]}...
Keywords: {', '.join(keywords[:10])}

Available Categories: {categories_str}

Instructions:
1. Choose ONLY ONE category that best fits the main topic
2. Consider the primary subject matter, not secondary mentions
3. If uncertain, choose the category that represents the main focus

Respond with ONLY the category name (e.g., "Technology" or "Business")."""

            headers = {'Content-Type': 'application/json'}
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 50
                }
            }
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        ai_response = result["candidates"][0]["content"]["parts"][0]["text"].strip()
                        
                        # Clean the response
                        ai_category = ai_response.replace('"', '').replace("'", '').strip()
                        
                        # Validate the response
                        if ai_category in self.categories:
                            return {
                                "category": ai_category,
                                "confidence": 0.85,
                                "method": "ai_analysis"
                            }
                        else:
                            print(f"⚠️  AI returned invalid category: {ai_category}")
                            
        except Exception as e:
            print(f"⚠️  AI categorization failed: {e}")
        
        # Fallback to simple analysis
        return self.analyze_content_simple(title, content, keywords)
    
    def categorize_article(self, article: Dict, use_ai: bool = True) -> Dict:
        """Categorize an article using the best available method"""
        
        title = article.get('title', '')
        content = article.get('content', '')
        keywords = article.get('keywords', [])
        
        if not title and not content:
            return {"category": "World", "confidence": 0.2, "method": "no_content"}
        
        # For short articles or when AI is disabled, use simple analysis
        if not use_ai or len(content) < 500:
            return self.analyze_content_simple(title, content, keywords)
        
        # Use AI for longer, more complex articles
        import asyncio
        try:
            # Run the async AI analysis
            result = asyncio.create_task(self.analyze_with_ai(title, content, keywords))
            return asyncio.get_event_loop().run_until_complete(result)
        except:
            # Fallback to simple analysis
            return self.analyze_content_simple(title, content, keywords)
    
    def batch_categorize(self, articles: List[Dict], use_ai: bool = True, max_ai_calls: int = 100) -> List[Dict]:
        """Categorize multiple articles efficiently"""
        
        results = []
        ai_calls_made = 0
        
        for i, article in enumerate(articles):
            print(f"📊 Categorizing article {i+1}/{len(articles)}: {article.get('title', 'Untitled')[:50]}...")
            
            # Use AI for first N articles, then simple analysis
            use_ai_for_this = use_ai and ai_calls_made < max_ai_calls and len(article.get('content', '')) > 500
            
            result = self.categorize_article(article, use_ai_for_this)
            
            if result['method'] == 'ai_analysis':
                ai_calls_made += 1
            
            # Update the article
            original_category = article.get('category', 'Unknown')
            article['category'] = result['category']
            
            results.append({
                'title': article.get('title', 'Untitled'),
                'original_category': original_category,
                'new_category': result['category'],
                'confidence': result['confidence'],
                'method': result['method'],
                'changed': original_category != result['category']
            })
            
            if result['changed']:
                print(f"   🔄 {original_category} → {result['category']} (confidence: {result['confidence']:.2f})")
            else:
                print(f"   ✅ Confirmed: {result['category']} (confidence: {result['confidence']:.2f})")
        
        print(f"\n📈 Categorization Summary:")
        print(f"   Total articles: {len(articles)}")
        print(f"   AI calls made: {ai_calls_made}")
        print(f"   Changed categories: {sum(1 for r in results if r['changed'])}")
        
        return results

# Integration functions
def simple_ai_categorize(article: Dict) -> str:
    """Simple function to categorize a single article"""
    categorizer = AICategorizer()
    result = categorizer.categorize_article(article, use_ai=True)
    return result['category']

def categorize_with_confidence(article: Dict) -> Tuple[str, float]:
    """Categorize article and return confidence score"""
    categorizer = AICategorizer()
    result = categorizer.categorize_article(article, use_ai=True)
    return result['category'], result['confidence']

if __name__ == "__main__":
    # Demo the AI categorizer
    print("🤖 AI-Powered Article Categorization Demo")
    print("=" * 50)
    
    # Test articles
    test_articles = [
        {
            "title": "Revolutionary AI Algorithm Transforms Healthcare Diagnosis",
            "content": "Artificial intelligence and machine learning technologies are revolutionizing medical diagnosis. Deep learning algorithms can now detect diseases with unprecedented accuracy...",
            "keywords": ["AI", "healthcare", "machine learning", "diagnosis", "technology"]
        },
        {
            "title": "Stock Market Reaches New Heights as Tech Stocks Surge",
            "content": "The stock market closed at record highs today, driven by strong performance in technology stocks. Apple, Google, and Microsoft all saw significant gains...",
            "keywords": ["stock market", "finance", "technology stocks", "investment", "business"]
        },
        {
            "title": "Climate Change Summit Announces Global Green Initiative",
            "content": "World leaders gathered at the climate summit to announce new environmental policies. The initiative focuses on renewable energy, carbon reduction, and sustainability...",
            "keywords": ["climate change", "environment", "sustainability", "green energy", "global warming"]
        }
    ]
    
    categorizer = AICategorizer()
    
    print("Testing simple content analysis:")
    for article in test_articles:
        result = categorizer.analyze_content_simple(
            article['title'], 
            article['content'], 
            article['keywords']
        )
        print(f"📝 '{article['title'][:40]}...'")
        print(f"   Category: {result['category']} (confidence: {result['confidence']:.2f})")
        print(f"   Method: {result['method']}")
        print()
    
    print("✅ AI Categorization system ready!")
    print("📋 Available categories:", ", ".join(categorizer.categories))
