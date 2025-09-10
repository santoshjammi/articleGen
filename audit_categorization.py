#!/usr/bin/env python3
"""
Article Categorization Audit and Fix Script
Identifies and fixes miscategorized articles in the perplexityArticles_eeat_enhanced.json file
"""

import json
import os
from datetime import datetime

# Define mapping of subcategories that should be Technology or Business
TECH_SUBCATEGORIES = {
    'Agile Certifications', 'Agile Project Management', 'Agile Methodologies', 
    'Product Management', 'Emerging Technologies', 'Web Development', 
    'Digital Economy', 'Artificial Intelligence', 'Software Development',
    'Programming', 'DevOps', 'Cloud Computing', 'Cybersecurity', 'Data Science',
    'Machine Learning', 'Tech News', 'Mobile Development', 'API Development',
    'Database Management', 'System Administration', 'IT Management'
}

BUSINESS_SUBCATEGORIES = {
    'Digital Strategy', 'Marketing Strategy', 'Business Strategy', 'Digital Marketing',
    'International Business', 'Banking', 'Recruitment', 'Stock Market', 'Stock Analysis',
    'Personal Finance', 'Retail', 'Fast Food', 'Semiconductors', 'Project Management',
    'Business Analytics', 'E-commerce', 'Fintech', 'Startup', 'Entrepreneurship',
    'Corporate Strategy', 'Business Development', 'Sales', 'Customer Service',
    'Banking News'
}

def audit_categorization(filename):
    """Audit the categorization of articles and identify issues"""
    
    print("🔍 Starting categorization audit...")
    
    # Load the articles data
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        print(f"✅ Loaded {len(articles)} articles from {filename}")
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return None, None
    
    # Find miscategorized articles
    miscategorized = []
    world_category_stats = {}
    
    for i, article in enumerate(articles):
        if article.get('category') == 'World':
            subcategory = article.get('subCategory', '')
            
            # Count subcategories under World
            world_category_stats[subcategory] = world_category_stats.get(subcategory, 0) + 1
            
            # Check if should be recategorized
            should_be = None
            if subcategory in TECH_SUBCATEGORIES:
                should_be = 'Technology'
            elif subcategory in BUSINESS_SUBCATEGORIES:
                should_be = 'Business'
                
            if should_be:
                miscategorized.append({
                    'index': i,
                    'id': article.get('id'),
                    'title': article.get('title', ''),
                    'slug': article.get('slug'),
                    'current_category': article.get('category'),
                    'subcategory': subcategory,
                    'should_be': should_be
                })
    
    print(f"\n📊 AUDIT RESULTS:")
    print(f"Total articles: {len(articles)}")
    print(f"Articles categorized as 'World': {sum(1 for a in articles if a.get('category') == 'World')}")
    print(f"Miscategorized articles found: {len(miscategorized)}")
    
    print(f"\n📋 SUBCATEGORIES UNDER 'WORLD' (Top 20):")
    sorted_stats = sorted(world_category_stats.items(), key=lambda x: x[1], reverse=True)
    for subcategory, count in sorted_stats[:20]:
        status = ""
        if subcategory in TECH_SUBCATEGORIES:
            status = " → Should be TECHNOLOGY"
        elif subcategory in BUSINESS_SUBCATEGORIES:
            status = " → Should be BUSINESS"
        print(f"  {subcategory}: {count}{status}")
    
    print(f"\n🚨 MISCATEGORIZED ARTICLES:")
    for article in miscategorized[:10]:  # Show first 10
        print(f"  ID: {article['id']} | {article['should_be']} | {article['subcategory']}")
        print(f"    Title: {article['title'][:80]}...")
        print()
    
    if len(miscategorized) > 10:
        print(f"  ... and {len(miscategorized) - 10} more")
    
    return miscategorized, articles

def fix_categorization(miscategorized, articles, filename):
    """Fix the categorization issues"""
    
    if not miscategorized:
        print("✅ No miscategorized articles to fix!")
        return
    
    print(f"\n🔧 FIXING {len(miscategorized)} MISCATEGORIZED ARTICLES...")
    
    # Create backup
    backup_filename = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"✅ Backup created: {backup_filename}")
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return
    
    # Fix categorization
    fixes_applied = 0
    for issue in miscategorized:
        index = issue['index']
        if index < len(articles):
            old_category = articles[index]['category']
            articles[index]['category'] = issue['should_be']
            fixes_applied += 1
            print(f"  Fixed ID {issue['id']}: {old_category} → {issue['should_be']} ({issue['subcategory']})")
    
    # Save the fixed data
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"✅ Applied {fixes_applied} fixes to {filename}")
        
        # Verify the fixes
        print(f"\n🔍 VERIFICATION:")
        world_count = sum(1 for a in articles if a.get('category') == 'World')
        tech_count = sum(1 for a in articles if a.get('category') == 'Technology')
        business_count = sum(1 for a in articles if a.get('category') == 'Business')
        
        print(f"  Articles now categorized as 'World': {world_count}")
        print(f"  Articles now categorized as 'Technology': {tech_count}")
        print(f"  Articles now categorized as 'Business': {business_count}")
        
    except Exception as e:
        print(f"❌ Error saving fixes: {e}")

def main():
    """Main function"""
    filename = 'perplexityArticles_eeat_enhanced.json'
    
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        return
    
    # Audit categorization
    miscategorized, articles = audit_categorization(filename)
    
    if miscategorized is None:
        return
    
    # Ask user if they want to fix the issues
    if miscategorized:
        print(f"\n❓ Do you want to fix these {len(miscategorized)} categorization issues? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            fix_categorization(miscategorized, articles, filename)
        else:
            print("❌ Categorization fixes cancelled.")
    
    print("\n✅ Categorization audit completed!")

if __name__ == "__main__":
    main()
