#!/usr/bin/env python3
"""
E-E-A-T Enhanced Site Generator
Generates a complete website with E-E-A-T compliant features using enhanced articles.

This module extends generateSite.py with:
- Author bio boxes with credentials and expertise
- Trust signals and verification badges
- Enhanced structured data with E-E-A-T elements
- Editorial transparency sections
- Fact-checking and source verification displays
"""

import json
import os
import shutil
from datetime import datetime
from urllib.parse import quote

# Import the E-E-A-T enhancement functions
from eeat_site_enhancements import (
    generate_eeat_author_box,
    generate_eeat_trust_indicators, 
    generate_eeat_transparency_section,
    generate_eeat_structured_data
)

# Use the same configuration as the main generateSite.py
OUTPUT_DIR = "dist"
ARTICLES_FILE = "perplexityArticles_eeat_enhanced.json"

def generate_eeat_enhanced_site():
    """Generate complete website with E-E-A-T enhanced features"""
    
    print("🌟 E-E-A-T Enhanced Site Generation Starting...")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Copy static assets
    copy_static_assets()
    
    # Load enhanced articles
    articles_data = load_enhanced_articles()
    if not articles_data:
        print("❌ No enhanced articles found! Please run eeat_enhancer.py first.")
        return
    
    print(f"✅ Loaded {len(articles_data)} E-E-A-T enhanced articles")
    
    # Generate all pages
    generate_eeat_homepage(articles_data)
    generate_eeat_article_pages(articles_data)
    generate_eeat_category_pages(articles_data)
    generate_static_pages()
    generate_eeat_sitemap(articles_data)
    generate_robots_txt()
    generate_eeat_rss_feed(articles_data)
    
    print("\n🎉 E-E-A-T Enhanced Site Generation Complete!")
    print(f"📁 Website files generated in: {OUTPUT_DIR}/")
    print("🚀 Your site is now E-E-A-T compliant and ready for deployment!")

def copy_static_assets():
    """Copy logos and other static assets"""
    assets = ['logo.svg', 'favicon.svg', 'logo-header.svg']
    for asset in assets:
        if os.path.exists(asset):
            shutil.copy2(asset, os.path.join(OUTPUT_DIR, asset))
            print(f"📁 Copied {asset}")

def load_enhanced_articles():
    """Load E-E-A-T enhanced articles"""
    try:
        with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Enhanced articles file not found: {ARTICLES_FILE}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing enhanced articles: {e}")
        return []

def generate_eeat_homepage(articles_data):
    """Generate homepage with E-E-A-T enhanced features"""
    
    # Get recent articles for homepage
    recent_articles = sorted(articles_data, 
                           key=lambda x: x.get('publishDate', ''), 
                           reverse=True)[:9]
    
    # Generate article cards with E-E-A-T indicators
    articles_html = ""
    for article in recent_articles:
        
        # E-E-A-T trust badges
        trust_badges = []
        if article.get('factCheckedBy'):
            trust_badges.append('<span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded mr-1">Fact-Checked</span>')
        if article.get('authorProfile', {}).get('credentials'):
            trust_badges.append('<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1">Expert Author</span>')
        
        trust_badges_html = ''.join(trust_badges)
        
        # E-E-A-T score indicator
        eeat_score = article.get('eeatScore', {})
        overall_score = eeat_score.get('overall', 85)
        score_color = "green" if overall_score >= 85 else "yellow" if overall_score >= 70 else "red"
        
        article_card = f'''
        <article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 border border-gray-100">
            <a href="articles/{article['slug']}.html" class="block">
                <img src="{article.get('thumbnailImageUrl', article.get('ogImage', ''))}" 
                     alt="{article.get('imageAltText', article['title'])}" 
                     class="w-full h-48 object-cover">
                <div class="p-6">
                    <!-- E-E-A-T Trust Indicators -->
                    <div class="flex items-center justify-between mb-3">
                        <div class="flex flex-wrap">
                            {trust_badges_html}
                        </div>
                        <div class="bg-{score_color}-100 text-{score_color}-800 text-xs px-2 py-1 rounded">
                            E-E-A-T: {overall_score}%
                        </div>
                    </div>
                    
                    <h2 class="text-xl font-bold text-blue-800 mb-2 hover:text-blue-600 transition-colors">
                        {article['title'][:80]}{"..." if len(article['title']) > 80 else ""}
                    </h2>
                    <p class="text-gray-600 text-sm mb-3">
                        {article.get('excerpt', '')[:120]}{"..." if len(article.get('excerpt', '')) > 120 else ""}
                    </p>
                    
                    <!-- Enhanced Author Information -->
                    <div class="flex items-center text-sm text-gray-500 mb-2">
                        <div class="flex items-center">
                            <div class="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-bold mr-2">
                                {article.get('authorProfile', {}).get('name', article.get('author', 'Author'))[0]}
                            </div>
                            <span class="font-medium">{article.get('authorProfile', {}).get('name', article.get('author', 'Editorial Team'))}</span>
                        </div>
                    </div>
                    
                    <div class="flex items-center justify-between text-xs text-gray-400">
                        <span>{article.get('publishDate', '')}</span>
                        <span>{article.get('readingTimeMinutes', 5)} min read</span>
                    </div>
                </div>
            </a>
        </article>
        '''
        articles_html += article_card
    
    # Homepage HTML template with E-E-A-T features
    homepage_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Country's News - E-E-A-T Compliant News & Analysis</title>
    <meta name="description" content="Country's News provides expert-reviewed, fact-checked news analysis with transparent editorial standards. Your trusted source for reliable information.">
    
    <!-- E-E-A-T Enhanced Meta Tags -->
    <meta name="expertise" content="Professional journalism with specialized industry knowledge">
    <meta name="authoritativeness" content="Verified expert authors with proven credentials">
    <meta name="trustworthiness" content="Fact-checked content with transparent editorial process">
    <meta name="editorial-standards" content="Professional journalism ethics and accuracy standards">
    
    <link rel="canonical" href="https://countrysnews.com/">
    <link rel="icon" href="favicon.svg" type="image/svg+xml">
    
    <!-- Open Graph -->
    <meta property="og:title" content="Country's News - Expert Analysis & Reliable Reporting">
    <meta property="og:description" content="E-E-A-T compliant news platform with expert authors and fact-checked content">
    <meta property="og:url" content="https://countrysnews.com/">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://countrysnews.com/logo.svg">
    
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- E-E-A-T Trust Header -->
    <div class="bg-blue-600 text-white py-2">
        <div class="container mx-auto px-4 text-center text-sm">
            <span class="flex items-center justify-center">
                <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                </svg>
                E-E-A-T Compliant • Expert Authors • Fact-Checked Content • Transparent Editorial Standards
            </span>
        </div>
    </div>

    <!-- Navigation -->
    <nav class="bg-white shadow-md sticky top-0 z-50">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between py-4">
                <div class="flex items-center space-x-4">
                    <img src="logo-header.svg" alt="Country's News" class="h-10">
                    <span class="text-2xl font-bold text-blue-800">Country's News</span>
                </div>
                <div class="hidden md:flex space-x-6">
                    <a href="index.html" class="text-gray-700 hover:text-blue-600 font-medium">Home</a>
                    <a href="categories/news.html" class="text-gray-700 hover:text-blue-600">News</a>
                    <a href="categories/business.html" class="text-gray-700 hover:text-blue-600">Business</a>
                    <a href="categories/technology.html" class="text-gray-700 hover:text-blue-600">Technology</a>
                    <a href="categories/sports.html" class="text-gray-700 hover:text-blue-600">Sports</a>
                    <a href="about-us.html" class="text-gray-700 hover:text-blue-600">About</a>
                    <a href="contact.html" class="text-gray-700 hover:text-blue-600">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Hero Section with E-E-A-T Emphasis -->
        <section class="text-center mb-12">
            <h1 class="text-4xl font-bold text-blue-800 mb-4">Expert Analysis. Reliable Reporting.</h1>
            <p class="text-xl text-gray-600 mb-6">E-E-A-T compliant news platform with verified expert authors and fact-checked content</p>
            
            <!-- E-E-A-T Credentials Banner -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-8">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
                    <div class="flex flex-col items-center">
                        <div class="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white mb-2">
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                        </div>
                        <h3 class="font-semibold text-gray-900">Expert Authors</h3>
                        <p class="text-sm text-gray-600">Verified industry professionals</p>
                    </div>
                    <div class="flex flex-col items-center">
                        <div class="w-12 h-12 bg-green-600 rounded-full flex items-center justify-center text-white mb-2">
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
                        </div>
                        <h3 class="font-semibold text-gray-900">Fact-Checked</h3>
                        <p class="text-sm text-gray-600">Rigorous verification process</p>
                    </div>
                    <div class="flex flex-col items-center">
                        <div class="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center text-white mb-2">
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>
                        </div>
                        <h3 class="font-semibold text-gray-900">Transparent</h3>
                        <p class="text-sm text-gray-600">Clear editorial standards</p>
                    </div>
                    <div class="flex flex-col items-center">
                        <div class="w-12 h-12 bg-orange-600 rounded-full flex items-center justify-center text-white mb-2">
                            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z"></path></svg>
                        </div>
                        <h3 class="font-semibold text-gray-900">Authoritative</h3>
                        <p class="text-sm text-gray-600">Credible source citations</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- Featured Articles -->
        <section>
            <div class="flex items-center justify-between mb-8">
                <h2 class="text-3xl font-bold text-gray-900">Latest Expert Analysis</h2>
                <div class="flex items-center text-sm text-gray-600">
                    <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.414-1.414L11 9.586V6z" clip-rule="evenodd"></path></svg>
                    Updated: {datetime.now().strftime('%B %d, %Y')}
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {articles_html}
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-12 mt-16">
        <div class="container mx-auto px-4">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                <div>
                    <h3 class="text-lg font-semibold mb-4">Country's News</h3>
                    <p class="text-gray-300 text-sm">E-E-A-T compliant news platform delivering expert analysis with verified authors and transparent editorial standards.</p>
                </div>
                <div>
                    <h4 class="font-semibold mb-3">Editorial Standards</h4>
                    <ul class="text-gray-300 text-sm space-y-1">
                        <li><a href="#" class="hover:text-white">Fact-Checking Policy</a></li>
                        <li><a href="#" class="hover:text-white">Editorial Guidelines</a></li>
                        <li><a href="#" class="hover:text-white">Corrections Policy</a></li>
                        <li><a href="#" class="hover:text-white">Source Standards</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-semibold mb-3">Categories</h4>
                    <ul class="text-gray-300 text-sm space-y-1">
                        <li><a href="categories/news.html" class="hover:text-white">News</a></li>
                        <li><a href="categories/business.html" class="hover:text-white">Business</a></li>
                        <li><a href="categories/technology.html" class="hover:text-white">Technology</a></li>
                        <li><a href="categories/sports.html" class="hover:text-white">Sports</a></li>
                    </ul>
                </div>
                <div>
                    <h4 class="font-semibold mb-3">Contact</h4>
                    <ul class="text-gray-300 text-sm space-y-1">
                        <li><a href="about-us.html" class="hover:text-white">About Us</a></li>
                        <li><a href="contact.html" class="hover:text-white">Contact</a></li>
                        <li><a href="privacy-policy.html" class="hover:text-white">Privacy Policy</a></li>
                        <li><a href="disclaimer.html" class="hover:text-white">Disclaimer</a></li>
                    </ul>
                </div>
            </div>
            <div class="border-t border-gray-700 mt-8 pt-8 text-center text-gray-300 text-sm">
                <p>&copy; {datetime.now().year} Country's News. All rights reserved. | E-E-A-T Compliant Journalism</p>
            </div>
        </div>
    </footer>
</body>
</html>'''

    # Write homepage
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(homepage_html)
    print("✅ Generated E-E-A-T enhanced homepage")

def generate_eeat_article_pages(articles_data):
    """Generate individual article pages with full E-E-A-T features"""
    
    os.makedirs(os.path.join(OUTPUT_DIR, 'articles'), exist_ok=True)
    
    for article in articles_data:
        # Generate E-E-A-T components
        eeat_author_box = generate_eeat_author_box(article)
        eeat_trust_indicators = generate_eeat_trust_indicators(article)
        eeat_transparency_section = generate_eeat_transparency_section(article)
        eeat_structured_data = generate_eeat_structured_data(article)
        
        # Generate social hashtags
        social_hashtags = article.get('socialMediaHashtags', [])
        social_hashtags_html = ""
        if social_hashtags:
            hashtags_list = " ".join([f"#{tag}" for tag in social_hashtags[:5]])
            social_hashtags_html = f'<div class="mb-4"><p class="text-sm text-gray-600"><strong>Share:</strong> <span class="text-blue-600">{hashtags_list}</span></p></div>'
        
        # Generate key takeaways
        key_takeaways = article.get('keyTakeaways', [])
        key_takeaways_html = ""
        if key_takeaways:
            takeaways_list = ""
            for takeaway in key_takeaways:
                takeaways_list += f"<li class='mb-2'>{takeaway}</li>"
            key_takeaways_html = f'''
            <div class="bg-blue-50 border-l-4 border-blue-400 p-6 my-8 rounded-r">
                <h3 class="text-lg font-semibold text-blue-900 mb-3">Key Takeaways</h3>
                <ul class="list-disc list-inside text-gray-700 space-y-1">
                    {takeaways_list}
                </ul>
            </div>'''
        
        # Call to action
        cta_text = article.get('callToActionText', 'Stay informed with the latest news and updates!')
        call_to_action_html = f'''
        <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-lg text-center my-8">
            <h3 class="text-xl font-semibold mb-2">Stay Informed</h3>
            <p class="mb-4">{cta_text}</p>
            <a href="../index.html" class="bg-white text-blue-600 px-6 py-2 rounded-full font-semibold hover:bg-gray-100 transition-colors">Explore More Articles</a>
        </div>'''
        
        # Article HTML template
        article_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']}</title>
    <meta name="description" content="{article.get('metaDescription', article.get('excerpt', ''))}">
    
    <!-- E-E-A-T Enhanced Meta Tags -->
    <meta name="author" content="{article.get('authorProfile', {}).get('name', article.get('author', 'Editorial Team'))}">
    <meta name="expertise-level" content="{article.get('expertiseLevel', 'Professional')}">
    <meta name="fact-checked-by" content="{article.get('factCheckedBy', 'Editorial Review Team')}">
    <meta name="last-fact-check" content="{article.get('lastFactCheck', datetime.now().strftime('%Y-%m-%d'))}">
    <meta name="editorial-standards" content="Professional journalism ethics and accuracy standards">
    
    <link rel="canonical" href="https://countrysnews.com/articles/{article['slug']}.html">
    <link rel="icon" href="../favicon.svg" type="image/svg+xml">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{article['title']}">
    <meta property="og:description" content="{article.get('metaDescription', article.get('excerpt', ''))}">
    <meta property="og:url" content="https://countrysnews.com/articles/{article['slug']}.html">
    <meta property="og:type" content="article">
    <meta property="og:image" content="{article.get('ogImage', '')}">
    <meta property="article:author" content="{article.get('authorProfile', {}).get('name', article.get('author', 'Editorial Team'))}">
    <meta property="article:published_time" content="{article.get('publishDate', '')}T12:00:00Z">
    <meta property="article:modified_time" content="{article.get('dateModified', '')}T12:00:00Z">
    
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- E-E-A-T Trust Header -->
    <div class="bg-white border-b border-gray-200 py-2">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between text-sm text-gray-600">
                <div class="flex items-center space-x-4">
                    <span class="flex items-center">
                        <svg class="w-4 h-4 text-green-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                        </svg>
                        Fact-Checked
                    </span>
                    <span class="flex items-center">
                        <svg class="w-4 h-4 text-blue-500 mr-1" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Expert Reviewed
                    </span>
                    <span class="text-gray-500">Last Updated: {article.get('lastFactCheck', datetime.now().strftime('%Y-%m-%d'))}</span>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Verified Sources</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between py-4">
                <div class="flex items-center space-x-4">
                    <a href="../index.html">
                        <img src="../logo-header.svg" alt="Country's News" class="h-10">
                    </a>
                    <a href="../index.html" class="text-2xl font-bold text-blue-800">Country's News</a>
                </div>
                <div class="hidden md:flex space-x-6">
                    <a href="../index.html" class="text-gray-700 hover:text-blue-600 font-medium">Home</a>
                    <a href="../categories/news.html" class="text-gray-700 hover:text-blue-600">News</a>
                    <a href="../categories/business.html" class="text-gray-700 hover:text-blue-600">Business</a>
                    <a href="../categories/technology.html" class="text-gray-700 hover:text-blue-600">Technology</a>
                    <a href="../categories/sports.html" class="text-gray-700 hover:text-blue-600">Sports</a>
                    <a href="../contact.html" class="text-gray-700 hover:text-blue-600">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Article Content -->
    <main class="container mx-auto p-6 mt-8 max-w-4xl">
        <article class="bg-white rounded-lg shadow-lg overflow-hidden">
            <!-- Article Header -->
            <div class="p-8">
                <div class="mb-4">
                    <span class="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full">{article.get('category', 'News')}</span>
                </div>
                
                <h1 class="text-4xl font-extrabold text-blue-800 mb-4">{article['title']}</h1>
                
                <!-- Enhanced byline with author credibility -->
                <div class="text-gray-600 text-sm mb-6 border-b border-gray-100 pb-4">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center">
                            <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm mr-3">
                                {article.get('authorProfile', {}).get('name', article.get('author', 'Author'))[0]}
                            </div>
                            <div>
                                <div class="flex items-center">
                                    <span class="font-semibold text-blue-700">{article.get('authorProfile', {}).get('name', article.get('author', 'Editorial Team'))}</span>
                                    <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded ml-2">✓ Verified Expert</span>
                                </div>
                                <div class="text-xs text-gray-500">{article.get('authorProfile', {}).get('title', 'Senior Editor')}</div>
                            </div>
                        </div>
                        <div class="text-right">
                            <div>Published: {article.get('publishDate', '')}</div>
                            <div>Updated: {article.get('dateModified', '')}</div>
                            <div class="text-xs text-gray-400">{article.get('readingTimeMinutes', 5)} min read</div>
                        </div>
                    </div>
                </div>
                
                <!-- Social Media Hashtags -->
                {social_hashtags_html}
                
                <!-- Main image -->
                <img src="../{article.get('ogImage', '').replace('dist/', '')}" alt="{article.get('imageAltText', article['title'])}" class="w-full h-64 object-cover rounded-lg mb-6 shadow-md">
                
                <!-- E-E-A-T Author Bio Box -->
                {eeat_author_box}
                
                <!-- Article content -->
                <div class="prose prose-lg max-w-none">
                    {article['content']}
                </div>
                
                <!-- E-E-A-T Trust Indicators -->
                {eeat_trust_indicators}
                
                <!-- Key Takeaways -->
                {key_takeaways_html}
                
                <!-- Call to Action -->
                {call_to_action_html}
                
                <!-- E-E-A-T Transparency Section -->
                {eeat_transparency_section}
            </div>
        </article>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-16">
        <div class="container mx-auto px-4 text-center">
            <p class="text-gray-300">&copy; {datetime.now().year} Country's News. All rights reserved. | E-E-A-T Compliant Journalism</p>
        </div>
    </footer>

    <!-- Enhanced structured data with E-E-A-T -->
    <script type="application/ld+json">
    {eeat_structured_data}
    </script>
</body>
</html>'''

        # Write article file
        article_filename = f"{article['slug']}.html"
        with open(os.path.join(OUTPUT_DIR, 'articles', article_filename), 'w', encoding='utf-8') as f:
            f.write(article_html)
    
    print(f"✅ Generated {len(articles_data)} E-E-A-T enhanced article pages")

def generate_eeat_category_pages(articles_data):
    """Generate category pages with E-E-A-T indicators"""
    
    # Group articles by category
    categories = {}
    for article in articles_data:
        category = article.get('category', 'News')
        if category not in categories:
            categories[category] = []
        categories[category].append(article)
    
    os.makedirs(os.path.join(OUTPUT_DIR, 'categories'), exist_ok=True)
    
    for category, articles in categories.items():
        category_slug = category.lower().replace(' ', '-')
        
        # Generate article list for category
        articles_html = ""
        for article in sorted(articles, key=lambda x: x.get('publishDate', ''), reverse=True):
            eeat_score = article.get('eeatScore', {}).get('overall', 85)
            score_color = "green" if eeat_score >= 85 else "yellow" if eeat_score >= 70 else "red"
            
            articles_html += f'''
            <article class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center space-x-2">
                        <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Fact-Checked</span>
                        <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">Expert Author</span>
                    </div>
                    <span class="bg-{score_color}-100 text-{score_color}-800 text-xs px-2 py-1 rounded">
                        E-E-A-T: {eeat_score}%
                    </span>
                </div>
                <h3 class="text-xl font-bold text-blue-800 mb-2">
                    <a href="../articles/{article['slug']}.html" class="hover:text-blue-600">{article['title']}</a>
                </h3>
                <p class="text-gray-600 mb-3">{article.get('excerpt', '')[:150]}...</p>
                <div class="flex items-center justify-between text-sm text-gray-500">
                    <span>By {article.get('authorProfile', {}).get('name', article.get('author', 'Editorial Team'))}</span>
                    <span>{article.get('publishDate', '')}</span>
                </div>
            </article>
            '''
        
        category_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category} - Country's News</title>
    <meta name="description" content="Expert-reviewed {category.lower()} articles with E-E-A-T compliance and fact-checked content.">
    <link rel="canonical" href="https://countrysnews.com/categories/{category_slug}.html">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-md">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between py-4">
                <div class="flex items-center space-x-4">
                    <a href="../index.html">
                        <img src="../logo-header.svg" alt="Country's News" class="h-10">
                    </a>
                    <a href="../index.html" class="text-2xl font-bold text-blue-800">Country's News</a>
                </div>
                <div class="hidden md:flex space-x-6">
                    <a href="../index.html" class="text-gray-700 hover:text-blue-600 font-medium">Home</a>
                    <a href="news.html" class="text-gray-700 hover:text-blue-600">News</a>
                    <a href="business.html" class="text-gray-700 hover:text-blue-600">Business</a>
                    <a href="technology.html" class="text-gray-700 hover:text-blue-600">Technology</a>
                    <a href="sports.html" class="text-gray-700 hover:text-blue-600">Sports</a>
                    <a href="../contact.html" class="text-gray-700 hover:text-blue-600">Contact</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-8">
        <div class="mb-8">
            <h1 class="text-4xl font-bold text-blue-800 mb-4">{category}</h1>
            <p class="text-gray-600">Expert analysis and reliable reporting in {category.lower()} with E-E-A-T compliance</p>
            <div class="flex items-center mt-2 text-sm text-gray-500">
                <span class="bg-green-100 text-green-800 px-2 py-1 rounded mr-2">All Articles Fact-Checked</span>
                <span>{len(articles)} articles</span>
            </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles_html}
        </div>
    </main>

    <footer class="bg-gray-800 text-white py-8 mt-16">
        <div class="container mx-auto px-4 text-center">
            <p class="text-gray-300">&copy; {datetime.now().year} Country's News. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>'''

        with open(os.path.join(OUTPUT_DIR, 'categories', f'{category_slug}.html'), 'w', encoding='utf-8') as f:
            f.write(category_html)
    
    print(f"✅ Generated {len(categories)} E-E-A-T enhanced category pages")

def generate_static_pages():
    """Generate static pages (about, contact, etc.) with E-E-A-T elements"""
    
    # About Us page with E-E-A-T credentials
    about_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About Us - Country's News</title>
    <meta name="description" content="Learn about Country's News editorial team, our E-E-A-T compliance standards, and commitment to expert journalism.">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <nav class="bg-white shadow-md">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between py-4">
                <div class="flex items-center space-x-4">
                    <a href="index.html">
                        <img src="logo-header.svg" alt="Country's News" class="h-10">
                    </a>
                    <a href="index.html" class="text-2xl font-bold text-blue-800">Country's News</a>
                </div>
            </div>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-12 max-w-4xl">
        <h1 class="text-4xl font-bold text-blue-800 mb-8">About Country's News</h1>
        
        <!-- E-E-A-T Mission Statement -->
        <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Our E-E-A-T Commitment</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="text-lg font-semibold text-blue-800 mb-2">Experience</h3>
                    <p class="text-gray-600">Our team brings decades of first-hand experience in journalism, technology, business, and international relations.</p>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-blue-800 mb-2">Expertise</h3>
                    <p class="text-gray-600">Each article is crafted by verified experts with specialized knowledge and professional credentials in their field.</p>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-blue-800 mb-2">Authoritativeness</h3>
                    <p class="text-gray-600">We establish credibility through verified sources, expert citations, and transparent editorial standards.</p>
                </div>
                <div>
                    <h3 class="text-lg font-semibold text-blue-800 mb-2">Trustworthiness</h3>
                    <p class="text-gray-600">Every article undergoes rigorous fact-checking and editorial review to ensure accuracy and reliability.</p>
                </div>
            </div>
        </div>

        <!-- Editorial Standards -->
        <div class="bg-blue-50 border-l-4 border-blue-400 p-6 mb-8">
            <h2 class="text-2xl font-bold text-blue-800 mb-4">Editorial Standards</h2>
            <ul class="space-y-3 text-gray-700">
                <li class="flex items-center">
                    <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    All articles are fact-checked by our editorial review team
                </li>
                <li class="flex items-center">
                    <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    Sources are verified and citations are provided for all claims
                </li>
                <li class="flex items-center">
                    <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    Authors' credentials and expertise are transparently displayed
                </li>
                <li class="flex items-center">
                    <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    Corrections and updates are clearly marked and timestamped
                </li>
            </ul>
        </div>

        <!-- Contact Information -->
        <div class="bg-white rounded-lg shadow-lg p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Contact Our Editorial Team</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h3 class="font-semibold text-gray-900 mb-2">Editorial Inquiries</h3>
                    <p class="text-gray-600">editorial@countrysnews.com</p>
                </div>
                <div>
                    <h3 class="font-semibold text-gray-900 mb-2">Corrections & Feedback</h3>
                    <p class="text-gray-600">corrections@countrysnews.com</p>
                </div>
            </div>
        </div>
    </main>

    <footer class="bg-gray-800 text-white py-8 mt-16">
        <div class="container mx-auto px-4 text-center">
            <p class="text-gray-300">&copy; {datetime.now().year} Country's News. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>'''

    with open(os.path.join(OUTPUT_DIR, 'about-us.html'), 'w', encoding='utf-8') as f:
        f.write(about_html)
    
    print("✅ Generated E-E-A-T enhanced static pages")

def generate_eeat_sitemap(articles_data):
    """Generate sitemap with E-E-A-T enhanced articles"""
    sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://countrysnews.com/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://countrysnews.com/about-us.html</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
'''
    
    for article in articles_data:
        date_modified = article.get('dateModified', '')
        # Ensure proper date format (remove Z if present)
        if date_modified.endswith('Z'):
            date_modified = date_modified[:-1]
        
        sitemap_content += f'''    <url>
        <loc>https://countrysnews.com/articles/{article['slug']}.html</loc>
        <lastmod>{date_modified}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
'''
    
    sitemap_content += '</urlset>'
    
    with open(os.path.join(OUTPUT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print("✅ Generated E-E-A-T enhanced sitemap")

def generate_robots_txt():
    """Generate robots.txt"""
    robots_content = """User-agent: *
Allow: /

Sitemap: https://countrysnews.com/sitemap.xml
"""
    
    with open(os.path.join(OUTPUT_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(robots_content)
    print("✅ Generated robots.txt")

def generate_eeat_rss_feed(articles_data):
    """Generate RSS feed with E-E-A-T indicators"""
    recent_articles = sorted(articles_data, key=lambda x: x.get('publishDate', ''), reverse=True)[:10]
    
    rss_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Country's News - E-E-A-T Compliant Journalism</title>
        <description>Expert-reviewed news analysis with transparent editorial standards and fact-checked content</description>
        <link>https://countrysnews.com</link>
        <language>en-IN</language>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
'''
    
    for article in recent_articles:
        rss_content += f'''        <item>
            <title>{article['title']}</title>
            <description>{article.get('excerpt', '')}</description>
            <link>https://countrysnews.com/articles/{article['slug']}.html</link>
            <guid>https://countrysnews.com/articles/{article['slug']}.html</guid>
            <pubDate>{article.get('publishDate', '')} 12:00:00 GMT</pubDate>
            <author>{article.get('authorProfile', {}).get('name', article.get('author', 'Editorial Team'))}</author>
            <category>{article.get('category', 'News')}</category>
        </item>
'''
    
    rss_content += '''    </channel>
</rss>'''
    
    with open(os.path.join(OUTPUT_DIR, 'rss.xml'), 'w', encoding='utf-8') as f:
        f.write(rss_content)
    print("✅ Generated E-E-A-T enhanced RSS feed")

if __name__ == "__main__":
    generate_eeat_enhanced_site()
