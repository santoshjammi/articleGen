#!/usr/bin/env python3
"""
Intelligent Category Management System
Dynamically learns and evolves categories based on article content and trends.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from collections import defaultdict, Counter
import difflib

class IntelligentCategoryManager:
    """Dynamic category management with machine learning capabilities"""
    
    def __init__(self, categories_file: str = "intelligent_categories.json"):
        self.categories_file = categories_file
        self.backup_dir = "category_backups"
        self.confidence_threshold = 0.7
        
        # Initialize data structures
        self.category_data = {
            "categories": {},
            "subcategory_mapping": {},
            "category_keywords": {},
            "category_stats": {},
            "learning_data": {
                "keyword_associations": defaultdict(list),
                "confidence_scores": {},
                "trend_patterns": {},
                "last_update": None
            },
            "version": "1.0.0",
            "created_at": datetime.now().isoformat()
        }
        
        self.load_categories()
    
    def create_backup(self) -> str:
        """Create versioned backup of current categories"""
        os.makedirs(self.backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"categories_backup_{timestamp}.json")
        
        try:
            if os.path.exists(self.categories_file):
                import shutil
                shutil.copy2(self.categories_file, backup_file)
                print(f"📁 Category backup created: {backup_file}")
                return backup_file
        except Exception as e:
            print(f"⚠️  Failed to create backup: {e}")
        return ""
    
    def load_categories(self) -> bool:
        """Load existing categories or create defaults"""
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    
                # Merge with defaults to ensure all keys exist
                self.category_data.update(loaded_data)
                
                # Convert defaultdict back from JSON
                if 'keyword_associations' in self.category_data["learning_data"]:
                    keyword_assoc = self.category_data["learning_data"]["keyword_associations"]
                    self.category_data["learning_data"]["keyword_associations"] = defaultdict(list, keyword_assoc)
                
                print(f"✅ Loaded intelligent categories from {self.categories_file}")
                return True
                
            except Exception as e:
                print(f"❌ Error loading categories: {e}")
                print("🔄 Creating new intelligent category system...")
        
        # Initialize with current mappings from super_article_manager.py
        self._initialize_default_categories()
        return False
    
    def _initialize_default_categories(self):
        """Initialize with current category mappings"""
        # Check if super_article_manager has SUBCATEGORY_MAPPING
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from super_article_manager import SUBCATEGORY_MAPPING
            existing_subcategory_mapping = SUBCATEGORY_MAPPING
        except ImportError:
            # Fallback to our enhanced mapping
            existing_subcategory_mapping = {
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
                'Banking News': 'Business'
            }
        
        # Convert to intelligent format
        self.category_data["categories"] = {
            "Technology": {
                "subcategories": ["AI", "Software", "Hardware", "Web Development", "Cybersecurity", "Data Science", 
                                "Machine Learning", "Cloud Computing", "DevOps", "Mobile Development"],
                "keywords": ["tech", "digital", "software", "ai", "artificial intelligence", "programming", 
                           "development", "computing", "cyber", "data", "algorithm", "code"],
                "confidence": 1.0,
                "created_at": datetime.now().isoformat()
            },
            "Business": {
                "subcategories": ["Finance", "Marketing", "Strategy", "Entrepreneurship", "E-commerce", 
                                "Banking", "Investment", "Startup"],
                "keywords": ["business", "finance", "economy", "marketing", "startup", "investment", 
                           "banking", "commerce", "trade", "corporate", "strategy", "entrepreneur"],
                "confidence": 1.0,
                "created_at": datetime.now().isoformat()
            },
            "Health": {
                "subcategories": ["Wellness", "Medical", "Fitness", "Mental Health", "Nutrition", "Healthcare"],
                "keywords": ["health", "medical", "wellness", "fitness", "healthcare", "doctor", 
                           "medicine", "nutrition", "mental", "therapy", "hospital"],
                "confidence": 1.0,
                "created_at": datetime.now().isoformat()
            },
            "Sports": {
                "subcategories": ["Football", "Cricket", "Basketball", "Olympics", "Tennis", "Soccer"],
                "keywords": ["sports", "game", "tournament", "player", "team", "match", 
                           "football", "cricket", "basketball", "olympics", "athletic"],
                "confidence": 1.0,
                "created_at": datetime.now().isoformat()
            },
            "Entertainment": {
                "subcategories": ["Movies", "Music", "TV", "Celebrity", "Gaming", "Streaming"],
                "keywords": ["movie", "music", "entertainment", "celebrity", "film", "tv", 
                           "gaming", "streaming", "show", "actor", "singer"],
                "confidence": 1.0,
                "created_at": datetime.now().isoformat()
            },
            "Lifestyle": {
                "subcategories": ["Travel", "Food", "Fashion", "Career", "Home", "Beauty"],
                "keywords": ["travel", "food", "lifestyle", "fashion", "career", "home", 
                           "beauty", "cooking", "recipe", "style", "decoration"],
                "confidence": 1.0,
                "created_at": datetime.now().isoformat()
            },
            "Environment": {
                "subcategories": ["Climate", "Sustainability", "Green Energy", "Conservation", "Pollution"],
                "keywords": ["environment", "climate", "green", "sustainability", "eco", 
                           "pollution", "renewable", "conservation", "carbon", "emission"],
                "confidence": 1.0,
                "created_at": datetime.now().isoformat()
            },
            "World": {
                "subcategories": ["Politics", "International", "News", "Government", "Global"],
                "keywords": ["news", "politics", "international", "government", "world", 
                           "global", "country", "nation", "diplomatic", "policy"],
                "confidence": 1.0,
                "created_at": datetime.now().isoformat()
            }
        }
        
        # Convert existing mappings
        self.category_data["subcategory_mapping"] = existing_subcategory_mapping.copy()
        
        # Initialize stats
        for category in self.category_data["categories"]:
            self.category_data["category_stats"][category] = {
                "article_count": 0,
                "avg_confidence": 1.0,
                "last_used": datetime.now().isoformat(),
                "trending_score": 0.0
            }
        
        print("🆕 Initialized intelligent category system with defaults")
    
    def save_categories(self) -> bool:
        """Save categories with backup"""
        try:
            # Create backup first
            self.create_backup()
            
            # Update metadata
            self.category_data["learning_data"]["last_update"] = datetime.now().isoformat()
            
            # Convert defaultdict to regular dict for JSON serialization
            learning_data = self.category_data["learning_data"]
            if isinstance(learning_data["keyword_associations"], defaultdict):
                learning_data["keyword_associations"] = dict(learning_data["keyword_associations"])
            
            # Save current data
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.category_data, f, indent=2, ensure_ascii=False, default=str)
            
            # Restore defaultdict
            learning_data["keyword_associations"] = defaultdict(list, learning_data["keyword_associations"])
            
            print(f"💾 Saved intelligent categories to {self.categories_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving categories: {e}")
            return False
    
    def analyze_content_for_category(self, title: str, content: str, keywords: List[str]) -> Dict:
        """Intelligent content analysis for category detection"""
        text_to_analyze = f"{title} {content}".lower()
        word_tokens = re.findall(r'\b\w+\b', text_to_analyze)
        word_freq = Counter(word_tokens)
        
        category_scores = {}
        confidence_scores = {}
        
        # Analyze against each category
        for category, category_info in self.category_data["categories"].items():
            score = 0.0
            category_keywords = category_info.get("keywords", [])
            subcategories = category_info.get("subcategories", [])
            
            # Keyword matching
            for keyword in category_keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in text_to_analyze:
                    # Weight by frequency and importance
                    frequency = word_freq.get(keyword_lower, 0)
                    importance = len(keyword.split())  # Multi-word keywords are more specific
                    score += frequency * importance * 10
            
            # Subcategory matching
            for subcategory in subcategories:
                subcategory_lower = subcategory.lower()
                if subcategory_lower in text_to_analyze:
                    score += 15  # Higher weight for subcategory matches
            
            # Semantic similarity (simplified)
            for provided_keyword in keywords:
                for category_keyword in category_keywords:
                    similarity = difflib.SequenceMatcher(None, 
                                                      provided_keyword.lower(), 
                                                      category_keyword.lower()).ratio()
                    if similarity > 0.6:
                        score += similarity * 8
            
            category_scores[category] = score
            
            # Calculate confidence based on score distribution
            total_score = sum(category_scores.values()) or 1
            confidence_scores[category] = min(score / total_score, 1.0)
        
        # Find best match
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            best_confidence = confidence_scores[best_category]
        else:
            best_category = "World"  # Fallback
            best_confidence = 0.3
        
        return {
            "suggested_category": best_category,
            "confidence": best_confidence,
            "all_scores": category_scores,
            "analysis_method": "intelligent_content_analysis"
        }
    
    def learn_from_article(self, article: Dict, suggested_category: str = None) -> Dict:
        """Learn patterns from new article"""
        title = article.get("title", "")
        content = article.get("content", "")
        keywords = article.get("keywords", [])
        current_category = article.get("category", "")
        subcategory = article.get("subCategory", "")
        
        # Analyze content
        analysis = self.analyze_content_for_category(title, content, keywords)
        
        # Use suggested category if provided and confidence is high
        if suggested_category and analysis["confidence"] > self.confidence_threshold:
            final_category = suggested_category
            confidence = analysis["confidence"]
        else:
            final_category = analysis["suggested_category"]
            confidence = analysis["confidence"]
        
        # Update learning data
        learning_data = self.category_data["learning_data"]
        
        # Record keyword associations
        for keyword in keywords:
            learning_data["keyword_associations"][final_category].append(keyword.lower())
        
        # Record confidence score
        learning_data["confidence_scores"][f"{title[:50]}"] = {
            "category": final_category,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update category stats
        if final_category in self.category_data["category_stats"]:
            stats = self.category_data["category_stats"][final_category]
            stats["article_count"] += 1
            stats["last_used"] = datetime.now().isoformat()
            
            # Update average confidence
            prev_avg = stats.get("avg_confidence", 0.5)
            count = stats["article_count"]
            stats["avg_confidence"] = ((prev_avg * (count - 1)) + confidence) / count
        
        # Learn new subcategories
        if subcategory and subcategory not in self.category_data["subcategory_mapping"]:
            self._learn_new_subcategory(subcategory, final_category, confidence)
        
        # Learn new keywords
        self._learn_new_keywords(final_category, keywords, confidence)
        
        return {
            "final_category": final_category,
            "confidence": confidence,
            "learning_applied": True,
            "changes_detected": current_category != final_category
        }
    
    def _learn_new_subcategory(self, subcategory: str, category: str, confidence: float):
        """Learn and add new subcategory"""
        if confidence > self.confidence_threshold:
            self.category_data["subcategory_mapping"][subcategory] = category
            
            # Add to category's subcategory list
            if category in self.category_data["categories"]:
                subcategories = self.category_data["categories"][category]["subcategories"]
                if subcategory not in subcategories:
                    subcategories.append(subcategory)
                    print(f"🧠 Learned new subcategory: '{subcategory}' → {category}")
    
    def _learn_new_keywords(self, category: str, keywords: List[str], confidence: float):
        """Learn and add new keywords to category"""
        if confidence > self.confidence_threshold and category in self.category_data["categories"]:
            category_keywords = self.category_data["categories"][category]["keywords"]
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # Add if not already present and relevant
                if (keyword_lower not in category_keywords and 
                    len(keyword_lower) > 2 and
                    not keyword_lower.isdigit()):
                    
                    # Simple relevance check
                    if self._is_keyword_relevant(keyword_lower, category):
                        category_keywords.append(keyword_lower)
                        print(f"📝 Learned new keyword: '{keyword_lower}' for {category}")
    
    def _is_keyword_relevant(self, keyword: str, category: str) -> bool:
        """Simple relevance check for new keywords"""
        # Skip very generic words
        generic_words = {"news", "latest", "update", "today", "new", "best", "top", "guide", "2025"}
        if keyword in generic_words:
            return False
        
        # Skip if already exists in other categories
        for other_category, info in self.category_data["categories"].items():
            if other_category != category and keyword in info.get("keywords", []):
                return False
        
        return True
    
    def suggest_category_optimizations(self) -> Dict:
        """Suggest optimizations based on learning data"""
        suggestions = {
            "merge_similar": [],
            "split_categories": [],
            "new_categories": [],
            "keyword_updates": []
        }
        
        # Analyze keyword associations for patterns
        keyword_assoc = self.category_data["learning_data"]["keyword_associations"]
        
        # Find categories with overlapping keywords
        category_keywords = {}
        for category, keywords in keyword_assoc.items():
            if keywords:
                category_keywords[category] = set(keywords)
        
        # Suggest merges for high overlap
        categories = list(category_keywords.keys())
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                overlap = category_keywords[cat1] & category_keywords[cat2]
                total = category_keywords[cat1] | category_keywords[cat2]
                if overlap and len(overlap) / len(total) > 0.3:
                    suggestions["merge_similar"].append({
                        "categories": [cat1, cat2],
                        "overlap_ratio": len(overlap) / len(total),
                        "common_keywords": list(overlap)
                    })
        
        # Suggest splits for categories with too many diverse keywords
        for category, keywords in category_keywords.items():
            if len(keywords) > 20:  # Arbitrary threshold
                suggestions["split_categories"].append({
                    "category": category,
                    "keyword_count": len(keywords),
                    "suggestion": f"Consider splitting {category} into subcategories"
                })
        
        # Find emerging keyword clusters that might need new categories
        all_keywords = []
        for keywords in keyword_assoc.values():
            all_keywords.extend(keywords)
        
        keyword_freq = Counter(all_keywords)
        uncategorized_keywords = [k for k, v in keyword_freq.items() if v >= 3]
        
        if uncategorized_keywords:
            suggestions["new_categories"].append({
                "emerging_keywords": uncategorized_keywords[:10],
                "suggestion": "Consider creating categories for these trending keywords"
            })
        
        return suggestions
    
    def get_trending_categories(self, days: int = 30) -> List[Tuple[str, float]]:
        """Get trending categories based on recent usage"""
        category_trends = []
        
        for category, stats in self.category_data["category_stats"].items():
            # Simple trending score based on article count and recency
            article_count = stats.get("article_count", 0)
            avg_confidence = stats.get("avg_confidence", 0.5)
            
            # Calculate trending score (simplified)
            trending_score = article_count * avg_confidence
            category_trends.append((category, trending_score))
        
        return sorted(category_trends, key=lambda x: x[1], reverse=True)
    
    def categorize_with_intelligence(self, title: str, content: str, keywords: List[str], 
                                   current_category: str = None, subcategory: str = None) -> Dict:
        """Main intelligent categorization function"""
        
        # Step 1: Content analysis
        analysis = self.analyze_content_for_category(title, content, keywords)
        
        # Step 2: Check subcategory mapping
        subcategory_result = None
        if subcategory and subcategory in self.category_data["subcategory_mapping"]:
            subcategory_result = self.category_data["subcategory_mapping"][subcategory]
        
        # Step 3: Confidence-based decision
        final_category = analysis["suggested_category"]
        confidence = analysis["confidence"]
        reasoning = ["content_analysis"]
        
        # Override with subcategory if more confident
        if subcategory_result and confidence < 0.8:
            final_category = subcategory_result
            confidence = 0.9  # High confidence for subcategory mapping
            reasoning.append("subcategory_mapping")
        
        # Check if this contradicts current category
        category_changed = current_category and current_category != final_category
        
        if category_changed and confidence > self.confidence_threshold:
            reasoning.append("category_correction")
        
        return {
            "category": final_category,
            "confidence": confidence,
            "reasoning": reasoning,
            "changed": category_changed,
            "analysis_data": analysis
        }
    
    def enhance_with_trending_data(self, trending_keywords: List[Tuple[str, str, int]]):
        """Enhance categories with trending keyword data"""
        print("📈 Enhancing categories with trending data...")
        
        trend_patterns = self.category_data["learning_data"]["trend_patterns"]
        
        for region, keyword, searches in trending_keywords:
            # Analyze keyword for category hints
            analysis = self.analyze_content_for_category(keyword, keyword, [keyword])
            suggested_category = analysis["suggested_category"]
            
            # Record trend pattern
            if suggested_category not in trend_patterns:
                trend_patterns[suggested_category] = {
                    "trending_keywords": [],
                    "total_searches": 0,
                    "regions": set()
                }
            
            trend_patterns[suggested_category]["trending_keywords"].append({
                "keyword": keyword,
                "searches": searches,
                "region": region,
                "timestamp": datetime.now().isoformat()
            })
            trend_patterns[suggested_category]["total_searches"] += searches
            trend_patterns[suggested_category]["regions"].add(region)
        
        # Update trending scores for categories
        for category in trend_patterns:
            if category in self.category_data["category_stats"]:
                total_searches = trend_patterns[category]["total_searches"]
                self.category_data["category_stats"][category]["trending_score"] = total_searches
        
        print("✅ Enhanced categories with trending data")
    
    def generate_category_report(self) -> Dict:
        """Generate comprehensive category intelligence report"""
        report = {
            "summary": {
                "total_categories": len(self.category_data["categories"]),
                "total_subcategories": len(self.category_data["subcategory_mapping"]),
                "confidence_threshold": self.confidence_threshold,
                "last_update": self.category_data["learning_data"]["last_update"]
            },
            "category_stats": {},
            "trending_categories": self.get_trending_categories(),
            "optimization_suggestions": self.suggest_category_optimizations(),
            "learning_insights": {}
        }
        
        # Detailed category stats
        for category, stats in self.category_data["category_stats"].items():
            category_info = self.category_data["categories"].get(category, {})
            report["category_stats"][category] = {
                **stats,
                "subcategory_count": len(category_info.get("subcategories", [])),
                "keyword_count": len(category_info.get("keywords", [])),
                "confidence": category_info.get("confidence", 0.5)
            }
        
        # Learning insights
        keyword_assoc = self.category_data["learning_data"]["keyword_associations"]
        report["learning_insights"] = {
            "most_learned_categories": sorted(
                [(k, len(v)) for k, v in keyword_assoc.items()], 
                key=lambda x: x[1], reverse=True
            )[:5],
            "total_keyword_associations": sum(len(v) for v in keyword_assoc.values()),
            "confidence_history": len(self.category_data["learning_data"]["confidence_scores"])
        }
        
        return report

if __name__ == "__main__":
    # Demo the intelligent system
    print("🧠 Intelligent Category Management System Demo")
    print("=" * 60)
    
    # Initialize system
    manager = IntelligentCategoryManager()
    
    # Demo article
    demo_article = {
        "title": "Advanced Machine Learning Techniques for Business Intelligence",
        "content": "This article explores artificial intelligence, machine learning algorithms, and their applications in business analytics and data science...",
        "keywords": ["machine learning", "AI", "business intelligence", "data science", "analytics"],
        "category": "World",  # Incorrectly categorized
        "subCategory": "Artificial Intelligence"
    }
    
    # Test intelligent categorization
    result = manager.categorize_with_intelligence(
        demo_article["title"],
        demo_article["content"],
        demo_article["keywords"],
        demo_article["category"],
        demo_article["subCategory"]
    )
    
    print(f"📊 Categorization Result:")
    print(f"   Suggested Category: {result['category']}")
    print(f"   Confidence: {result['confidence']:.2f}")
    print(f"   Reasoning: {', '.join(result['reasoning'])}")
    print(f"   Changed: {result['changed']}")
    
    # Test learning
    learning_result = manager.learn_from_article(demo_article, result["category"])
    print(f"\n🧠 Learning Result:")
    print(f"   Final Category: {learning_result['final_category']}")
    print(f"   Learning Applied: {learning_result['learning_applied']}")
    
    # Save the intelligent system
    manager.save_categories()
    
    # Generate report
    report = manager.generate_category_report()
    print(f"\n📈 Intelligence Report:")
    print(f"   Total Categories: {report['summary']['total_categories']}")
    print(f"   Total Subcategories: {report['summary']['total_subcategories']}")
    print(f"   Trending Categories: {report['trending_categories'][:3]}")
    
    print("\n🎉 Intelligent categorization system ready!")
