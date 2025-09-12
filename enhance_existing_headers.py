#!/usr/bin/env python3
"""
Enhanced Article Header Updater
Adds keyword optimization to headers in existing articles without generating infographics.
Fast, cost-effective enhancement for all existing content.
"""

import json
import re
import os
from typing import Dict, List, Tuple
from datetime import datetime
import shutil

class ExistingArticleHeaderEnhancer:
    """Enhance existing articles with keyword-optimized headers (no infographics)"""
    
    def __init__(self, articles_file: str = "perplexityArticles_eeat_enhanced.json"):
        self.articles_file = articles_file
        self.backup_file = f"{articles_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_backup(self):
        """Create backup before enhancement"""
        shutil.copy2(self.articles_file, self.backup_file)
        print(f"📁 Backup created: {self.backup_file}")
    
    def extract_main_keyword(self, article: Dict) -> str:
        """Extract main keyword from article data"""
        # Priority order for keyword extraction
        keywords = article.get('keywords', [])
        title = article.get('title', '')
        
        if keywords and len(keywords) > 0:
            # Use first keyword as primary, clean it up
            main_keyword = keywords[0].strip()
            # Remove any bracketed content like [IN]
            main_keyword = re.sub(r'\[.*?\]', '', main_keyword).strip()
            return main_keyword
        
        # Extract from title if no keywords
        title_words = re.findall(r'\b\w+\b', title.lower())
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
            'how', 'what', 'why', 'when', 'where', 'complete', 'guide', '2025', '2024', 'comprehensive',
            'vs', 'ultimate', 'best', 'top', 'latest', 'new'
        }
        meaningful_words = [w for w in title_words if w not in stop_words and len(w) > 2]
        
        return ' '.join(meaningful_words[:2]) if meaningful_words else 'guide'
    
    def enhance_content_headers(self, content: str, main_keyword: str, title: str) -> Tuple[str, int]:
        """Add keyword to headers while maintaining natural flow"""
        if not content or not main_keyword:
            return content, 0
        
        # Pattern to match headers (##, ###, ####)
        header_pattern = r'^(#{2,4})\s+(.+)$'
        headers_enhanced = 0
        
        def enhance_header(match):
            nonlocal headers_enhanced
            header_level = match.group(1)
            header_text = match.group(2).strip()
            
            # Skip if keyword already in header (case insensitive)
            if main_keyword.lower() in header_text.lower():
                return f"{header_level} {header_text}"
            
            # Skip very short headers or those that are just numbers/symbols
            if len(header_text) < 3 or header_text.isdigit():
                return f"{header_level} {header_text}"
            
            # Choose enhancement pattern based on header content and context
            enhanced_header = self._choose_header_enhancement(header_text, main_keyword, header_level)
            
            if enhanced_header != header_text:
                headers_enhanced += 1
                return f"{header_level} {enhanced_header}"
            else:
                return f"{header_level} {header_text}"
        
        # Apply header enhancement
        enhanced_content = re.sub(header_pattern, enhance_header, content, flags=re.MULTILINE)
        
        return enhanced_content, headers_enhanced
    
    def _choose_header_enhancement(self, header_text: str, main_keyword: str, header_level: str) -> str:
        """Choose the most appropriate header enhancement pattern"""
        header_lower = header_text.lower()
        
        # Pattern matching for natural enhancement
        if any(word in header_lower for word in ['what is', 'definition', 'overview', 'introduction']):
            return f"What is {main_keyword}? {header_text}"
        
        elif any(word in header_lower for word in ['how to', 'step', 'guide', 'process', 'method']):
            return f"How to {header_text} with {main_keyword}"
        
        elif any(word in header_lower for word in ['best', 'top', 'optimal', 'recommended']):
            return f"{header_text} for {main_keyword}"
        
        elif any(word in header_lower for word in ['why', 'reason', 'importance', 'benefit']):
            return f"Why {main_keyword} {header_text.replace('Why ', '').replace('why ', '')}"
        
        elif any(word in header_lower for word in ['when', 'timing', 'schedule']):
            return f"When to Use {main_keyword}: {header_text}"
        
        elif any(word in header_lower for word in ['where', 'location', 'place']):
            return f"Where {main_keyword} {header_text.replace('Where ', '').replace('where ', '')}"
        
        elif any(word in header_lower for word in ['feature', 'characteristic', 'aspect', 'element']):
            return f"{main_keyword} {header_text}"
        
        elif any(word in header_lower for word in ['future', 'trend', 'upcoming', 'prediction']):
            return f"Future of {main_keyword}: {header_text}"
        
        elif any(word in header_lower for word in ['challenge', 'problem', 'issue', 'difficulty']):
            return f"{main_keyword} {header_text}"
        
        elif any(word in header_lower for word in ['solution', 'answer', 'resolution']):
            return f"{header_text} for {main_keyword}"
        
        elif any(word in header_lower for word in ['comparison', 'vs', 'versus', 'difference']):
            return f"{header_text} in {main_keyword}"
        
        elif any(word in header_lower for word in ['cost', 'price', 'budget', 'expense']):
            return f"{main_keyword} {header_text}"
        
        elif any(word in header_lower for word in ['security', 'safety', 'protection']):
            return f"{main_keyword} {header_text}"
        
        elif any(word in header_lower for word in ['conclusion', 'summary', 'final']):
            return f"{header_text}: {main_keyword} Takeaways"
        
        else:
            # Default enhancement pattern
            if header_level == "##":  # Main sections
                return f"{main_keyword}: {header_text}"
            else:  # Subsections
                return f"{header_text} with {main_keyword}"
    
    def enhance_article_metadata(self, article: Dict, main_keyword: str) -> int:
        """Enhance article metadata with keyword optimization"""
        changes = 0
        
        # Enhance meta description if exists
        if 'metaDescription' in article and main_keyword:
            meta_desc = article['metaDescription']
            if main_keyword.lower() not in meta_desc.lower():
                # Add keyword to beginning of meta description
                article['metaDescription'] = f"{main_keyword}: {meta_desc}"
                changes += 1
        
        # Add main keyword to keywords list if not present
        keywords = article.get('keywords', [])
        if main_keyword and main_keyword not in [k.lower() for k in keywords]:
            keywords.insert(0, main_keyword)
            article['keywords'] = keywords
            changes += 1
        
        return changes
    
    def enhance_article(self, article: Dict) -> Dict:
        """Enhance single article with keyword-optimized headers"""
        # Skip if already enhanced
        if article.get('enhanced_headers'):
            return {'enhanced': False, 'reason': 'already_enhanced'}
        
        main_keyword = self.extract_main_keyword(article)
        if not main_keyword:
            return {'enhanced': False, 'reason': 'no_keyword'}
        
        title = article.get('title', '')
        original_content = article.get('content', '')
        
        if not original_content:
            return {'enhanced': False, 'reason': 'no_content'}
        
        # Enhance content headers
        enhanced_content, headers_count = self.enhance_content_headers(original_content, main_keyword, title)
        
        # Enhance metadata
        metadata_changes = self.enhance_article_metadata(article, main_keyword)
        
        # Update article if changes were made
        if enhanced_content != original_content or metadata_changes > 0:
            article['content'] = enhanced_content
            article['enhanced_headers'] = True
            article['enhancement_date'] = datetime.now().isoformat()
            article['enhanced_headers_count'] = headers_count
            article['main_keyword_enhanced'] = main_keyword
            
            return {
                'enhanced': True,
                'headers_count': headers_count,
                'metadata_changes': metadata_changes,
                'main_keyword': main_keyword
            }
        
        return {'enhanced': False, 'reason': 'no_changes_needed'}
    
    def enhance_all_articles(self, max_articles: int = None, backup: bool = True) -> Dict:
        """Enhance all existing articles with header optimization"""
        print("🚀 Starting Header Enhancement for Existing Articles")
        print("=" * 60)
        print("✨ Adding keyword optimization to headers (no infographics)")
        print("⚡ Fast processing - text enhancement only")
        print()
        
        # Create backup if requested
        if backup:
            self.create_backup()
        
        # Load articles
        try:
            with open(self.articles_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)
        except Exception as e:
            print(f"❌ Error loading articles: {e}")
            return {'error': str(e)}
        
        total_articles = len(articles)
        if max_articles:
            total_articles = min(total_articles, max_articles)
            articles = articles[:max_articles]
        
        print(f"📊 Processing {total_articles} articles...")
        print()
        
        # Statistics
        enhanced_count = 0
        skipped_count = 0
        total_headers_enhanced = 0
        total_metadata_changes = 0
        
        # Process articles
        for i, article in enumerate(articles, 1):
            result = self.enhance_article(article)
            
            if result['enhanced']:
                enhanced_count += 1
                total_headers_enhanced += result.get('headers_count', 0)
                total_metadata_changes += result.get('metadata_changes', 0)
                
                if i <= 5:  # Show first few examples
                    print(f"✅ Enhanced: {article.get('title', 'Unknown')[:50]}...")
                    print(f"   🎯 Keyword: {result.get('main_keyword', 'N/A')}")
                    print(f"   📝 Headers: {result.get('headers_count', 0)}")
                    print()
            else:
                skipped_count += 1
                if result['reason'] == 'already_enhanced' and i <= 3:
                    print(f"⏭️  Skipped: {article.get('title', 'Unknown')[:50]}... (already enhanced)")
            
            # Progress indicator
            if i % 100 == 0:
                print(f"⏳ Processed {i}/{total_articles} articles... (Enhanced: {enhanced_count})")
        
        # Save enhanced articles
        try:
            with open(self.articles_file, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving articles: {e}")
            return {'error': f'Save failed: {str(e)}'}
        
        # Results summary
        results = {
            'total_articles': total_articles,
            'enhanced_count': enhanced_count,
            'skipped': skipped_count,
            'total_headers_enhanced': total_headers_enhanced,
            'total_metadata_changes': total_metadata_changes,
            'backup_file': self.backup_file,
            'success': True
        }
        
        print("\n" + "=" * 60)
        print("✅ Header Enhancement Complete!")
        print(f"📊 Total Articles: {total_articles}")
        print(f"✨ Enhanced: {enhanced_count} articles")
        print(f"📝 Headers Enhanced: {total_headers_enhanced}")
        print(f"🏷️  Metadata Updates: {total_metadata_changes}")
        print(f"⏭️  Skipped: {skipped_count} articles")
        print(f"💾 Backup: {self.backup_file}")
        print()
        print("🎯 Benefits:")
        print("   • Better SEO keyword optimization")
        print("   • Improved header structure")
        print("   • Enhanced content discoverability")
        print("   • Zero API costs (text processing only)")
        
        return results

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhance existing articles with keyword-optimized headers")
    parser.add_argument('--max-articles', type=int, help='Maximum number of articles to process (for testing)')
    parser.add_argument('--file', default='perplexityArticles_eeat_enhanced.json', help='Articles file to process')
    
    args = parser.parse_args()
    
    enhancer = ExistingArticleHeaderEnhancer(args.file)
    results = enhancer.enhance_all_articles(args.max_articles)
    
    if results.get('success'):
        print(f"\n🎉 Enhancement completed successfully!")
        return True
    else:
        print(f"\n❌ Enhancement failed: {results.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
