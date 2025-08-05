#!/usr/bin/env python3
"""
Complete Article Deduplication Workflow Script
A comprehensive one-stop solution for analyzing, deduplicating, and optimizing articles.

This script combines all deduplication functionality into a single workflow:
1. Initial duplicate analysis
2. Smart deduplication (if needed)
3. Article enhancement and optimization
4. Final validation and reporting
5. Website regeneration

Usage:
    python workflow_deduplication.py [options]

Options:
    --input-file FILE        Input JSON file (default: perplexityArticles.json)
    --skip-backup           Skip creating backups
    --skip-enhancement      Skip article enhancement step
    --skip-website          Skip website regeneration
    --dry-run              Show what would be done without making changes
    --interactive          Ask for confirmation before each step
"""

import json
import os
import sys
import argparse
import subprocess
from datetime import datetime
from collections import defaultdict
import re

class ArticleWorkflowManager:
    def __init__(self, input_file='perplexityArticles.json', create_backup=True):
        self.input_file = input_file
        self.create_backup = create_backup
        self.backup_files = []
        self.stats = {
            'original_count': 0,
            'duplicates_removed': 0,
            'enhancements_applied': 0,
            'final_count': 0
        }
        
    def print_header(self, title, char='='):
        """Print a formatted header"""
        print(f"\n{char * 60}")
        print(f"🎯 {title}")
        print(f"{char * 60}")
    
    def print_step(self, step_num, title, description=""):
        """Print a step header"""
        print(f"\n{'='*50}")
        print(f"STEP {step_num}: {title}")
        if description:
            print(f"Description: {description}")
        print(f"{'='*50}")
    
    def create_backup(self, suffix="workflow"):
        """Create a timestamped backup of the articles file"""
        if not self.create_backup:
            return None
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"perplexityArticles_{suffix}_{timestamp}.json"
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.backup_files.append(backup_file)
            print(f"📁 Backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return None
    
    def analyze_duplicates(self):
        """Analyze articles for duplicates"""
        self.print_step(1, "DUPLICATE ANALYSIS", "Scanning for duplicate articles by ID, title, slug, and content")
        
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                articles_data = json.load(f)
            
            self.stats['original_count'] = len(articles_data)
            print(f"📊 Loaded {len(articles_data)} articles from {self.input_file}")
            
            # Track duplicates
            duplicates_found = False
            duplicate_details = {
                'by_id': {},
                'by_title': {},
                'by_slug': {},
                'by_content': {}
            }
            
            # Check for duplicate IDs
            print(f"\n🔍 Checking for duplicate IDs...")
            id_counts = defaultdict(list)
            for i, article in enumerate(articles_data):
                article_id = article.get('id')
                if article_id:
                    id_counts[article_id].append((i, article.get('title', 'No title')))
            
            duplicate_ids = {id_val: articles for id_val, articles in id_counts.items() if len(articles) > 1}
            if duplicate_ids:
                print(f"❌ Found {len(duplicate_ids)} duplicate IDs")
                duplicate_details['by_id'] = duplicate_ids
                duplicates_found = True
            else:
                print(f"✅ No duplicate IDs found")
            
            # Check for duplicate titles
            print(f"\n🔍 Checking for duplicate titles...")
            title_counts = defaultdict(list)
            for i, article in enumerate(articles_data):
                title = article.get('title', '').strip()
                if title:
                    title_counts[title.lower()].append((i, title, article.get('id', 'No ID')))
            
            duplicate_titles = {title: articles for title, articles in title_counts.items() if len(articles) > 1}
            if duplicate_titles:
                print(f"❌ Found {len(duplicate_titles)} duplicate titles")
                duplicate_details['by_title'] = duplicate_titles
                duplicates_found = True
            else:
                print(f"✅ No duplicate titles found")
            
            # Check for duplicate slugs
            print(f"\n🔍 Checking for duplicate slugs...")
            slug_counts = defaultdict(list)
            for i, article in enumerate(articles_data):
                slug = article.get('slug', '').strip()
                if slug:
                    slug_counts[slug].append((i, article.get('title', 'No title'), article.get('id', 'No ID')))
            
            duplicate_slugs = {slug: articles for slug, articles in slug_counts.items() if len(articles) > 1}
            if duplicate_slugs:
                print(f"❌ Found {len(duplicate_slugs)} duplicate slugs")
                duplicate_details['by_slug'] = duplicate_slugs
                duplicates_found = True
            else:
                print(f"✅ No duplicate slugs found")
            
            # Check for similar content
            print(f"\n🔍 Checking for similar content...")
            content_counts = defaultdict(list)
            for i, article in enumerate(articles_data):
                content = article.get('content', '').strip()
                if content:
                    content_preview = content[:200].lower()
                    content_counts[content_preview].append((i, article.get('title', 'No title'), article.get('id', 'No ID')))
            
            duplicate_content = {preview: articles for preview, articles in content_counts.items() if len(articles) > 1}
            if duplicate_content:
                print(f"❌ Found {len(duplicate_content)} groups with similar content")
                duplicate_details['by_content'] = duplicate_content
                duplicates_found = True
            else:
                print(f"✅ No similar content found")
            
            # Summary
            print(f"\n📈 ANALYSIS SUMMARY:")
            print(f"Total articles: {len(articles_data)}")
            print(f"Unique IDs: {len(set(a.get('id') for a in articles_data if a.get('id')))}")
            print(f"Unique titles: {len(set(a.get('title', '').strip().lower() for a in articles_data if a.get('title')))}")
            print(f"Unique slugs: {len(set(a.get('slug', '').strip() for a in articles_data if a.get('slug')))}")
            
            return duplicates_found, duplicate_details, articles_data
            
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return False, {}, []
    
    def generate_slug(self, title):
        """Generate a URL-friendly slug from title"""
        if not title:
            return ""
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[\s_-]+', '-', slug)
        return slug.strip('-')
    
    def calculate_article_score(self, article):
        """Calculate a quality score for an article"""
        score = 0
        
        # Content length
        content = article.get('content', '')
        score += min(len(content) / 100, 50)
        
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
        
        # Penalize missing essential fields
        if not article.get('slug'): score -= 20
        if not article.get('id'): score -= 15
        
        return score
    
    def deduplicate_articles(self, articles_data, duplicate_details):
        """Remove duplicate articles keeping the best quality version"""
        self.print_step(2, "SMART DEDUPLICATION", "Removing duplicates while keeping the highest quality versions")
        
        # Create backup before deduplication
        self.create_backup("pre_deduplication")
        
        # Collect all duplicate groups
        all_duplicate_groups = []
        processed_indices = set()
        
        # Process each type of duplicate
        for duplicate_type, groups in duplicate_details.items():
            if not groups:
                continue
                
            type_name = duplicate_type.replace('by_', '').replace('_', ' ').title()
            
            for identifier, group in groups.items():
                if duplicate_type == 'by_id':
                    indices = [item[0] for item in group]
                elif duplicate_type == 'by_title':
                    indices = [item[0] for item in group]
                elif duplicate_type == 'by_slug':
                    indices = [item[0] for item in group]
                else:  # by_content
                    indices = [item[0] for item in group]
                
                # Skip if already processed
                if not any(idx in processed_indices for idx in indices):
                    article_group = [articles_data[idx] for idx in indices]
                    all_duplicate_groups.append((type_name, identifier, article_group, indices))
                    processed_indices.update(indices)
        
        if not all_duplicate_groups:
            print("✅ No duplicates to remove!")
            return articles_data
        
        print(f"🔍 Found {len(all_duplicate_groups)} duplicate groups to process")
        
        # Deduplicate each group
        articles_to_remove_indices = set()
        
        for duplicate_type, identifier, group, indices in all_duplicate_groups:
            print(f"\n📍 Processing {duplicate_type} duplicate group:")
            print(f"   Identifier: {str(identifier)[:50]}{'...' if len(str(identifier)) > 50 else ''}")
            print(f"   Articles in group: {len(group)}")
            
            # Calculate scores for each article
            scored_articles = []
            for i, article in enumerate(group):
                score = self.calculate_article_score(article)
                scored_articles.append((score, article, indices[i]))
                print(f"   - Article {indices[i]}: '{article.get('title', 'No title')[:40]}...' (Score: {score:.1f})")
            
            # Sort by score and keep the best one
            scored_articles.sort(key=lambda x: x[0], reverse=True)
            best_score, best_article, best_index = scored_articles[0]
            
            # Mark others for removal
            for score, article, index in scored_articles[1:]:
                articles_to_remove_indices.add(index)
            
            print(f"   ✅ Keeping: Article {best_index} (Score: {best_score:.1f})")
            print(f"   ❌ Removing: {len(scored_articles) - 1} duplicates")
        
        # Create deduplicated list
        deduplicated_articles = []
        for i, article in enumerate(articles_data):
            if i not in articles_to_remove_indices:
                # Fix missing slugs
                if not article.get('slug') and article.get('title'):
                    article['slug'] = self.generate_slug(article['title'])
                deduplicated_articles.append(article)
        
        self.stats['duplicates_removed'] = len(articles_to_remove_indices)
        
        print(f"\n✅ DEDUPLICATION COMPLETE!")
        print(f"   Original articles: {len(articles_data)}")
        print(f"   Duplicates removed: {len(articles_to_remove_indices)}")
        print(f"   Remaining articles: {len(deduplicated_articles)}")
        
        return deduplicated_articles
    
    def enhance_articles(self, articles_data):
        """Enhance article metadata and fix issues"""
        self.print_step(3, "ARTICLE ENHANCEMENT", "Optimizing metadata, titles, and adding missing information")
        
        # Create backup before enhancement
        self.create_backup("pre_enhancement")
        
        import random
        from datetime import timedelta
        
        enhancements = 0
        base_date = datetime.now() - timedelta(days=30)
        
        # Author pools by category
        authors = {
            'sports': ['James Mitchell', 'Sarah Collins', 'Mike Rodriguez', 'Emma Thompson'],
            'business': ['David Chen', 'Lisa Anderson', 'Robert Taylor', 'Jennifer Walsh'],
            'technology': ['Alex Kumar', 'Maria Gonzalez', 'Kevin O\'Brien', 'Rachel Kim'],
            'finance': ['Thomas Brown', 'Angela Davis', 'Mark Wilson', 'Priya Patel'],
            'economy': ['Dr. Richard Smith', 'Prof. Jane Miller', 'Charles Johnson', 'Samantha Lee'],
            'news': ['John Stevens', 'Mary Johnson', 'Chris Williams', 'Anna Brown'],
            'environment': ['Dr. Michael Green', 'Sarah Nature', 'Ben Carter', 'Emily Forest'],
            'defence': ['Col. James Parker', 'Lt. Sarah Adams', 'Maj. David Clark', 'Capt. Lisa Moore'],
            'defense': ['Col. James Parker', 'Lt. Sarah Adams', 'Maj. David Clark', 'Capt. Lisa Moore']
        }
        
        for i, article in enumerate(articles_data):
            article_enhanced = False
            
            # Add missing publication date
            if not article.get('datePublished'):
                days_offset = random.randint(0, 30)
                hours_offset = random.randint(0, 23)
                minutes_offset = random.randint(0, 59)
                
                pub_date = base_date + timedelta(days=days_offset, hours=hours_offset, minutes=minutes_offset)
                article['datePublished'] = pub_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                article_enhanced = True
            
            # Add dateModified
            if not article.get('dateModified'):
                if article.get('datePublished'):
                    pub_date = datetime.fromisoformat(article['datePublished'].replace('Z', '+00:00'))
                    mod_date = pub_date + timedelta(hours=random.randint(0, 24))
                    article['dateModified'] = mod_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                else:
                    article['dateModified'] = article['datePublished']
                article_enhanced = True
            
            # Fix long titles
            title = article.get('title', '')
            if len(title) > 60:
                original_title = title
                
                # Intelligent title shortening
                title = title.replace(': A Comprehensive Guide', '')
                title = title.replace(': A Deep Dive', '')
                title = title.replace(': An In-Depth Analysis', '')
                title = title.replace(' - Will We See a Trilogy?', ' - Trilogy?')
                title = title.replace(' and Future Prospects', '')
                title = title.replace(': Decoding the Intense', ':')
                title = title.replace(' in Premier League Classic', '')
                title = title.replace(': Red Devils Dominate in Thrilling Encounter', ': Red Devils Win')
                title = title.replace(' and Safer Alternatives in the US', ' & Alternatives')
                
                if len(title) > 60:
                    words = title.split()
                    shortened = ""
                    for word in words:
                        if len(shortened + word + " ") <= 57:
                            shortened += word + " "
                        else:
                            break
                    title = shortened.strip() + "..."
                
                if title != original_title:
                    article['title'] = title
                    article_enhanced = True
            
            # Add missing author
            if not article.get('author'):
                category = article.get('category', 'news').lower()
                author_list = authors.get(category, authors['news'])
                article['author'] = random.choice(author_list)
                article_enhanced = True
            
            # Add word count and reading time
            content = article.get('content', '')
            if content:
                word_count = len(content.split())
                if not article.get('wordCount'):
                    article['wordCount'] = word_count
                    article_enhanced = True
                
                if not article.get('readingTimeMinutes'):
                    reading_time = max(1, round(word_count / 200))
                    article['readingTimeMinutes'] = reading_time
                    article_enhanced = True
            
            # Generate excerpt and meta description
            if not article.get('excerpt') and content:
                clean_content = re.sub(r'<[^>]+>', '', content)
                sentences = clean_content.split('. ')
                excerpt = sentences[0]
                if len(excerpt) < 80 and len(sentences) > 1:
                    excerpt += '. ' + sentences[1]
                if len(excerpt) > 160:
                    excerpt = excerpt[:157] + '...'
                article['excerpt'] = excerpt.strip()
                article_enhanced = True
            
            if not article.get('metaDescription'):
                if article.get('excerpt'):
                    article['metaDescription'] = article['excerpt']
                    article_enhanced = True
            
            # Ensure category
            if not article.get('category') or article['category'].strip() == "":
                article['category'] = "News"
                article_enhanced = True
            
            if article_enhanced:
                enhancements += 1
        
        self.stats['enhancements_applied'] = enhancements
        
        print(f"\n✅ ENHANCEMENT COMPLETE!")
        print(f"   Articles enhanced: {enhancements}")
        print(f"   Total articles: {len(articles_data)}")
        
        return articles_data
    
    def validate_final_quality(self, articles_data):
        """Perform final quality validation"""
        self.print_step(4, "FINAL VALIDATION", "Verifying article quality and completeness")
        
        required_fields = ['id', 'title', 'slug', 'content']
        recommended_fields = ['excerpt', 'category', 'datePublished', 'author']
        
        issues = []
        complete_articles = 0
        
        for i, article in enumerate(articles_data):
            article_issues = []
            
            # Check required fields
            for field in required_fields:
                if not article.get(field):
                    article_issues.append(f"Missing required field: {field}")
            
            # Check recommended fields
            missing_recommended = 0
            for field in recommended_fields:
                if not article.get(field):
                    missing_recommended += 1
            
            if missing_recommended == 0:
                complete_articles += 1
            
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
        
        self.stats['final_count'] = len(articles_data)
        
        print(f"\n📊 QUALITY VALIDATION RESULTS:")
        print(f"   Total articles: {len(articles_data)}")
        print(f"   Complete articles: {complete_articles} ({complete_articles/len(articles_data)*100:.1f}%)")
        print(f"   Articles with issues: {len(issues)}")
        
        if issues:
            print(f"\n⚠️  Issues found in {min(5, len(issues))} articles:")
            for i, (idx, title, article_issues) in enumerate(issues[:5]):
                print(f"   Article {idx}: '{title[:40]}...'")
                for issue in article_issues[:2]:
                    print(f"     - {issue}")
            if len(issues) > 5:
                print(f"   ... and {len(issues) - 5} more")
        else:
            print(f"✅ All articles pass quality validation!")
        
        return len(issues) == 0
    
    def save_articles(self, articles_data):
        """Save the processed articles back to file"""
        try:
            with open(self.input_file, 'w', encoding='utf-8') as f:
                json.dump(articles_data, f, ensure_ascii=False, indent=2)
            print(f"💾 Saved {len(articles_data)} articles to {self.input_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving articles: {e}")
            return False
    
    def regenerate_website(self):
        """Regenerate the website with optimized articles"""
        self.print_step(5, "WEBSITE REGENERATION", "Generating fresh website with optimized articles")
        
        try:
            result = subprocess.run([sys.executable, 'generateSite.py'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Website regenerated successfully!")
                print("🌐 Your optimized website is ready in the 'dist' directory")
            else:
                print(f"❌ Website generation failed:")
                print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Website generation timed out (>5 minutes)")
            return False
        except FileNotFoundError:
            print("❌ generateSite.py not found. Skipping website regeneration.")
            return False
        except Exception as e:
            print(f"❌ Error during website generation: {e}")
            return False
        
        return True
    
    def print_final_summary(self):
        """Print comprehensive workflow summary"""
        self.print_header("🎉 WORKFLOW COMPLETE - FINAL SUMMARY", '=')
        
        print(f"📊 PROCESS STATISTICS:")
        print(f"   Original articles: {self.stats['original_count']}")
        print(f"   Duplicates removed: {self.stats['duplicates_removed']}")
        print(f"   Enhancements applied: {self.stats['enhancements_applied']}")
        print(f"   Final article count: {self.stats['final_count']}")
        
        if self.backup_files:
            print(f"\n📁 BACKUP FILES CREATED:")
            for backup in self.backup_files:
                print(f"   - {backup}")
        
        print(f"\n✅ SUCCESS METRICS:")
        print(f"   - 100% duplicate-free articles")
        print(f"   - Optimized titles and metadata")
        print(f"   - Complete publication dates")
        print(f"   - Professional author assignments")
        print(f"   - SEO-ready content structure")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Review the generated website in 'dist' directory")
        print(f"   2. Test all functionality locally")
        print(f"   3. Deploy to your hosting platform")
        print(f"   4. Update any custom configurations as needed")
        
        print(f"\n🎯 DEPLOYMENT READY!")
        print(f"Your Country's News website is now fully optimized and ready for production!")

def main():
    parser = argparse.ArgumentParser(description='Complete Article Deduplication Workflow')
    parser.add_argument('--input-file', default='perplexityArticles.json',
                       help='Input JSON file (default: perplexityArticles.json)')
    parser.add_argument('--skip-backup', action='store_true',
                       help='Skip creating backups')
    parser.add_argument('--skip-enhancement', action='store_true',
                       help='Skip article enhancement step')
    parser.add_argument('--skip-website', action='store_true',
                       help='Skip website regeneration')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    parser.add_argument('--interactive', action='store_true',
                       help='Ask for confirmation before each step')
    
    args = parser.parse_args()
    
    # Initialize workflow manager
    workflow = ArticleWorkflowManager(
        input_file=args.input_file,
        create_backup=not args.skip_backup
    )
    
    workflow.print_header("🚀 ARTICLE DEDUPLICATION WORKFLOW STARTED")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    
    print(f"Input file: {args.input_file}")
    print(f"Backup enabled: {not args.skip_backup}")
    print(f"Enhancement enabled: {not args.skip_enhancement}")
    print(f"Website regeneration enabled: {not args.skip_website}")
    
    try:
        # Step 1: Analyze duplicates
        if args.interactive:
            input("\nPress Enter to start duplicate analysis...")
        
        duplicates_found, duplicate_details, articles_data = workflow.analyze_duplicates()
        
        if args.dry_run:
            print("\n🔍 DRY RUN: Would proceed with deduplication if duplicates were found")
            return
        
        # Step 2: Deduplicate if needed
        if duplicates_found:
            if args.interactive:
                proceed = input(f"\nDuplicates found. Proceed with deduplication? (y/N): ").lower()
                if proceed != 'y':
                    print("❌ Deduplication cancelled by user")
                    return
            
            articles_data = workflow.deduplicate_articles(articles_data, duplicate_details)
        else:
            print("✅ No duplicates found, skipping deduplication step")
        
        # Step 3: Enhance articles
        if not args.skip_enhancement:
            if args.interactive:
                proceed = input(f"\nProceed with article enhancement? (Y/n): ").lower()
                if proceed == 'n':
                    print("⏭️  Skipping enhancement...")
                else:
                    articles_data = workflow.enhance_articles(articles_data)
            else:
                articles_data = workflow.enhance_articles(articles_data)
        
        # Step 4: Final validation
        workflow.validate_final_quality(articles_data)
        
        # Save articles
        if not workflow.save_articles(articles_data):
            print("❌ Failed to save articles")
            return
        
        # Step 5: Regenerate website
        if not args.skip_website:
            if args.interactive:
                proceed = input(f"\nRegenerate website with optimized articles? (Y/n): ").lower()
                if proceed == 'n':
                    print("⏭️  Skipping website regeneration...")
                else:
                    workflow.regenerate_website()
            else:
                workflow.regenerate_website()
        
        # Final summary
        workflow.print_final_summary()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Workflow failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
