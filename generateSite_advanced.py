#!/usr/bin/env python3
"""
Advanced Site Generator with E-E-A-T Standards
Generates a comprehensive website with all advanced features including ads, lazy loading, 
social features, SEO optimization, and E-E-A-T compliance.

Options:
- --differential: Use differential generation mode (default)
- --full: Force full regeneration of all files  
- --enhance: Enhance existing articles before generation
"""

import json
import html
import os
import sys
import argparse
import shutil
import re
import time
from collections import defaultdict
from datetime import datetime, timezone, date
from urllib.parse import quote

# Optional markdown support
try:
    import markdown as md
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("⚠️  Markdown module not available - using fallback HTML processing")

OUTPUT_DIR = "dist"
ARTICLES_FILE = "perplexityArticles_eeat_enhanced.json"
DEFAULT_CATEGORY = "News"

def perform_preflight_checks():
    """Critical pre-flight checks before generation"""
    print("🔍 Performing critical pre-flight checks...")
    
    # Check if articles file exists
    if not os.path.exists(ARTICLES_FILE):
        fallback_file = 'perplexityArticles.json'
        if not os.path.exists(fallback_file):
            print(f"❌ CRITICAL ERROR: No articles file found ({ARTICLES_FILE} or {fallback_file})")
            return False
        else:
            print(f"⚠️  Using fallback articles file: {fallback_file}")
    
    # Load and validate articles data
    try:
        articles_data = load_articles()
        if not articles_data:
            print("❌ CRITICAL ERROR: No articles found in articles file")
            return False
        
        print(f"✅ Found {len(articles_data)} articles")
        
        # Check for required fields in articles
        missing_slugs = 0
        missing_titles = 0
        duplicate_slugs = set()
        seen_slugs = set()
        
        for i, article in enumerate(articles_data):
            slug = article.get('slug', '').strip()
            title = article.get('title', '').strip()
            
            if not slug:
                missing_slugs += 1
            elif slug in seen_slugs:
                duplicate_slugs.add(slug)
            else:
                seen_slugs.add(slug)
            
            if not title:
                missing_titles += 1
        
        issues = missing_slugs + missing_titles + len(duplicate_slugs)
        if issues > 0:
            print(f"❌ CRITICAL ERROR: Article data issues found:")
            print(f"   - Articles missing slugs: {missing_slugs}")
            print(f"   - Articles missing titles: {missing_titles}")
            print(f"   - Duplicate slugs: {len(duplicate_slugs)}")
            if duplicate_slugs:
                print(f"   - Duplicate slug examples: {list(duplicate_slugs)[:5]}")
            return False
        
        print("✅ All articles have valid slugs and titles")
        print("✅ Pre-flight checks passed")
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Failed to validate articles data: {e}")
        return False

def enhance_existing_articles():
    """Enhance existing articles using super_article_manager system"""
    try:
        print("🚀 Enhancing existing articles with latest features...")
        print("=" * 60)
        
        # Import the SuperArticleManager class
        import subprocess
        import os
        
        # Run the enhancement using the super_article_manager
        result = subprocess.run([
            sys.executable, 'super_article_manager.py', 'enhance', '--all'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Article enhancement completed successfully!")
            print(result.stdout)
            return True
        else:
            print("❌ Article enhancement failed!")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error during article enhancement: {e}")
        return False

def generate_advanced_site(enhance_articles=False):
    """Generate advanced website with all features"""
    
    print("🚀 Generating Advanced E-E-A-T Compliant Website...")
    print("=" * 60)
    
    # Optionally enhance articles first
    if enhance_articles:
        if not enhance_existing_articles():
            print("⚠️  Article enhancement failed, continuing with existing articles...")
        else:
            print("✅ Articles enhanced successfully!")
    
    # CRITICAL: Pre-flight validation checks
    if not perform_preflight_checks():
        print("❌ CRITICAL ERROR: Pre-flight checks failed. Aborting generation.")
        return False
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Ensure placeholder image exists
    ensure_placeholder_image()
    
    # Copy static assets
    copy_static_assets()
    
    # Load articles
    articles_data = load_articles()
    if not articles_data:
        print("❌ No articles found!")
        return
    
    print(f"✅ Loaded {len(articles_data)} articles")
    
    # Get unique categories
    unique_categories = get_unique_categories(articles_data)
    print(f"✅ Found {len(unique_categories)} categories")
    
    # Generate all pages with advanced features
    generate_advanced_homepage(articles_data, unique_categories)
    generate_advanced_article_pages(articles_data, unique_categories)
    generate_advanced_category_pages(articles_data, unique_categories)
    generate_static_pages(unique_categories)
    generate_sitemap(articles_data)
    
    # CRITICAL: Validate sitemap to prevent Google Search Console errors
    sitemap_valid = validate_and_fix_sitemap()
    if not sitemap_valid:
        print("❌ CRITICAL ERROR: Sitemap validation failed!")
        print("🚨 THIS WILL CAUSE GOOGLE SEARCH CONSOLE ERRORS!")
        print("🚨 GENERATION CANNOT CONTINUE SAFELY!")
        return False
    
    generate_robots_txt()
    generate_rss_feed(articles_data)
    
    # Final validation checks
    if not perform_final_validation():
        print("❌ CRITICAL ERROR: Final validation failed!")
        return False
    
    print("\n🎉 Advanced E-E-A-T Website Generation Complete!")
    print(f"📁 Website files generated in: {OUTPUT_DIR}/")
    print("🌟 Features included: Ads, Lazy Loading, Social Media, SEO, E-E-A-T Compliance!")
    print("✅ All critical validations passed - safe for deployment!")
    return True

def ensure_placeholder_image():
    """Ensure placeholder image exists"""
    placeholder_path = os.path.join('images', 'placeholder.webp')
    # Also remove legacy .jpg placeholder if it exists
    legacy_path = os.path.join('images', 'placeholder.jpg')
    if os.path.exists(legacy_path):
        os.remove(legacy_path)
    if not os.path.exists(placeholder_path):
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create images directory if it doesn't exist
            os.makedirs('images', exist_ok=True)
            
            # Create a simple placeholder image
            img = Image.new('RGB', (800, 600), color='#f0f0f0')
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font, fallback to basic if needed
            try:
                font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 48)
            except:
                try:
                    font = ImageFont.load_default()
                except:
                    font = None
            
            # Add text
            text = 'Image Placeholder'
            if font:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                x = (800 - text_width) // 2
                y = (600 - text_height) // 2
                draw.text((x, y), text, fill='#666666', font=font)
            
            # Save as WebP
            img.save(placeholder_path, 'WEBP', quality=85)
            print(f"📁 Created placeholder image: {placeholder_path}")
            
        except ImportError:
            print("⚠️  PIL not available, skipping placeholder image creation")
        except Exception as e:
            print(f"⚠️  Could not create placeholder image: {e}")

def copy_static_assets():
    """Copy all static assets"""
    assets = ['logo.svg', 'favicon.svg', 'logo-header.svg']
    for asset in assets:
        if os.path.exists(asset):
            shutil.copy2(asset, os.path.join(OUTPUT_DIR, asset))
            print(f"📁 Copied {asset}")
    
    # Copy images directory if it exists
    if os.path.exists('images'):
        shutil.copytree('images', os.path.join(OUTPUT_DIR, 'images'), dirs_exist_ok=True)
        print("📁 Copied images directory")

def load_articles():
    """Load articles data"""
    try:
        with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        try:
            with open('perplexityArticles.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ No articles file found")
            return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing articles: {e}")
        return []

def get_unique_categories(articles_data):
    """Get unique categories from articles"""
    categories = set()
    for article in articles_data:
        category = article.get('category', DEFAULT_CATEGORY)
        categories.add(category)
    return sorted(list(categories))

def generate_slug(text):
    """Generate URL-friendly slug"""
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def get_base_html_head():
    """Advanced HTML head with all optimizations"""
    return '''
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    <!-- Google AdSense -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7451593482486400"
         crossorigin="anonymous"></script>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Favicon and Logo -->
    <link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48" />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg">
    <link rel="apple-touch-icon" href="/favicon.svg">
    
    <!-- Performance optimizations -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="dns-prefetch" href="//cdn.tailwindcss.com">
    
    <!-- RSS feed -->
    <link rel="alternate" type="application/rss+xml" title="Country's News RSS" href="/rss.xml">
    
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8fafc;
            scroll-behavior: smooth;
        }
        
        /* Article Content Styling */
        .article-content h1, .article-content h2, .article-content h3, 
        .article-content h4, .article-content h5, .article-content h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
            color: #1e3a8a;
            /* Ensure anchors scroll below sticky header */
            scroll-margin-top: 6rem; /* ~96px for header + spacing */
        }
    .article-content h1 { font-size: 2.5em; }
    .article-content h2 { font-size: 2em; }
    .article-content h3 { font-size: 1.75em; }
    /* Extra safety: apply scroll-margin to any heading in article to cover injected IDs */
    .article-content :is(h1,h2,h3,h4,h5,h6) { scroll-margin-top: 6rem; }
        .article-content p {
            margin-bottom: 1em;
            line-height: 1.7;
            color: #374151;
        }
        .article-content ul, .article-content ol {
            list-style-position: inside;
            margin-bottom: 1em;
            padding-left: 1.5em;
        }
        .article-content ul li {
            list-style-type: disc;
            margin-bottom: 0.5em;
        }
        .article-content ol li {
            list-style-type: decimal;
            margin-bottom: 0.5em;
        }
        .article-content img {
            max-width: 100%;
            height: auto;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 1.5rem auto;
            display: block;
        }
        
        /* Card hover effects */
        .article-card {
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .article-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        /* Ad Container Styles */
        /* Ad containers remain in DOM for layout but are inert until populated by an ad script */
        .ad-container {
            margin: 2rem 0;
            padding: 0.5rem;
            text-align: center;
            background-color: transparent; /* don't show placeholder background */
            border: none;
            border-radius: 0.5rem;
            min-height: 0; /* collapsed until content appears */
            display: block;
            align-items: stretch;
            justify-content: stretch;
            position: relative;
            overflow: hidden;
            transition: min-height 0.25s ease, padding 0.25s ease;
        }
        
        .ad-container.mobile-bottom {
            margin: 0;
            min-height: 50px;
            border-radius: 0;
        }
        
        .ad-container.sidebar {
            width: 300px;
            height: 250px;
            margin: 1rem 0;
        }
        
        .ad-container.banner {
            width: 100%;
            height: 90px;
        }
        
        /* Placeholder text removed — ad-slot elements are empty until populated by ad JS */
        .ad-placeholder { display: none; }
        
        /* Author Profile Styling */
        .author-profile {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-left: 4px solid #0ea5e9;
            padding: 1.5rem;
            border-radius: 0.75rem;
            margin: 2rem 0;
        }
        
        /* Social Media Hashtags */
        .hashtags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin: 1rem 0;
        }
        
        .hashtag {
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            color: #1e40af;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .hashtag:hover {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            transform: scale(1.05);
        }
        
        /* Lazy Loading */
        .lazy-image {
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: loading 1.5s infinite;
            min-height: 200px;
        }
        
        @keyframes loading {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        
        /* Load More Button */
        .load-more-btn {
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 0.75rem;
            font-size: 1.125rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 14px 0 rgba(37, 99, 235, 0.4);
        }
        
        .load-more-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px 0 rgba(37, 99, 235, 0.5);
        }
        
        /* Navigation Dropdown */
        .dropdown {
            position: relative;
            display: inline-block;
        }
        
        .dropdown-content {
            display: none;
            position: absolute;
            background: rgba(30, 58, 138, 0.95);
            min-width: 200px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            z-index: 1000;
            border-radius: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            -webkit-backdrop-filter: blur(10px);
            backdrop-filter: blur(10px);
            top: 100%;
            right: 0;
        }
        
        .dropdown-content a {
            color: white;
            padding: 12px 16px;
            text-decoration: none;
            display: block;
            transition: background-color 0.3s ease;
        }
        
        .dropdown-content a:hover {
            background: rgba(59, 130, 246, 0.3);
        }
        
        .dropdown:hover .dropdown-content {
            display: block;
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .ad-container.sidebar {
                width: 100%;
                height: 200px;
            }
        }
    </style>
    '''

def generate_header_html(unique_categories, current_page_type="home"):
    """Generate advanced header with dropdown navigation"""
    
    # Get top categories for main nav
    category_links = ""
    top_categories = unique_categories[:5] if len(unique_categories) > 5 else unique_categories
    
    for category in top_categories:
        category_slug = generate_slug(category)
        link_path = f"categories/{category_slug}.html" if current_page_type == "home" else f"../categories/{category_slug}.html"
        category_links += f'<li><a href="{link_path}" class="hover:text-blue-200 transition-colors px-2 py-1 rounded">{category}</a></li>'
    
    # More categories dropdown
    dropdown_categories = ""
    if len(unique_categories) > 5:
        for category in unique_categories[5:]:
            category_slug = generate_slug(category)
            link_path = f"categories/{category_slug}.html" if current_page_type == "home" else f"../categories/{category_slug}.html"
            dropdown_categories += f'<a href="{link_path}">{category}</a>'
    
    # Mobile menu links - include ALL categories
    mobile_category_links = ""
    for category in unique_categories:
        category_slug = generate_slug(category)
        link_path = f"categories/{category_slug}.html" if current_page_type == "home" else f"../categories/{category_slug}.html"
        mobile_category_links += f'<a href="{link_path}" class="block py-2 hover:text-blue-200">{category}</a>'
    
    home_link = "index.html" if current_page_type == "home" else "../index.html"
    logo_path = "logo-header.svg" if current_page_type == "home" else "../logo-header.svg"
    pfx = "" if current_page_type == "home" else "../"
    about_link = f"{pfx}about/"
    editorial_link = f"{pfx}editorial-policy/"
    contact_link = f"{pfx}contact/"
    
    return f'''
    <header class="bg-gradient-to-r from-blue-900 via-blue-700 to-blue-800 text-white shadow-xl sticky top-0 z-50">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Main Header -->
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center space-x-4">
                    <a href="{home_link}" class="hover:opacity-80 transition-opacity">
                        <img src="{logo_path}" alt="Country's News Logo" class="h-12 sm:h-16 w-auto">
                    </a>
                    <div class="hidden sm:block">
                        <h1 class="text-xl font-bold">Country's News</h1>
                        <p class="text-xs text-blue-200">Trusted. Verified. Expert.</p>
                    </div>
                </div>
                
                <nav class="hidden lg:block">
                    <ul class="flex items-center space-x-6">
                        <li><a href="{home_link}" class="hover:text-blue-200 transition-colors font-medium">Home</a></li>
                        {category_links}
                        <li class="dropdown">
                            <span class="dropdown-toggle hover:text-blue-200 transition-colors cursor-pointer flex items-center">
                                More
                                <svg class="w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                                </svg>
                            </span>
                            <div class="dropdown-content">
                                {dropdown_categories}
                                <a href="{about_link}" class="border-t border-blue-600">About Us</a>
                                <a href="{editorial_link}">Editorial Policy</a>
                                <a href="{contact_link}">Contact</a>
                            </div>
                        </li>
                    </ul>
                </nav>
                
                <!-- Mobile Menu Button -->
                <button id="mobile-menu-btn" class="lg:hidden text-white hover:text-blue-200" aria-label="Open mobile menu">
                    <span class="sr-only">Open mobile menu</span>
                    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                    </svg>
                </button>
            </div>
        </div>
        
        <!-- Mobile Menu -->
        <div id="mobile-menu" class="lg:hidden hidden bg-blue-800 border-t border-blue-600">
            <div class="px-4 py-2 space-y-2">
                <a href="{home_link}" class="block py-2 hover:text-blue-200">Home</a>
                {mobile_category_links}
                <a href="{about_link}" class="block py-2 hover:text-blue-200">About Us</a>
                <a href="{editorial_link}" class="block py-2 hover:text-blue-200">Editorial Policy</a>
                <a href="{contact_link}" class="block py-2 hover:text-blue-200">Contact</a>
            </div>
        </div>
    </header>
    
    <!-- Top Banner Ad -->
    <div class="ad-container banner">
        <div data-ad-slot="banner-top" aria-hidden="true"></div>
    </div>
    '''

def generate_footer_html(current_page_type="home"):
    """Generate advanced footer with social links and ads"""
    logo_path = "logo-header.svg" if current_page_type == "home" else "../logo-header.svg"
    rss_link = "rss.xml" if current_page_type == "home" else "../rss.xml"
    pfx = "" if current_page_type == "home" else "../"
    about_link = f"{pfx}about/"
    editorial_link = f"{pfx}editorial-policy/"
    fact_check_link = f"{pfx}fact-checking-policy/"
    privacy_link = f"{pfx}privacy-policy/"
    terms_link = f"{pfx}terms/"
    contact_link = f"{pfx}contact/"
    cats_prefix = f"{pfx}categories/"
    
    return f'''
    <!-- Footer Ad -->
    <div class="ad-container banner mt-12">
        <div data-ad-slot="banner-footer" aria-hidden="true"></div>
    </div>
    
    <footer class="bg-gray-900 text-white shadow-inner">
        <div class="container mx-auto px-4 py-12">
            <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
                <!-- Logo and Description -->
                <div class="text-center md:text-left">
                    <img src="{logo_path}" alt="Country's News Logo" class="h-16 w-auto mx-auto md:mx-0 mb-4">
                    <p class="text-gray-400 text-sm leading-relaxed mb-4">
                        Professional journalism delivering comprehensive news coverage with fact-checked content.
                    </p>
                </div>
                
                <!-- Categories -->
                <div class="text-center md:text-left">
                    <h3 class="text-lg font-semibold mb-4 text-blue-400">Intelligence Pillars</h3>
                    <div class="space-y-2 text-sm">
                        <a href="{cats_prefix}ai-infrastructure.html" class="block hover:text-blue-400 transition-colors text-gray-400">AI Infrastructure</a>
                        <a href="{cats_prefix}enterprise-transformation.html" class="block hover:text-blue-400 transition-colors text-gray-400">Enterprise Transformation</a>
                        <a href="{cats_prefix}smart-mobility.html" class="block hover:text-blue-400 transition-colors text-gray-400">Smart Mobility</a>
                        <a href="{cats_prefix}india-digital-transformation.html" class="block hover:text-blue-400 transition-colors text-gray-400">India Digital</a>
                    </div>
                </div>

                <!-- Quick Links -->
                <div class="text-center md:text-left">
                    <h3 class="text-lg font-semibold mb-4 text-blue-400">Quick Links</h3>
                    <div class="space-y-2 text-sm">
                        <a href="{about_link}" class="block hover:text-blue-400 transition-colors text-gray-400">About Us</a>
                        <a href="{editorial_link}" class="block hover:text-blue-400 transition-colors text-gray-400">Editorial Policy</a>
                        <a href="{fact_check_link}" class="block hover:text-blue-400 transition-colors text-gray-400">Fact-Checking</a>
                        <a href="{privacy_link}" class="block hover:text-blue-400 transition-colors text-gray-400">Privacy Policy</a>
                        <a href="{terms_link}" class="block hover:text-blue-400 transition-colors text-gray-400">Terms</a>
                        <a href="{contact_link}" class="block hover:text-blue-400 transition-colors text-gray-400">Contact</a>
                    </div>
                </div>
                
                <!-- Connect -->
                <div class="text-center md:text-left">
                    <h3 class="text-lg font-semibold mb-4 text-blue-400">Stay Connected</h3>
                    <p class="text-gray-400 text-sm mb-4">Follow us for verified updates</p>
                    <div class="flex justify-center md:justify-start space-x-4">
                        <a href="{rss_link}" class="text-gray-400 hover:text-blue-400 transition-colors p-2 bg-gray-800 rounded-lg hover:bg-gray-700" title="RSS Feed">
                            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M3.429 2.571c8.571 0 15.714 7.143 15.714 15.714h-3.143c0-6.857-5.714-12.571-12.571-12.571v-3.143zM3.429 9.714c4.571 0 8.571 4 8.571 8.571h-3.143c0-3.143-2.286-5.429-5.429-5.429v-3.142zM6.571 16c0 1.571-1.286 2.857-2.857 2.857s-2.857-1.286-2.857-2.857 1.286-2.857 2.857-2.857 2.857 1.286 2.857 2.857z"/>
                            </svg>
                        </a>
                        <a href="https://twitter.com/countrysnews" class="text-gray-400 hover:text-blue-400 transition-colors p-2 bg-gray-800 rounded-lg hover:bg-gray-700" title="Twitter">
                            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84"/>
                            </svg>
                        </a>
                    </div>
                </div>
            </div>
            
            <!-- Copyright -->
            <div class="border-t border-gray-700 mt-8 pt-6 text-center">
                <p class="text-gray-400 text-sm">
                    &copy; {datetime.now().year} Country's News. All rights reserved. | 
                    <span class="text-blue-400">Verified Journalism</span> | 
                    Expert Analysis | Fact-Checked Content
                </p>
            </div>
        </div>
    </footer>
    
    <!-- Mobile Bottom Ad -->
    <div class="ad-container mobile-bottom fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 lg:hidden z-40">
        <div data-ad-slot="mobile-bottom" aria-hidden="true"></div>
    </div>
    
    <!-- JavaScript for mobile menu and lazy loading -->
    <script>
        // Mobile menu toggle
        document.getElementById('mobile-menu-btn')?.addEventListener('click', function() {{
            const mobileMenu = document.getElementById('mobile-menu');
            mobileMenu.classList.toggle('hidden');
        }});
        
        // Lazy loading for images
        document.addEventListener('DOMContentLoaded', function() {{
            const lazyImages = document.querySelectorAll('img[data-src]');
            const imageObserver = new IntersectionObserver((entries, observer) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.classList.remove('lazy-image');
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }}
                }});
            }});
            
            lazyImages.forEach(img => imageObserver.observe(img));
        }});
        
    </script>
    '''

def generate_article_card(article, current_page_type="home"):
    """Generate advanced article card with E-E-A-T indicators and ads"""
    
    # Get proper thumbnail URL
    thumbnail_url = article.get('thumbnailImageUrl', '')
    if not thumbnail_url:
        thumbnail_url = article.get('ogImage', '')
    
    # Adjust path for different page types
    if current_page_type == "article":
        article_link = f"{article['slug']}.html"
        if thumbnail_url and not thumbnail_url.startswith('http'):
            thumbnail_url = f"../{thumbnail_url}"
    elif current_page_type == "category":
        article_link = f"../articles/{article['slug']}.html"
        if thumbnail_url and not thumbnail_url.startswith('http') and thumbnail_url.startswith('dist/'):
            thumbnail_url = thumbnail_url.replace('dist/', '../')
    else:  # home page
        article_link = f"articles/{article['slug']}.html"
        if thumbnail_url.startswith('dist/'):
            thumbnail_url = thumbnail_url.replace('dist/', '')
    
    # Generate social hashtags
    hashtags_html = ""
    social_hashtags = article.get('socialMediaHashtags', [])
    if social_hashtags:
        hashtags_html = '<div class="hashtags">'
        for tag in social_hashtags[:5]:  # Limit to 5 hashtags
            hashtags_html += f'<span class="hashtag">#{tag}</span>'
        hashtags_html += '</div>'
    
    return f'''
    <article class="article-card bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
        <a href="{article_link}" class="block">
            <div class="relative">
                <img src="{thumbnail_url}" 
                     alt="{article.get('imageAltText', article['title'])}" 
                     class="w-full h-48 object-cover"
                     onerror="this.style.display='none'">
                <div class="absolute top-3 left-3">
                    <span class="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                        {article.get('category', 'News')}
                    </span>
                </div>
            </div>
            <div class="p-6">
                <h2 class="text-xl font-bold text-gray-900 mb-3 hover:text-blue-600 transition-colors line-clamp-2">
                    {article['title'][:80]}{"..." if len(article['title']) > 80 else ""}
                </h2>
                
                <p class="text-gray-600 text-sm mb-4 line-clamp-3">
                    {article.get('excerpt', '')[:150]}{"..." if len(article.get('excerpt', '')) > 150 else ""}
                </p>
                
                <!-- Social Hashtags -->
                {hashtags_html}
                
                <!-- Article Meta -->
                <div class="flex items-center justify-between text-sm text-gray-500 mt-4 pt-4 border-t border-gray-100">
                    <div class="flex items-center space-x-3">
                        <span class="flex items-center">
                            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                            </svg>
                            {article.get('author', 'Editor')}
                        </span>
                        <span class="flex items-center">
                            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.414-1.414L11 9.586V6z" clip-rule="evenodd"></path>
                            </svg>
                            {article.get('readingTimeMinutes', 5)} min
                        </span>
                    </div>
                    <span class="text-blue-600 font-medium">{article.get('publishDate', '')}</span>
                </div>
            </div>
        </a>
    </article>
    '''

def generate_advanced_homepage(articles_data, unique_categories):
    """Generate advanced homepage with ads and features"""
    print("📝 Generating advanced homepage...")
    
    # Sort articles by date (newest first)
    sorted_articles = sorted(articles_data, key=lambda x: x.get('publishDate', ''), reverse=True)

    # Hero: single most recent article with a full-bleed card
    hero_article = sorted_articles[0] if sorted_articles else None

    # Group by editorial pillar (top 3 per pillar for homepage sections)
    from collections import defaultdict as _defaultdict
    _pillar_buckets = _defaultdict(list)
    for _a in sorted_articles[1:]:   # skip the hero
        _cat = _a.get('category', 'India Digital Transformation')
        _pillar_buckets[_cat].append(_a)

    pillar_sections = {
        'AI Infrastructure':            _pillar_buckets['AI Infrastructure'][:3],
        'Enterprise Transformation':    _pillar_buckets['Enterprise Transformation'][:3],
        'Smart Mobility':               _pillar_buckets['Smart Mobility'][:3],
        'India Digital Transformation': _pillar_buckets['India Digital Transformation'][:3],
    }

    # Recent articles for the "Latest Intelligence" grid (initial load)
    recent_articles = sorted_articles[1:13]
    remaining_articles = sorted_articles[13:]

    # Recent cards HTML
    recent_cards_html = ""
    for i, article in enumerate(recent_articles):
        recent_cards_html += generate_article_card(article, "home")
        if (i + 1) % 3 == 0 and i < len(recent_articles) - 1:
            recent_cards_html += '''
            <div class="col-span-full">
                <div class="ad-container">
                    <div data-ad-slot="in-content-recent" aria-hidden="true"></div>
                </div>
            </div>
            '''

    # Generate structured data for E-E-A-T
    structured_data = generate_homepage_structured_data(articles_data)

    # Remaining articles JSON for Load More
    remaining_articles_json = json.dumps([{
        'title': article['title'],
        'slug': article['slug'],
        'author': article.get('author', 'Editorial Team'),
        'publishDate': article.get('publishDate', ''),
        'category': article.get('category', 'India Digital Transformation'),
        'excerpt': article.get('excerpt', ''),
        'imageUrl': article.get('imageUrl', ''),
        'thumbnail': article.get('thumbnail', ''),
        'thumbnailImageUrl': article.get('thumbnailImageUrl', ''),
        'ogImage': article.get('ogImage', ''),
        'imageAltText': article.get('imageAltText', article['title']),
        'readingTimeMinutes': article.get('readingTimeMinutes', 5),
        'socialMediaHashtags': article.get('socialMediaHashtags', [])
    } for article in remaining_articles] if remaining_articles else [])

    # ── Hero card helper ──────────────────────────────────────────────────
    def hero_card_html(article):
        if not article:
            return ''
        img = article.get('thumbnailImageUrl') or article.get('thumbnail') or article.get('imageUrl') or 'images/placeholder.webp'
        if img.startswith('dist/'):
            img = img[5:]
        cat = article.get('category', 'Intelligence')
        cat_slug = generate_slug(cat)
        slug = article.get('slug', '')
        content_type = article.get('contentType', 'strategic-analysis')
        type_label = content_type.replace('-', ' ').title()
        return f'''
        <article class="relative bg-gray-900 rounded-2xl overflow-hidden shadow-2xl min-h-[400px] flex flex-col justify-end group">
            <img src="{img}" alt="{article.get('imageAltText', article['title'])}"
                 class="absolute inset-0 w-full h-full object-cover opacity-50 group-hover:opacity-60 transition-opacity duration-300"
                 onerror="this.src='images/placeholder.webp'">
            <div class="relative z-10 p-8 bg-gradient-to-t from-gray-900 via-gray-900/80 to-transparent">
                <div class="flex items-center gap-3 mb-4">
                    <a href="categories/{cat_slug}.html"
                       class="bg-blue-600 text-white px-4 py-1 rounded-full text-xs font-bold uppercase tracking-wider hover:bg-blue-500 transition-colors">
                        {cat}
                    </a>
                    <span class="text-blue-300 text-xs font-medium uppercase tracking-wider">{type_label}</span>
                </div>
                <a href="articles/{slug}.html" class="block">
                    <h1 class="text-3xl md:text-4xl font-bold text-white mb-3 leading-tight hover:text-blue-200 transition-colors">
                        {article['title']}
                    </h1>
                    <p class="text-gray-300 text-base mb-4 line-clamp-2">{article.get('excerpt', '')[:200]}</p>
                </a>
                <div class="flex items-center gap-4 text-sm text-gray-400">
                    <span>By <span class="text-white font-medium">{article.get('author', 'Editorial Team')}</span></span>
                    <span>{article.get('publishDate', '')}</span>
                    <span>{article.get('readingTimeMinutes', 5)} min read</span>
                </div>
            </div>
        </article>'''

    # ── Pillar section helper ─────────────────────────────────────────────
    def pillar_section_html(pillar_name, articles, pillar_slug, accent_color='blue'):
        if not articles:
            return ''
        cards = ''.join(generate_article_card(a, "home") for a in articles)
        return f'''
        <section class="mb-16">
            <div class="flex items-center justify-between mb-6">
                <div class="flex items-center gap-3">
                    <div class="w-1 h-8 bg-{accent_color}-600 rounded-full"></div>
                    <h2 class="text-2xl font-bold text-gray-900">{pillar_name}</h2>
                </div>
                <a href="categories/{pillar_slug}.html"
                   class="text-{accent_color}-600 hover:text-{accent_color}-700 text-sm font-semibold flex items-center gap-1">
                    View all
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
                    </svg>
                </a>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {cards}
            </div>
        </section>'''

    pillar_colors = {
        'AI Infrastructure':            ('blue',   'ai-infrastructure'),
        'Enterprise Transformation':    ('indigo', 'enterprise-transformation'),
        'Smart Mobility':               ('emerald','smart-mobility'),
        'India Digital Transformation': ('orange', 'india-digital-transformation'),
    }

    pillar_sections_html = ''
    for pillar_name, articles in pillar_sections.items():
        color, slug = pillar_colors[pillar_name]
        pillar_sections_html += pillar_section_html(pillar_name, articles, slug, color)

    homepage_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Country's News — Technology Intelligence Platform</title>
        <meta name="description" content="Technology intelligence for the AI transformation era. Covering AI infrastructure, enterprise transformation, smart mobility, and India's digital economy.">
        <meta name="keywords" content="AI infrastructure, enterprise AI, smart mobility, India digital transformation, technology intelligence, EV, LLM, enterprise SaaS">

        <!-- E-E-A-T Meta Tags -->
        <meta name="author" content="Country's News Intelligence Team">
        <meta name="publisher" content="Country's News">
        <meta name="copyright" content="© {datetime.now().year} Country's News">

        <!-- Open Graph -->
        <meta property="og:title" content="Country's News — Technology Intelligence Platform">
        <meta property="og:description" content="Technology intelligence for the AI transformation era.">
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://countrysnews.com/">
        <meta property="og:site_name" content="Country's News">

        <!-- Twitter Card -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Country's News — Technology Intelligence Platform">
        <meta name="twitter:description" content="Technology intelligence for the AI transformation era.">

        <!-- Canonical URL -->
        <link rel="canonical" href="https://countrysnews.com/">

        {get_base_html_head()}

        <!-- Structured Data for E-E-A-T -->
        {structured_data}
    </head>
    <body>
        {generate_header_html(unique_categories, "home")}

        <main class="min-h-screen">

            <!-- ─── HERO ─────────────────────────────────────────────── -->
            <section class="container mx-auto px-4 py-10">
                <div class="flex flex-col lg:flex-row gap-8">
                    <!-- Hero card (full-bleed featured article) -->
                    <div class="lg:w-2/3">
                        {hero_card_html(hero_article)}
                    </div>

                    <!-- Sidebar: positioning + quick pillars + ad -->
                    <aside class="lg:w-1/3 space-y-6">
                        <!-- Positioning statement -->
                        <div class="bg-gradient-to-br from-blue-900 to-blue-700 rounded-2xl p-6 text-white">
                            <p class="text-xs font-bold uppercase tracking-widest text-blue-300 mb-2">Country's News</p>
                            <h2 class="text-xl font-bold leading-snug mb-3">
                                Technology intelligence for the AI transformation era.
                            </h2>
                            <p class="text-blue-200 text-sm leading-relaxed">
                                We analyse how AI, enterprise software, and smart infrastructure are reshaping industries — covering AI Infrastructure, Enterprise Transformation, Smart Mobility, and India's Digital Economy.
                            </p>
                        </div>

                        <!-- Pillar quick links -->
                        <div class="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                            <h3 class="text-sm font-bold uppercase tracking-wider text-gray-500 mb-4">Editorial Pillars</h3>
                            <div class="space-y-2">
                                <a href="categories/ai-infrastructure.html" class="flex items-center gap-3 p-3 rounded-xl hover:bg-blue-50 group transition-colors">
                                    <div class="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0"></div>
                                    <span class="text-sm font-semibold text-gray-800 group-hover:text-blue-700">AI Infrastructure</span>
                                </a>
                                <a href="categories/enterprise-transformation.html" class="flex items-center gap-3 p-3 rounded-xl hover:bg-indigo-50 group transition-colors">
                                    <div class="w-2 h-2 bg-indigo-600 rounded-full flex-shrink-0"></div>
                                    <span class="text-sm font-semibold text-gray-800 group-hover:text-indigo-700">Enterprise Transformation</span>
                                </a>
                                <a href="categories/smart-mobility.html" class="flex items-center gap-3 p-3 rounded-xl hover:bg-emerald-50 group transition-colors">
                                    <div class="w-2 h-2 bg-emerald-600 rounded-full flex-shrink-0"></div>
                                    <span class="text-sm font-semibold text-gray-800 group-hover:text-emerald-700">Smart Mobility</span>
                                </a>
                                <a href="categories/india-digital-transformation.html" class="flex items-center gap-3 p-3 rounded-xl hover:bg-orange-50 group transition-colors">
                                    <div class="w-2 h-2 bg-orange-500 rounded-full flex-shrink-0"></div>
                                    <span class="text-sm font-semibold text-gray-800 group-hover:text-orange-700">India Digital Transformation</span>
                                </a>
                            </div>
                        </div>

                        <!-- Sidebar ad -->
                        <div class="ad-container sidebar">
                            <div data-ad-slot="sidebar-1" aria-hidden="true"></div>
                        </div>
                    </aside>
                </div>
            </section>

            <!-- ─── BANNER AD ─────────────────────────────────────────── -->
            <div class="container mx-auto px-4">
                <div class="ad-container my-4">
                    <div data-ad-slot="banner-top" aria-hidden="true"></div>
                </div>
            </div>

            <!-- ─── PILLAR SECTIONS ───────────────────────────────────── -->
            <div class="container mx-auto px-4 py-8">
                {pillar_sections_html}
            </div>

            <!-- ─── LATEST INTELLIGENCE GRID ─────────────────────────── -->
            <section class="bg-gray-50 py-12">
                <div class="container mx-auto px-4">
                    <div class="flex items-center gap-3 mb-8">
                        <div class="w-1 h-8 bg-gray-400 rounded-full"></div>
                        <h2 class="text-2xl font-bold text-gray-900">Latest Intelligence</h2>
                    </div>
                    <div id="recent-articles-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {recent_cards_html}
                    </div>
                    <div class="text-center mt-12">
                        <button id="load-more-btn" class="load-more-btn">
                            Load More
                        </button>
                    </div>
                </div>
            </section>

            <!-- ─── NEWSLETTER CAPTURE ────────────────────────────────── -->
            <section class="py-16 bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900">
                <div class="container mx-auto px-4 max-w-2xl text-center">
                    <p class="text-blue-300 text-xs font-bold uppercase tracking-widest mb-3">Intelligence Brief</p>
                    <h2 class="text-3xl font-bold text-white mb-4">
                        Stay ahead of the AI transformation.
                    </h2>
                    <p class="text-blue-200 mb-8 leading-relaxed">
                        Weekly analysis of AI infrastructure, enterprise transformation, smart mobility, and India's digital economy — delivered to your inbox.
                    </p>
                    <form class="flex flex-col sm:flex-row gap-3 justify-center" onsubmit="return false;">
                        <input type="email" placeholder="your@email.com"
                               class="flex-1 max-w-sm px-5 py-3 rounded-xl text-gray-900 focus:ring-2 focus:ring-blue-300 focus:outline-none text-sm"
                               aria-label="Email address">
                        <button type="submit"
                                class="bg-white text-blue-900 font-bold px-6 py-3 rounded-xl hover:bg-blue-50 transition-colors text-sm whitespace-nowrap">
                            Subscribe Free
                        </button>
                    </form>
                    <p class="text-blue-400 text-xs mt-4">No spam. Unsubscribe anytime.</p>
                </div>
            </section>

        </main>

        {generate_footer_html("home")}

        <!-- Load More JavaScript -->
        <script>
        (function() {{
            const remainingArticles = {remaining_articles_json};
            let currentPage = 0;
            const articlesPerPage = 6;
            const loadMoreBtn = document.getElementById('load-more-btn');
            const articlesGrid = document.getElementById('recent-articles-grid');

            function generateArticleCardHTML(article) {{
                let thumbnailUrl = article.thumbnailImageUrl || article.thumbnail || article.imageUrl || 'images/placeholder.webp';
                if (thumbnailUrl && thumbnailUrl.startsWith('dist/')) thumbnailUrl = thumbnailUrl.substring(5);
                const articleUrl = `articles/${{article.slug}}.html`;
                return `
                    <article class="article-card bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
                        <a href="${{articleUrl}}" class="block">
                            <div class="relative">
                                <img src="${{thumbnailUrl}}"
                                     alt="${{article.imageAltText}}"
                                     class="w-full h-48 object-cover"
                                     loading="lazy"
                                     onerror="this.src='images/placeholder.webp'">
                                <div class="absolute top-3 left-3">
                                    <span class="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                                        ${{article.category}}
                                    </span>
                                </div>
                            </div>
                            <div class="p-6">
                                <h2 class="text-xl font-bold text-gray-900 mb-3 hover:text-blue-600 transition-colors line-clamp-2">
                                    ${{article.title.length > 80 ? article.title.substring(0, 80) + '...' : article.title}}
                                </h2>
                                <p class="text-gray-600 text-sm mb-4 line-clamp-3">
                                    ${{article.excerpt.length > 150 ? article.excerpt.substring(0, 150) + '...' : article.excerpt}}
                                </p>
                                <div class="flex items-center justify-between text-sm text-gray-500 mt-4 pt-4 border-t border-gray-100">
                                    <div class="flex items-center space-x-3">
                                        <span class="flex items-center">
                                            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                                            </svg>
                                            ${{article.author}}
                                        </span>
                                        <span class="flex items-center">
                                            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.414-1.414L11 9.586V6z" clip-rule="evenodd"></path>
                                            </svg>
                                            ${{article.readingTimeMinutes}} min
                                        </span>
                                    </div>
                                    <span class="text-blue-600 font-medium">${{article.publishDate}}</span>
                                </div>
                            </div>
                        </a>
                    </article>`;
            }}

            if (loadMoreBtn) {{
                if (remainingArticles.length === 0) {{
                    loadMoreBtn.style.display = 'none';
                }} else {{
                    loadMoreBtn.addEventListener('click', function() {{
                        const startIndex = currentPage * articlesPerPage;
                        const endIndex = Math.min(startIndex + articlesPerPage, remainingArticles.length);
                        const articlesToLoad = remainingArticles.slice(startIndex, endIndex);
                        if (articlesToLoad.length === 0) {{ this.style.display = 'none'; return; }}
                        const originalText = this.innerHTML;
                        this.innerHTML = '<div class="loading-spinner"></div>Loading...';
                        this.disabled = true;
                        setTimeout(() => {{
                            articlesToLoad.forEach(article => {{
                                articlesGrid.insertAdjacentHTML('beforeend', generateArticleCardHTML(article));
                            }});
                            currentPage++;
                            if (endIndex >= remainingArticles.length) {{
                                this.style.display = 'none';
                            }} else {{
                                this.innerHTML = originalText;
                                this.disabled = false;
                            }}
                        }}, 800);
                    }});
                }}
            }}
        }})();
        </script>
    </body>
    </html>
    '''

    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(homepage_html)

    print(f"✅ Homepage generated: hero + 4 pillar sections + {len(recent_articles)} latest articles")

def generate_homepage_structured_data(articles_data):
    """Generate structured data for homepage E-E-A-T"""
    recent_articles = sorted(articles_data, key=lambda x: x.get('publishDate', ''), reverse=True)[:10]
    
    articles_json = []
    for article in recent_articles:
        article_data = {
            "@type": "NewsArticle",
            "headline": article['title'],
            "description": article.get('excerpt', ''),
            "datePublished": article.get('publishDate', ''),
            "dateModified": article.get('lastUpdated', article.get('publishDate', '')),
            "author": {
                "@type": "Person",
                "name": article.get('author', 'Editorial Team')
            },
            "publisher": {
                "@type": "Organization",
                "name": "Country's News",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://countrysnews.com/logo.svg"
                }
            }
        }
        articles_json.append(article_data)
    
    structured_data = {
        "@context": "https://schema.org",
        "@type": "NewsMediaOrganization",
        "name": "Country's News",
        "url": "https://countrysnews.com/",
        "logo": "https://countrysnews.com/logo.svg",
        "description": "Professional journalism platform delivering comprehensive news coverage with fact-checked content",
        "sameAs": [
            "https://twitter.com/countrysnews"
        ],
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": articles_json
        }
    }
    
    return f'<script type="application/ld+json">{json.dumps(structured_data, indent=2)}</script>'

def generate_advanced_category_pages(articles_data, unique_categories):
    """Generate advanced category pages with ads and features"""
    print(f"📝 Generating {len(unique_categories)} advanced category pages...")
    
    # Create categories directory
    categories_dir = os.path.join(OUTPUT_DIR, 'categories')
    os.makedirs(categories_dir, exist_ok=True)
    
    for category in unique_categories:
        # Filter articles for this category
        category_articles = [a for a in articles_data if a.get('category', DEFAULT_CATEGORY) == category]
        category_articles.sort(key=lambda x: x.get('publishDate', ''), reverse=True)
        
        generate_single_category_page(category, category_articles, unique_categories)
    
    print(f"✅ All {len(unique_categories)} advanced category pages generated")

def generate_single_category_page(category, category_articles, unique_categories):
    """Generate single advanced category page"""
    category_slug = generate_slug(category)
    
    # Show first 9 articles initially, keep rest for load more
    initial_articles = category_articles[:9]
    remaining_articles = category_articles[9:]
    
    # Generate article cards with ads interspersed
    articles_html = ""
    for i, article in enumerate(initial_articles):
        articles_html += generate_article_card(article, "category")
        # Add ad after every 3 articles
        if (i + 1) % 3 == 0 and i < len(initial_articles) - 1:
            articles_html += '''
            <div class="col-span-full">
                <div class="ad-container">
                    <div data-ad-slot="category-banner" aria-hidden="true"></div>
                </div>
            </div>
            '''
    
    # Generate structured data for category
    structured_data = generate_category_structured_data(category, category_articles)
    
    category_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>{category} News | Country's News</title>
        <meta name="description" content="Latest {category.lower()} news and updates from Country's News. Expert analysis and verified reporting on {category.lower()} topics.">
        <meta name="keywords" content="{category.lower()}, news, updates, analysis, {category.lower()} articles">
        
        <!-- E-E-A-T Meta Tags -->
        <meta name="publisher" content="Country's News">
        <meta name="article:section" content="{category}">
        
        <!-- Open Graph -->
        <meta property="og:title" content="{category} News | Country's News">
        <meta property="og:description" content="Latest {category.lower()} news and expert analysis from Country's News.">
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://countrysnews.com/categories/{category_slug}.html">
        <meta property="og:site_name" content="Country's News">
        
        <!-- Twitter Card -->
        <meta name="twitter:card" content="summary">
        <meta name="twitter:title" content="{category} News | Country's News">
        <meta name="twitter:description" content="Latest {category.lower()} news and expert analysis.">
        
        <!-- Canonical URL -->
        <link rel="canonical" href="https://countrysnews.com/categories/{category_slug}.html">
        
        {get_base_html_head()}
        
        <!-- Category Structured Data -->
        {structured_data}
    </head>
    <body>
        {generate_header_html(unique_categories, "category")}
        
        <main class="min-h-screen">
            <!-- Category Header -->
            <section class="bg-gradient-to-br from-blue-900 via-blue-700 to-purple-800 text-white py-16">
                <div class="container mx-auto px-4 text-center">
                    <!-- Breadcrumb -->
                    <nav class="mb-6 text-blue-200">
                        <a href="../index.html" class="hover:text-white">Home</a>
                        <span class="mx-2">/</span>
                        <span class="text-white">Categories</span>
                        <span class="mx-2">/</span>
                        <span class="text-white">{category}</span>
                    </nav>
                    
                    <h1 class="text-4xl md:text-6xl font-bold mb-4">
                        {category}
                        <span class="block text-2xl md:text-3xl font-normal text-blue-200 mt-2">
                            News & Updates
                        </span>
                    </h1>
                    
                    <p class="text-xl text-blue-100 max-w-2xl mx-auto mb-8">
                        Stay informed with the latest {category.lower()} news, expert analysis, and verified reporting from our trusted journalists.
                    </p>
                </div>
            </section>
            
            <!-- Articles Grid with Sidebar -->
            <section class="py-12">
                <div class="container mx-auto px-4">
                    <div class="flex flex-col lg:flex-row gap-8">
                        <!-- Main Content -->
                        <div class="lg:w-2/3">
                            <div class="flex items-center justify-between mb-8">
                                <h2 class="text-2xl font-bold text-gray-900">
                                    Latest {category} Articles 
                                    <span class="text-blue-600">({len(category_articles)})</span>
                                </h2>
                                
                                <!-- Sort Options -->
                                <div class="flex items-center space-x-2">
                                    <span class="text-sm text-gray-500">Sort by:</span>
                                    <select class="text-sm border border-gray-300 rounded-lg px-3 py-2 bg-white">
                                        <option>Latest First</option>
                                        <option>Oldest First</option>
                                        <option>Most Popular</option>
                                    </select>
                                </div>
                            </div>
                            
                            <!-- Articles Grid -->
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {articles_html}
                            </div>
                            
                            <!-- Load More Button -->
                            <div class="text-center mt-12">
                                <button id="load-more-btn" class="load-more-btn">
                                    Load More {category} Articles
                                </button>
                            </div>
                        </div>
                        
                        <!-- Sidebar -->
                        <aside class="lg:w-1/3">
                            <div class="sticky top-24 space-y-6">
                                <!-- Sidebar Ad -->
                                <div class="ad-container sidebar">
                                    <div data-ad-slot="category-sidebar-1" aria-hidden="true"></div>
                                </div>
                                
                                <!-- Category Stats -->
                                <div class="bg-gradient-to-br from-blue-50 to-indigo-100 p-6 rounded-xl border border-blue-200">
                                    <h3 class="text-xl font-bold text-gray-900 mb-4">{category} Statistics</h3>
                                    <div class="space-y-3">
                                        <div class="flex justify-between">
                                            <span class="text-gray-600">Total Articles:</span>
                                            <span class="font-semibold text-blue-600">{len(category_articles)}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span class="text-gray-600">This Week:</span>
                                            <span class="font-semibold text-green-600">12</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span class="text-gray-600">Expert Authors:</span>
                                            <span class="font-semibold text-purple-600">8</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <!-- Other Categories -->
                                <div class="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                                    <h3 class="text-xl font-bold text-gray-900 mb-4">Other Categories</h3>
                                    <div class="space-y-2">
                                        {generate_other_categories_html(unique_categories, category)}
                                    </div>
                                </div>
                                
                                <!-- Another Sidebar Ad -->
                                <div class="ad-container sidebar">
                                    <div data-ad-slot="category-sidebar-2" aria-hidden="true"></div>
                                </div>
                            </div>
                        </aside>
                    </div>
                </div>
            </section>
        </main>
        
        {generate_footer_html("category")}
        
        <!-- Category Load More JavaScript -->
        <script>
        // Category specific load more functionality
        (function() {{
            const remainingArticles = {json.dumps([{
                'title': article['title'],
                'slug': article['slug'],
                'author': article.get('author', 'Editorial Team'),
                'publishDate': article.get('publishDate', ''),
                'category': article.get('category', 'News'),
                'excerpt': article.get('excerpt', ''),
                'imageUrl': article.get('imageUrl', ''),
                'thumbnail': article.get('thumbnail', ''),
                'thumbnailImageUrl': article.get('thumbnailImageUrl', ''),
                'imageAltText': article.get('imageAltText', article['title']),
                'readingTimeMinutes': article.get('readingTimeMinutes', 5)
            } for article in remaining_articles] if remaining_articles else [])};
            
            let currentPage = 0;
            const articlesPerPage = 6;
            const loadMoreBtn = document.getElementById('load-more-btn');
            const articlesGrid = document.querySelector('.grid.grid-cols-1.md\\\\:grid-cols-2.gap-8');
            
            function generateArticleCardHTML(article) {{
                // Remove 'dist/' prefix from thumbnailImageUrl if present
                let thumbnailUrl = article.thumbnailImageUrl || article.thumbnail || article.imageUrl || '../images/placeholder.webp';
                if (thumbnailUrl && thumbnailUrl.startsWith('dist/')) {{
                    thumbnailUrl = '../' + thumbnailUrl.substring(5); // Remove 'dist/' and add '../'
                }}
                const articleUrl = `../articles/${{article.slug}}.html`;
                
                return `
                    <article class="article-card bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
                        <a href="${{articleUrl}}" class="block">
                            <div class="relative">
                                <img src="${{thumbnailUrl}}" 
                                     alt="${{article.imageAltText}}"
                                     class="w-full h-48 object-cover" 
                                     loading="lazy"
                                     onerror="this.src='../images/placeholder.webp'">
                                <div class="absolute top-3 left-3">
                                    <span class="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                                        ${{article.category}}
                                    </span>
                                </div>
                            </div>
                            <div class="p-6">
                                <h2 class="text-xl font-bold text-gray-900 mb-3 hover:text-blue-600 transition-colors line-clamp-2">
                                    ${{article.title.length > 80 ? article.title.substring(0, 80) + '...' : article.title}}
                                </h2>
                                
                                <p class="text-gray-600 text-sm mb-4 line-clamp-3">
                                    ${{article.excerpt.length > 150 ? article.excerpt.substring(0, 150) + '...' : article.excerpt}}
                                </p>
                                
                                <div class="flex items-center justify-between text-sm text-gray-500 mt-4 pt-4 border-t border-gray-100">
                                    <div class="flex items-center space-x-3">
                                        <span class="flex items-center">
                                            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                                            </svg>
                                            ${{article.author}}
                                        </span>
                                        <span class="flex items-center">
                                            <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.414-1.414L11 9.586V6z" clip-rule="evenodd"></path>
                                            </svg>
                                            ${{article.readingTimeMinutes}} min
                                        </span>
                                    </div>
                                    <span class="text-blue-600 font-medium">${{article.publishDate}}</span>
                                </div>
                            </div>
                        </a>
                    </article>
                `;
            }}
            
            if (loadMoreBtn) {{
                if (remainingArticles.length === 0) {{
                    loadMoreBtn.style.display = 'none';
                }} else {{
                    loadMoreBtn.addEventListener('click', function() {{
                        const startIndex = currentPage * articlesPerPage;
                        const endIndex = Math.min(startIndex + articlesPerPage, remainingArticles.length);
                        const articlesToLoad = remainingArticles.slice(startIndex, endIndex);
                        
                        if (articlesToLoad.length === 0) {{
                            this.style.display = 'none';
                            return;
                        }}
                        
                        // Show loading state
                        const originalText = this.innerHTML;
                        this.innerHTML = '<div class="loading-spinner"></div>Loading...';
                        this.disabled = true;
                        
                        setTimeout(() => {{
                            // Add new articles to the grid
                            articlesToLoad.forEach(article => {{
                                const articleHTML = generateArticleCardHTML(article);
                                articlesGrid.insertAdjacentHTML('beforeend', articleHTML);
                            }});
                            
                            currentPage++;
                            
                            // Check if there are more articles to load
                            if (endIndex >= remainingArticles.length) {{
                                this.style.display = 'none';
                            }} else {{
                                this.innerHTML = originalText;
                                this.disabled = false;
                            }}
                        }}, 1000);
                    }});
                }}
            }}
        }})();
        </script>
    </body>
    </html>
    '''
    
    category_path = os.path.join(OUTPUT_DIR, 'categories', f"{category_slug}.html")
    with open(category_path, 'w', encoding='utf-8') as f:
        f.write(category_html)

def generate_other_categories_html(unique_categories, current_category):
    """Generate other categories navigation"""
    html = ""
    for category in unique_categories:
        if category != current_category:
            category_slug = generate_slug(category)
            html += f'''
            <a href="{category_slug}.html" 
               class="block py-2 px-3 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
                {category}
            </a>
            '''
    return html

def generate_category_structured_data(category, articles):
    """Generate structured data for category pages"""
    articles_data = []
    for article in articles[:10]:  # Limit to first 10 articles
        articles_data.append({
            "@type": "NewsArticle",
            "headline": article['title'],
            "datePublished": article.get('publishDate', ''),
            "author": {
                "@type": "Person",
                "name": article.get('author', 'Editorial Team')
            }
        })
    
    structured_data = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": f"{category} News",
        "description": f"Latest {category.lower()} news and updates",
        "url": f"https://countrysnews.com/categories/{generate_slug(category)}.html",
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": articles_data
        }
    }
    
    return f'<script type="application/ld+json">{json.dumps(structured_data, indent=2)}</script>'

def generate_static_pages(unique_categories):
    """Generate static pages (About, Contact, etc.)"""
    print("📝 Generating static pages...")
    
    # Generate About Us page
    generate_about_page(unique_categories)
    
    # Generate Contact page
    generate_contact_page(unique_categories)
    
    # Generate Privacy Policy page
    generate_privacy_page(unique_categories)
    
    # Generate Disclaimer page
    generate_disclaimer_page(unique_categories)
    
    print("✅ Static pages generated")

def generate_about_page(unique_categories):
    """Write a redirect stub for the legacy about-us.html URL."""
    redirect_html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>About Us | Country's News</title>
<meta http-equiv="refresh" content="0; url=/about/">
<link rel="canonical" href="https://countrysnews.com/about/">
</head>
<body>
<p>Redirecting to <a href="/about/">About Us</a>…</p>
</body>
</html>'''
    with open(os.path.join(OUTPUT_DIR, 'about-us.html'), 'w', encoding='utf-8') as f:
        f.write(redirect_html)
def generate_contact_page(unique_categories):
    """Write a redirect stub for the legacy contact.html URL."""
    redirect_html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Contact | Country's News</title>
<meta http-equiv="refresh" content="0; url=/contact/">
<link rel="canonical" href="https://countrysnews.com/contact/">
</head>
<body>
<p>Redirecting to <a href="/contact/">Contact</a>…</p>
</body>
</html>'''
    with open(os.path.join(OUTPUT_DIR, 'contact.html'), 'w', encoding='utf-8') as f:
        f.write(redirect_html)

def generate_privacy_page(unique_categories):
    """Generate Privacy Policy page"""
    privacy_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Privacy Policy | Country's News</title>
        <meta name="description" content="Country's News Privacy Policy - Learn how we protect your privacy and handle your data.">
        
        {get_base_html_head()}
    </head>
    <body>
        {generate_header_html(unique_categories, "home")}
        
        <main class="min-h-screen py-12">
            <div class="container mx-auto px-4 max-w-4xl">
                <h1 class="text-4xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
                
                <div class="prose prose-lg max-w-none">
                    <p class="text-gray-600 mb-8">Last updated: {datetime.now().strftime('%B %d, %Y')}</p>
                    
                    <h2>Information We Collect</h2>
                    <p>We collect information to provide better services to our users. This includes information you provide directly and data collected automatically when you visit our site.</p>
                    
                    <h2>How We Use Information</h2>
                    <p>We use the information we collect to maintain, protect and improve our services, to develop new ones, and to protect Country's News and our users.</p>
                    
                    <h2>Information Sharing</h2>
                    <p>We do not share personal information with companies, organizations and individuals outside of Country's News except in specific circumstances outlined in this policy.</p>
                    
                    <h2>Data Security</h2>
                    <p>We work hard to protect Country's News and our users from unauthorized access to or unauthorized alteration, disclosure or destruction of information we hold.</p>
                    
                    <h2>Contact Us</h2>
                    <p>If you have any questions about this Privacy Policy, please contact us at privacy@countrysnews.com.</p>
                </div>
                
                <!-- Ad -->
                <div class="ad-container my-12">
                    <div data-ad-slot="privacy-banner" aria-hidden="true"></div>
                </div>
            </div>
        </main>
        
        {generate_footer_html("home")}
    </body>
    </html>
    '''
    
    with open(os.path.join(OUTPUT_DIR, 'privacy-policy.html'), 'w', encoding='utf-8') as f:
        f.write(privacy_html)

def generate_disclaimer_page(unique_categories):
    """Generate Disclaimer page"""
    disclaimer_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Disclaimer | Country's News</title>
        <meta name="description" content="Country's News Disclaimer - Important information about our content and services.">
        
        {get_base_html_head()}
    </head>
    <body>
        {generate_header_html(unique_categories, "home")}
        
        <main class="min-h-screen py-12">
            <div class="container mx-auto px-4 max-w-4xl">
                <h1 class="text-4xl font-bold text-gray-900 mb-8">Disclaimer</h1>
                
                <div class="prose prose-lg max-w-none">
                    <h2>General Information</h2>
                    <p>The information on this website is published in good faith and for general information purpose only. Country's News does not make any warranties about the completeness, reliability and accuracy of this information.</p>
                    
                    <h2>Editorial Standards</h2>
                    <p>We strive to maintain the highest standards of journalistic integrity. All content is fact-checked and verified by our editorial team. However, opinions expressed in articles are those of the authors and do not necessarily reflect the views of Country's News.</p>
                    
                    <h2>External Links</h2>
                    <p>Our website may contain links to external websites. We have no control over the content and nature of these sites and cannot be held responsible for their content or privacy practices.</p>
                    
                    <h2>Advertising</h2>
                    <p>We may display advertisements from third parties. The presence of advertisements does not constitute endorsement by Country's News of the products or services advertised.</p>
                </div>
                
                <!-- Ad -->
                <div class="ad-container my-12">
                    <div data-ad-slot="disclaimer-banner" aria-hidden="true"></div>
                </div>
            </div>
        </main>
        
        {generate_footer_html("home")}
    </body>
    </html>
    '''
    
    with open(os.path.join(OUTPUT_DIR, 'disclaimer.html'), 'w', encoding='utf-8') as f:
        f.write(disclaimer_html)

def generate_sitemap(articles_data):
    """Generate XML sitemap with proper URL encoding"""
    print("📝 Generating XML sitemap...")
    
    # Write sitemap directly to avoid any string concatenation issues
    with open(os.path.join(OUTPUT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        
        # Homepage
        f.write('    <!-- Homepage -->\n')
        f.write('    <url>\n')
        f.write('        <loc>https://countrysnews.com/</loc>\n')
        f.write(f'        <lastmod>{date.today().isoformat()}</lastmod>\n')
        f.write('    </url>\n\n')
        
        # Static Pages
        f.write('    <!-- Static Pages -->\n')
        f.write('    <url>\n')
        f.write('        <loc>https://countrysnews.com/about/</loc>\n')
        about_path = os.path.join(OUTPUT_DIR, 'about', 'index.html')
        if os.path.exists(about_path):
            about_mtime = date.fromtimestamp(os.path.getmtime(about_path)).isoformat()
            f.write(f'        <lastmod>{about_mtime}</lastmod>\n')
        f.write('    </url>\n')
        f.write('    <url>\n')
        f.write('        <loc>https://countrysnews.com/contact/</loc>\n')
        contact_path = os.path.join(OUTPUT_DIR, 'contact', 'index.html')
        if os.path.exists(contact_path):
            contact_mtime = date.fromtimestamp(os.path.getmtime(contact_path)).isoformat()
            f.write(f'        <lastmod>{contact_mtime}</lastmod>\n')
        f.write('    </url>\n\n')
        
        # Add category pages
        categories = set([article.get('category', DEFAULT_CATEGORY) for article in articles_data])
        for category in categories:
            category_slug = generate_slug(category).strip()
            f.write('    <url>\n')
            f.write(f'        <loc>https://countrysnews.com/categories/{category_slug}.html</loc>\n')
            cat_path = os.path.join(OUTPUT_DIR, 'categories', f'{category_slug}.html')
            if os.path.exists(cat_path):
                cat_mtime = date.fromtimestamp(os.path.getmtime(cat_path)).isoformat()
                f.write(f'        <lastmod>{cat_mtime}</lastmod>\n')
            f.write('    </url>\n')
        
        # Add article pages
        for article in articles_data:
            article_slug = str(article['slug']).strip().replace('\n', '').replace('\r', '')
            # Escape any special characters that might cause XML issues
            escaped_slug = article_slug.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            f.write('    <url>\n')
            f.write(f'        <loc>https://countrysnews.com/articles/{escaped_slug}.html</loc>\n')
            # Use lastmod from article data or file modification time
            lastmod = None
            if isinstance(article.get('lastmod'), str) and article.get('lastmod'):
                lastmod = article.get('lastmod')
            elif isinstance(article.get('datePublished'), str) and article.get('datePublished'):
                lastmod = article.get('datePublished')
            else:
                article_path = os.path.join(OUTPUT_DIR, 'articles', f'{escaped_slug}.html')
                if os.path.exists(article_path):
                    lastmod = date.fromtimestamp(os.path.getmtime(article_path)).isoformat()
            if lastmod:
                # Ensure ISO date format (YYYY-MM-DD)
                try:
                    parsed = date.fromisoformat(str(lastmod)[:10])
                    f.write(f'        <lastmod>{parsed.isoformat()}</lastmod>\n')
                except Exception:
                    # Skip lastmod if parsing fails
                    pass
            f.write('    </url>\n')
        
        f.write('</urlset>\n')
    
    print("✅ XML sitemap generated")

def validate_and_fix_sitemap():
    """Validate sitemap XML and fix any issues - CRITICAL for Google Search Console"""
    print("🔍 Validating sitemap XML structure...")
    
    sitemap_path = os.path.join(OUTPUT_DIR, 'sitemap.xml')
    
    if not os.path.exists(sitemap_path):
        print("❌ CRITICAL ERROR: Sitemap file not found!")
        return False
    
    try:
        # Parse and validate XML structure
        import xml.etree.ElementTree as ET
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # Check namespace
        expected_namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
        if root.tag != f'{{{expected_namespace}}}urlset':
            print(f"❌ CRITICAL ERROR: Invalid sitemap namespace. Expected {expected_namespace}")
            return False
        
        # Get all URL entries
        urls = root.findall(f'.//{{{expected_namespace}}}url')
        print(f"📊 Found {len(urls)} URL entries in sitemap")
        
        # Validate each URL
        problematic_urls = 0
        invalid_chars = 0
        too_long_urls = 0
        
        for i, url in enumerate(urls):
            loc_element = url.find(f'{{{expected_namespace}}}loc')
            if loc_element is None:
                print(f"❌ CRITICAL ERROR: URL entry {i+1} missing <loc> element")
                problematic_urls += 1
                continue
                
            url_text = loc_element.text
            if not url_text:
                print(f"❌ CRITICAL ERROR: URL entry {i+1} has empty <loc> element")
                problematic_urls += 1
                continue
            
            # Check for line breaks (the main issue)
            if '\n' in url_text or '\r' in url_text:
                print(f"❌ CRITICAL ERROR: URL entry {i+1} contains line breaks: {repr(url_text[:50])}...")
                problematic_urls += 1
            
            # Check for invalid characters
            if any(ord(c) < 32 and c not in '\t\n\r' for c in url_text):
                print(f"❌ CRITICAL ERROR: URL entry {i+1} contains invalid control characters")
                invalid_chars += 1
            
            # Check URL length (Google recommends < 2048 characters)
            if len(url_text) > 2048:
                print(f"⚠️  WARNING: URL entry {i+1} is very long ({len(url_text)} chars): {url_text[:50]}...")
                too_long_urls += 1
            
            # Validate URL format
            if not url_text.startswith(('http://', 'https://')):
                print(f"❌ CRITICAL ERROR: URL entry {i+1} has invalid protocol: {url_text[:50]}...")
                problematic_urls += 1
        
        # Report results
        total_issues = problematic_urls + invalid_chars
        
        if total_issues == 0:
            print("✅ SITEMAP VALIDATION PASSED: All URLs are properly formatted")
            if too_long_urls > 0:
                print(f"⚠️  Note: {too_long_urls} URLs are longer than recommended (>2048 chars)")
            return True
        else:
            print(f"❌ SITEMAP VALIDATION FAILED: {total_issues} critical issues found")
            print(f"   - URLs with line breaks: {problematic_urls}")
            print(f"   - URLs with invalid characters: {invalid_chars}")
            print(f"   - URLs too long: {too_long_urls}")
            
            # Attempt to fix the sitemap
            print("🔧 Attempting to fix sitemap issues...")
            return fix_sitemap_issues(sitemap_path, tree, expected_namespace)
            
    except ET.ParseError as e:
        print(f"❌ CRITICAL ERROR: Sitemap XML is malformed: {e}")
        print("🔧 Attempting to regenerate sitemap...")
        # Try to regenerate sitemap
        try:
            articles_data = load_articles()
            generate_sitemap(articles_data)
            print("✅ Sitemap regenerated successfully")
            return validate_and_fix_sitemap()  # Recursive validation
        except Exception as regen_error:
            print(f"❌ CRITICAL ERROR: Failed to regenerate sitemap: {regen_error}")
            return False
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Unexpected error during sitemap validation: {e}")
        return False

def fix_sitemap_issues(sitemap_path, tree, namespace):
    """Attempt to fix sitemap issues"""
    try:
        root = tree.getroot()
        urls = root.findall(f'.//{{{namespace}}}url')
        fixed_count = 0
        
        for url in urls:
            loc_element = url.find(f'{{{namespace}}}loc')
            if loc_element is not None and loc_element.text:
                original_text = loc_element.text
                
                # Fix line breaks and control characters
                cleaned_text = original_text.replace('\n', '').replace('\r', '').strip()
                
                # Remove any other control characters except tab
                cleaned_text = ''.join(c for c in cleaned_text if ord(c) >= 32 or c == '\t')
                
                if cleaned_text != original_text:
                    loc_element.text = cleaned_text
                    fixed_count += 1
        
        if fixed_count > 0:
            # Write the fixed sitemap
            tree.write(sitemap_path, encoding='utf-8', xml_declaration=True)
            print(f"✅ Fixed {fixed_count} URL issues in sitemap")
            
            # Validate again to ensure fix worked
            return validate_and_fix_sitemap()
        else:
            print("❌ No fixable issues found, but validation still failed")
            return False
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Failed to fix sitemap: {e}")
        return False

def perform_final_validation():
    """Final validation checks after generation"""
    print("🔍 Performing final validation checks...")
    
    critical_files = [
        'index.html',
        'sitemap.xml',
        'robots.txt',
        'rss.xml'
    ]
    
    missing_files = []
    for file in critical_files:
        file_path = os.path.join(OUTPUT_DIR, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ CRITICAL ERROR: Missing critical files: {missing_files}")
        return False
    
    # Check if articles directory exists and has files
    articles_dir = os.path.join(OUTPUT_DIR, 'articles')
    if not os.path.exists(articles_dir):
        print("❌ CRITICAL ERROR: Articles directory not created")
        return False
    
    article_files = [f for f in os.listdir(articles_dir) if f.endswith('.html')]
    if not article_files:
        print("❌ CRITICAL ERROR: No article HTML files generated")
        return False
    
    # Check categories directory
    categories_dir = os.path.join(OUTPUT_DIR, 'categories')
    if not os.path.exists(categories_dir):
        print("❌ CRITICAL ERROR: Categories directory not created")
        return False
    
    category_files = [f for f in os.listdir(categories_dir) if f.endswith('.html')]
    if not category_files:
        print("❌ CRITICAL ERROR: No category HTML files generated")
        return False
    
    print(f"✅ All critical files present")
    print(f"✅ Generated {len(article_files)} article pages")
    print(f"✅ Generated {len(category_files)} category pages")
    print("✅ Final validation passed")
    return True

def generate_robots_txt():
    """Generate robots.txt"""
    robots_content = '''User-agent: *
Allow: /

Sitemap: https://countrysnews.com/sitemap.xml
'''
    
    with open(os.path.join(OUTPUT_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(robots_content)

def generate_rss_feed(articles_data):
    """Generate RSS feed"""
    print("📝 Generating RSS feed...")
    
    # Sort articles by date (newest first)
    sorted_articles = sorted(articles_data, key=lambda x: x.get('publishDate', ''), reverse=True)[:20]
    
    rss_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Country's News</title>
        <description>Your trusted source for verified news with expert analysis</description>
        <link>https://countrysnews.com/</link>
        <language>en-us</language>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S')} GMT</lastBuildDate>
        
'''
    
    for article in sorted_articles:
        rss_content += f'''        <item>
            <title><![CDATA[{article['title']}]]></title>
            <description><![CDATA[{article.get('excerpt', '')[:500]}]]></description>
            <link>https://countrysnews.com/articles/{article['slug']}.html</link>
            <guid>https://countrysnews.com/articles/{article['slug']}.html</guid>
            <pubDate>{article.get('publishDate', '')}</pubDate>
            <category>{article.get('category', 'News')}</category>
        </item>
'''
    
    rss_content += '''    </channel>
</rss>'''
    
    with open(os.path.join(OUTPUT_DIR, 'rss.xml'), 'w', encoding='utf-8') as f:
        f.write(rss_content)
    
    print("✅ RSS feed generated")

def generate_advanced_article_pages(articles_data, unique_categories):
    """Generate advanced individual article pages with E-E-A-T"""
    print(f"📝 Generating {len(articles_data)} advanced article pages...")
    
    # Create articles directory
    articles_dir = os.path.join(OUTPUT_DIR, 'articles')
    os.makedirs(articles_dir, exist_ok=True)
    
    # Precompute related articles for all articles
    related_map = compute_related_articles_map(articles_data)

    for i, article in enumerate(articles_data):
        generate_single_advanced_article(article, unique_categories, related_map.get(article.get('slug', ''), []))
        if (i + 1) % 20 == 0:
            print(f"   ✅ Generated {i + 1}/{len(articles_data)} articles")
    
    print(f"✅ All {len(articles_data)} advanced article pages generated")

def generate_single_advanced_article(article, unique_categories, related_list):
    """Generate single advanced article page"""
    
    # Generate author profile HTML
    author_profile_html = generate_author_profile(article)
    
    # Generate related articles
    related_articles_html = generate_related_articles(article, related_list)
    
    # Generate social sharing
    social_sharing_html = generate_social_sharing(article)
    
    # Generate structured data for article
    structured_data = generate_article_structured_data(article)
    
    # Get article image (relative for in-page use) and public absolute URL for meta/og/twitter/structured-data
    raw_thumb = article.get('thumbnailImageUrl', '') or ''
    raw_og = article.get('ogImage', '') or ''
    raw_image = raw_thumb or raw_og or ''
    # Keep a relative form for in-page img tags (previous logic)
    article_image = raw_image
    if article_image and article_image.startswith('dist/'):
        article_image = article_image.replace('dist/', '../')

    # Public absolute URL for meta tags and structured data
    def _to_public_url(path: str) -> str:
        if not path:
            return ''
        path = str(path)
        if path.startswith('http://') or path.startswith('https://'):
            return path
        if path.startswith('dist/'):
            return f"https://countrysnews.com/{path[len('dist/'):]}"
        if path.startswith('/'):
            return f"https://countrysnews.com{path}"
        # fallback
        return f"https://countrysnews.com/{path.lstrip('./')}"

    article_image_public = _to_public_url(raw_image)
    
    # Generate social hashtags
    hashtags_html = ""
    social_hashtags = article.get('socialMediaHashtags', [])
    if social_hashtags:
        hashtags_html = f'''
        <div class="hashtags">
            <h3 class="text-sm font-semibold text-gray-500 mb-2">TRENDING TOPICS</h3>
            <div class="flex flex-wrap gap-2">
                {' '.join([f'<span class="hashtag">#{tag}</span>' for tag in social_hashtags[:5]])}
            </div>
        </div>
        '''

    # Prepare content HTML (support Markdown) and fix inline image paths for article pages
    # 1) If content appears to be plain Markdown (no HTML tags), convert it to HTML
    # 2) Rewrite any 'dist/' image paths to '../' since article pages live in dist/articles/
    raw_content_html = article.get('content', article.get('body', '')) or ""

    def looks_like_html(text: str) -> bool:
        return bool(re.search(r'<\s*(p|h[1-6]|ul|ol|li|div|section|article|img|figure|blockquote|pre|code|table)\b', text, re.IGNORECASE))

    def has_markdown(text: str) -> bool:
        return (
            bool(re.search(r'(^|\n)\s*[\*-]\s+\S', text)) or  # bullets
            bool(re.search(r'(^|\n)\s*\d+\.\s+\S', text)) or  # ordered lists
            '```' in text or                                      # fenced code
            bool(re.search(r'(^|\n)#{1,6}\s+\S', text)) or      # ATX headings
            bool(re.search(r'\*\*[^\n]+\*\*', text))          # bold
        )

    # Normalize common Markdown artifacts before conversion
    normalized = raw_content_html
    # Insert line breaks before list items when they are crammed after a colon
    normalized = re.sub(r':\s*([\*-]\s+)', r':\n\n\1', normalized)
    # Ensure there is a newline before subsequent bullets if missing
    normalized = re.sub(r'(\S)\s+(\*[\s\S])', r'\1\n\n\2', normalized)
    # Auto-close unbalanced fenced code blocks
    if normalized.count('```') % 2 == 1:
        normalized = normalized.rstrip() + '\n```\n'

    content_html = normalized
    if normalized.strip() and (has_markdown(normalized) or not looks_like_html(normalized)):
        try:
            extensions = ['extra', 'sane_lists', 'smarty', 'tables', 'fenced_code', 'attr_list']
            # Try enabling Markdown-in-HTML if available
            try:
                extensions.append('md_in_html')
            except Exception:
                pass
            content_html = md.markdown(normalized, extensions=extensions)
        except Exception:
            content_html = normalized  # fallback

    try:
        fixed_content_html = re.sub(r'src=(["\'])dist/', r'src=\1../', content_html)
    except Exception:
        fixed_content_html = content_html

    # Auto-generate a Table of Contents (TOC) by scanning headings and injecting IDs
    def build_toc_and_inject_ids(html: str):
        # Find all h2/h3 headings
        heading_pattern = re.compile(r'<h([2-3])(\s[^>]*)?>(.*?)</h[2-3]>', re.IGNORECASE | re.DOTALL)
        headings = []
        used_ids = defaultdict(int)

        def slugify(text: str) -> str:
            base = re.sub(r"<[^>]+>", "", text)
            base = re.sub(r"[^a-z0-9\s-]", "", base.lower())
            base = re.sub(r"[\s-]+", "-", base).strip('-') or "section"
            used_ids[base] += 1
            return base if used_ids[base] == 1 else f"{base}-{used_ids[base]}"

        # Inject ids into headings
        def repl(m):
            level = m.group(1)
            attrs = m.group(2) or ""
            title_html = m.group(3)
            anchor_id = slugify(title_html)
            if 'id=' not in attrs:
                attrs = (attrs + f' id="{anchor_id}"').strip()
            return f"<h{level} {attrs}>{title_html}</h{level}>"

        html_with_ids = heading_pattern.sub(repl, html)

        # Collect headings for TOC
        for m in heading_pattern.finditer(html_with_ids):
            level = int(m.group(1))
            attrs = m.group(2) or ""
            title_html = m.group(3)
            # extract id value
            id_match = re.search(r'id=["\']([^"\']+)["\']', attrs)
            anchor_id = id_match.group(1) if id_match else slugify(title_html)
            # Strip tags in title for display
            title_text = re.sub(r"<[^>]+>", "", title_html).strip()
            headings.append({"level": level, "id": anchor_id, "title": title_text})

        # Build TOC HTML
        if headings:
            toc_links = []
            for h in headings:
                indent = "ml-0" if h["level"] == 2 else "ml-4"
                toc_links.append(f'<a href="#{h["id"]}" class="block text-blue-600 hover:text-blue-800 {indent}">{h["title"]}</a>')
            toc_html = '\n'.join(toc_links)
        else:
            toc_html = ''

        return html_with_ids, toc_html

    fixed_content_html, dynamic_toc_html = build_toc_and_inject_ids(fixed_content_html)
    
    # Helper to safely escape attribute values
    esc = html.escape

    article_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>{esc(article['title'])} | Country's News</title>
        <meta name="description" content="{esc(article.get('excerpt', '')[:160])}">
        <meta name="keywords" content="{esc(', '.join(article.get('keywords', [])))}">
        
        <!-- E-E-A-T Meta Tags -->
        <meta name="author" content="{article.get('author', 'Editorial Team')}">
        <meta name="publisher" content="Country's News">
        <meta name="article:published_time" content="{article.get('publishDate', '')}">
        <meta name="article:modified_time" content="{article.get('lastUpdated', article.get('publishDate', ''))}">
        <meta name="article:section" content="{article.get('category', 'News')}">
        
        <!-- Open Graph -->
    <meta property="og:title" content="{esc(article['title'])}">
    <meta property="og:description" content="{esc(article.get('excerpt', '')[:160])}">
        <meta property="og:type" content="article">
        <meta property="og:url" content="https://countrysnews.com/articles/{article['slug']}.html">
    <meta property="og:image" content="{article_image_public}">
        <meta property="og:site_name" content="Country's News">
        
        <!-- Twitter Card -->
        <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(article['title'])}">
    <meta name="twitter:description" content="{esc(article.get('excerpt', '')[:160])}">
    <meta name="twitter:image" content="{article_image_public}">
        
        <!-- Canonical URL -->
        <link rel="canonical" href="https://countrysnews.com/articles/{article['slug']}.html">
        
        {get_base_html_head()}
        
        <!-- Article Structured Data -->
        {structured_data}
    </head>
    <body>
        {generate_header_html(unique_categories, "article")}
        
        <main class="min-h-screen">
            <article class="container mx-auto px-4 py-8 max-w-4xl">
                <!-- Article Header -->
                <header class="mb-8">
                    <!-- Breadcrumb -->
                    <nav class="mb-6 text-sm text-gray-500">
                        <a href="../index.html" class="hover:text-blue-600">Home</a> 
                        <span class="mx-2">/</span>
                        <a href="../categories/{generate_slug(article.get('category', 'News'))}.html" class="hover:text-blue-600">{article.get('category', 'News')}</a>
                        <span class="mx-2">/</span>
                        <span class="text-gray-700">{article['title'][:50]}...</span>
                    </nav>
                    
                    <!-- Category Badge -->
                    <div class="mb-4">
                        <span class="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-semibold">
                            {article.get('category', 'News')}
                        </span>
                    </div>
                    
                    <!-- Article Title -->
                    <h1 class="text-4xl md:text-5xl font-bold text-gray-900 leading-tight mb-6">
                        {article['title']}
                    </h1>
                    
                    <!-- Article Meta -->
                    <div class="flex flex-wrap items-center gap-6 text-sm text-gray-600 mb-8">
                        <div class="flex items-center">
                            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"></path>
                            </svg>
                            By <span class="font-semibold text-gray-900">{article.get('author', 'Editorial Team')}</span>
                        </div>
                        <div class="flex items-center">
                            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.414-1.414L11 9.586V6z" clip-rule="evenodd"></path>
                            </svg>
                            {article.get('publishDate', '')}
                        </div>
                        <div class="flex items-center">
                            <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                            {article.get('readingTimeMinutes', 5)} min read
                        </div>
                    </div>
                    
                    <!-- Featured Image -->
                    <div class="mb-8">
                        <img src="{article_image}" 
                             alt="{article.get('imageAltText', article['title'])}" 
                             class="w-full h-64 md:h-96 object-cover rounded-xl shadow-lg"
                             onerror="this.style.display='none'">
                        {f'<p class="text-sm text-gray-500 mt-2 italic">{article.get("imageCaption", "")}</p>' if article.get('imageCaption') else ''}
                    </div>
                    
                    <!-- Social Sharing -->
                    {social_sharing_html}
                </header>
                
                <!-- Article Content with Sidebar -->
                <div class="flex flex-col lg:flex-row gap-8">
                    <div class="lg:w-2/3">
                        <!-- Mobile TOC (visible only on small screens) -->
                        {(
                            f'''<div class="bg-blue-50 p-6 rounded-xl border border-blue-200 mb-6 block lg:hidden">
                                <h3 class="text-lg font-bold text-gray-900 mb-4">In This Article</h3>
                                <nav class="space-y-2 text-sm">
                                    {dynamic_toc_html}
                                </nav>
                            </div>'''
                            if dynamic_toc_html else ''
                        )}
                        <!-- Article Body -->
                        <div class="article-content prose prose-lg max-w-none">
                                    {fixed_content_html}
                        </div>
                        
                        <!-- In-Content Ad -->
                        <div class="ad-container my-8">
                            <div data-ad-slot="article-content-1" aria-hidden="true"></div>
                        </div>
                        
                        <!-- Social Hashtags -->
                        {hashtags_html}
                        
                        <!-- Author Profile -->
                        {author_profile_html}
                        
                        <!-- Second In-Content Ad -->
                        <div class="ad-container my-8">
                            <div data-ad-slot="article-content-2" aria-hidden="true"></div>
                        </div>
                    </div>
                    
                    <!-- Sidebar -->
                    <aside class="lg:w-1/3">
                        <!-- Sticky Sidebar -->
                        <div class="sticky top-24 space-y-6">
                            <!-- Sidebar Ad -->
                            <div class="ad-container sidebar">
                                <div data-ad-slot="article-sidebar-1" aria-hidden="true"></div>
                            </div>
                            
                            <!-- Table of Contents (desktop only) -->
                            {f'''<div class="bg-blue-50 p-6 rounded-xl border border-blue-200 hidden lg:block">
                                <h3 class="text-lg font-bold text-gray-900 mb-4">In This Article</h3>
                                <nav class="space-y-2 text-sm">
                                    {dynamic_toc_html if dynamic_toc_html else '<span class="text-gray-500 text-sm">No sections available</span>'}
                                </nav>
                            </div>''' }
                            
                            <!-- Related Articles -->
                            {related_articles_html}
                            
                            <!-- Another Sidebar Ad -->
                            <div class="ad-container sidebar">
                                <div data-ad-slot="article-sidebar-2" aria-hidden="true"></div>
                            </div>
                        </div>
                    </aside>
                </div>
            </article>
        </main>
        
        {generate_footer_html("article")}
    </body>
    </html>
    '''
    
    article_path = os.path.join(OUTPUT_DIR, 'articles', f"{article['slug']}.html")
    with open(article_path, 'w', encoding='utf-8') as f:
        f.write(article_html)

def generate_author_profile(article):
    """Generate author profile section using named persona fields."""
    author_name = article.get('author', 'Editorial Team')
    author_title = article.get('authorTitle', 'Technology Analyst')
    author_bio = article.get('authorBio', (
        f"{author_name} is an experienced technology analyst at Country's News, "
        "specialising in AI infrastructure, enterprise transformation, and digital strategy."
    ))

    return f'''
    <div class="author-profile">
        <div class="flex items-start space-x-4">
            <div class="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                <svg class="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
                </svg>
            </div>
            <div class="flex-1">
                <h3 class="text-xl font-bold text-gray-900 mb-1">About {author_name}</h3>
                <p class="text-sm text-blue-600 font-medium mb-2">{author_title} · Country&#39;s News Intelligence</p>
                <p class="text-gray-600 text-sm">{author_bio}</p>
            </div>
        </div>
    </div>
    '''

def generate_social_sharing(article):
    """Generate social sharing buttons"""
    article_url = f"https://countrysnews.com/articles/{article['slug']}.html"
    article_title = quote(article['title'])
    
    return f'''
    <div class="flex items-center gap-4 py-4 border-y border-gray-200 mb-8">
        <span class="text-sm font-semibold text-gray-700">Share:</span>
        <div class="flex gap-2">
            <a href="https://twitter.com/intent/tweet?text={article_title}&url={article_url}" 
               target="_blank" 
               rel="noopener"
               title="Share on Twitter"
               class="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-lg transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84"/>
                </svg>
            </a>
            <a href="https://www.facebook.com/sharer/sharer.php?u={article_url}" 
               target="_blank"
               rel="noopener"
               title="Share on Facebook"
               class="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M20 10c0-5.523-4.477-10-10-10S0 4.477 0 10c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V10h2.54V7.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V10h2.773l-.443 2.89h-2.33v6.988C16.343 19.128 20 14.991 20 10z" clip-rule="evenodd"/>
                </svg>
            </a>
        </div>
    </div>
    '''

def generate_related_articles(current_article, related_list):
    """Generate related articles section given a prepared related list"""
    if not related_list:
        return ''

    cards = []
    for rel in related_list[:5]:
        slug = rel.get('slug')
        title = rel.get('title', 'Untitled')
        img = rel.get('thumbnailImageUrl') or rel.get('ogImage') or ''
        if img and not img.startswith('http'):
            img = img.replace('dist/', '../') if img.startswith('dist/') else f"../{img}"
        if not img:
            img = '../images/placeholder.webp'
        rel_url = f"../articles/{slug}.html"
        when = humanize_time_ago(rel.get('publishDate', ''))
        cards.append(f'''
            <a href="{rel_url}" class="block group">
                <div class="flex space-x-3">
                    <img src="{img}" alt="{rel.get('imageAltText', title)}" class="w-16 h-12 object-cover rounded flex-shrink-0" onerror="this.src='../images/placeholder.webp'">
                    <div class="flex-1">
                        <h4 class="text-sm font-semibold text-gray-900 group-hover:text-blue-600 line-clamp-2">{title}</h4>
                        <p class="text-xs text-gray-500 mt-1">{when}</p>
                    </div>
                </div>
            </a>
        ''')

    return f'''
    <div class="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Related Articles</h3>
        <div class="space-y-4">
            {''.join(cards)}
        </div>
    </div>
    '''

def compute_related_articles_map(articles):
    """Compute a map of slug -> list of related articles using lightweight scoring."""
    # Preprocess articles
    pre = []
    for a in articles:
        slug = a.get('slug')
        if not slug:
            continue
        pre.append({
            'slug': slug,
            'ref': a,
            'category': a.get('category', DEFAULT_CATEGORY) or DEFAULT_CATEGORY,
            'keywords': set([k.strip().lower() for k in (a.get('keywords') or []) if isinstance(k, str)]),
            'hashtags': set([h.strip('#').lower() for h in (a.get('socialMediaHashtags') or []) if isinstance(h, str)]),
            'title_words': extract_significant_words(a.get('title', '')),
            'ts': parse_date_to_ts(a.get('publishDate')),  # 0 if unknown
        })
    
    # Build map
    related = {}
    for i, A in enumerate(pre):
        scores = []
        for j, B in enumerate(pre):
            if i == j:
                continue
            s = 0.0
            # Category match
            if A['category'] == B['category']:
                s += 4.0
            # Shared keywords
            if A['keywords'] and B['keywords']:
                shared_k = A['keywords'] & B['keywords']
                if shared_k:
                    s += min(3.0 * len(shared_k), 9.0)
            # Shared hashtags
            if A['hashtags'] and B['hashtags']:
                shared_h = A['hashtags'] & B['hashtags']
                if shared_h:
                    s += min(1.0 * len(shared_h), 3.0)
            # Title word overlap
            if A['title_words'] and B['title_words']:
                shared_t = A['title_words'] & B['title_words']
                if shared_t:
                    s += min(1.5 * len(shared_t), 6.0)
            # Recency boost for B relative to A (prefer newer)
            if B['ts']:
                age_days = max(0, (now_ts() - B['ts']) / 86400)
                recency = max(0.0, 2.0 - (age_days / 30.0))  # up to +2 for within ~30 days
                s += recency
            if s > 0:
                scores.append((s, B))
        # Sort by score desc then by ts desc
        scores.sort(key=lambda x: (x[0], x[1]['ts']), reverse=True)
        top = [b['ref'] for (score, b) in scores[:8]]
        related[A['slug']] = top
    return related

def extract_significant_words(text):
    """Extract lowercased significant words from title (length>=4, not in stopwords)."""
    if not text:
        return set()
    stop = {
        'with','from','that','this','have','your','about','into','over','under','after','before','when','what','news',
        'the','and','for','are','but','not','you','was','were','has','had','his','her','its','they','them','our','out',
        'how','why','will','can','new','latest','updated','update'
    }
    words = re.findall(r"[a-zA-Z0-9']+", text.lower())
    return {w for w in words if len(w) >= 4 and w not in stop}

def parse_date_to_ts(date_str):
    """Parse various date string formats to epoch seconds. Return 0 if unknown."""
    if not date_str or not isinstance(date_str, str):
        return 0
    fmts = [
        '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%a, %d %b %Y %H:%M:%S', '%d %b %Y', '%B %d, %Y'
    ]
    for fmt in fmts:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except Exception:
            continue
    # Try ISO format fallback
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception:
        return 0

def now_ts():
    return int(datetime.now(tz=timezone.utc).timestamp())

def humanize_time_ago(date_str):
    ts = parse_date_to_ts(date_str)
    if not ts:
        return ''
    diff = max(0, now_ts() - ts)
    mins = diff // 60
    if mins < 60:
        return f"{int(mins)} min ago" if mins != 1 else "1 min ago"
    hours = mins // 60
    if hours < 24:
        return f"{int(hours)} hours ago" if hours != 1 else "1 hour ago"
    days = hours // 24
    if days < 30:
        return f"{int(days)} days ago" if days != 1 else "1 day ago"
    months = days // 30
    if months < 12:
        return f"{int(months)} months ago" if months != 1 else "1 month ago"
    years = months // 12
    return f"{int(years)} years ago" if years != 1 else "1 year ago"

def generate_article_structured_data(article):
    """Generate structured data for individual articles"""
    structured_data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": article['title'],
        "description": article.get('excerpt', ''),
        "datePublished": article.get('publishDate', ''),
        "dateModified": article.get('lastUpdated', article.get('publishDate', '')),
        "author": {
            "@type": "Person",
            "name": article.get('author', 'Editorial Team')
        },
        "publisher": {
            "@type": "Organization",
            "name": "Country's News",
            "logo": {
                "@type": "ImageObject",
                "url": "https://countrysnews.com/logo.svg"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://countrysnews.com/articles/{article['slug']}.html"
        }
    }
    
    # Add image if available (use absolute public URL when possible)
    def _local_to_public(p):
        if not p:
            return ''
        p = str(p)
        if p.startswith('http://') or p.startswith('https://'):
            return p
        if p.startswith('dist/'):
            return f"https://countrysnews.com/{p[len('dist/'):]}"
        if p.startswith('/'):
            return f"https://countrysnews.com{p}"
        return f"https://countrysnews.com/{p.lstrip('./')}"

    if article.get('thumbnailImageUrl'):
        img_pub = _local_to_public(article.get('thumbnailImageUrl'))
        if img_pub:
            structured_data["image"] = {
                "@type": "ImageObject",
                "url": img_pub
            }
    
    return f'<script type="application/ld+json">{json.dumps(structured_data, indent=2)}</script>'

def compare_articles_differential(current_articles, baseline_path):
    """Compare current articles with baseline to identify changes"""
    changes = {
        'changed': [],
        'new': [],
        'removed': [],
        'stats': {
            'total_current': len(current_articles),
            'total_baseline': 0
        }
    }
    
    # Load baseline if it exists
    baseline_articles = []
    if os.path.exists(baseline_path):
        try:
            with open(baseline_path, 'r', encoding='utf-8') as f:
                baseline_articles = json.load(f)
            print(f"📊 Loaded baseline with {len(baseline_articles)} articles from {baseline_path}")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"⚠️  Could not load baseline: {e}")
    else:
        print(f"📁 No baseline found at {baseline_path} - treating all articles as new")
    
    changes['stats']['total_baseline'] = len(baseline_articles)
    
    # Create lookup maps by id for efficient comparison
    current_map = {str(article.get('id', '')): article for article in current_articles if article.get('id')}
    baseline_map = {str(article.get('id', '')): article for article in baseline_articles if article.get('id')}
    
    # Find new articles (in current but not in baseline)
    for article_id, article in current_map.items():
        if article_id not in baseline_map:
            changes['new'].append(article)
            continue
        
        # Compare existing articles for changes
        baseline_article = baseline_map[article_id]
        
        # Check multiple fields for changes
        current_modified = article.get('dateModified', '')
        baseline_modified = baseline_article.get('dateModified', '')
        current_enhanced = article.get('enhancement_date', '')
        baseline_enhanced = baseline_article.get('enhancement_date', '')
        
        # Article is changed if any tracking field differs
        is_changed = (
            current_modified != baseline_modified or
            current_enhanced != baseline_enhanced or
            article.get('title', '') != baseline_article.get('title', '') or
            article.get('content', '') != baseline_article.get('content', '')
        )
        
        if is_changed:
            changes['changed'].append(article)
    
    # Find removed articles (in baseline but not in current)
    for article_id, article in baseline_map.items():
        if article_id not in current_map:
            changes['removed'].append(article)
    
    return changes

def save_articles_baseline(articles, baseline_path):
    """Save current articles as new baseline"""
    try:
        os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
        with open(baseline_path, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved new baseline with {len(articles)} articles to {baseline_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving baseline: {e}")
        return False

def update_sync_manifest_with_articles(articles_data, changes):
    """Update sync manifest with article metadata for intelligent sync decisions"""
    sync_manifest_path = os.path.join(OUTPUT_DIR, '.sync_manifest.json')
    differential_manifest_path = os.path.join(OUTPUT_DIR, '.differential_sync.json')
    
    # Load existing sync manifest if it exists
    sync_manifest = {}
    if os.path.exists(sync_manifest_path):
        try:
            with open(sync_manifest_path, 'r', encoding='utf-8') as f:
                sync_manifest = json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load sync manifest: {e}")
    
    # Create article metadata mapping
    article_metadata = {}
    for article in articles_data:
        if article.get('slug'):
            article_metadata[article['slug']] = {
                'id': article.get('id', ''),
                'dateModified': article.get('dateModified', ''),
                'enhancement_date': article.get('enhancement_date', ''),
                'publishDate': article.get('publishDate', ''),
                'title': article.get('title', ''),
                'category': article.get('category', DEFAULT_CATEGORY)
            }
    
    # Track files that need sync due to article changes
    files_to_sync = set()
    
    # Process changed and new articles
    changed_articles = changes.get('changed', []) + changes.get('new', [])
    for article in changed_articles:
        article_slug = article.get('slug')
        if not article_slug:
            continue
        
        # Mark article HTML file for sync
        article_file = f"articles/{article_slug}.html"
        files_to_sync.add(article_file)
        
        # Update sync manifest entry with article metadata
        if article_file in sync_manifest:
            # Enhance existing entry
            sync_manifest[article_file].update({
                'article_id': article.get('id', ''),
                'dateModified': article.get('dateModified', ''),
                'enhancement_date': article.get('enhancement_date', ''),
                'sync_reason': 'article_changed',
                'last_content_update': datetime.now(timezone.utc).isoformat()
            })
        
        # Mark category page for sync if needed
        category = article.get('category', DEFAULT_CATEGORY)
        if category:
            category_slug = generate_slug(category)
            category_file = f"categories/{category_slug}.html"
            files_to_sync.add(category_file)
    
    # Always mark critical pages for sync if any articles changed
    if changed_articles:
        critical_pages = ['index.html', 'sitemap.xml', 'rss.xml', 'robots.txt']
        for page in critical_pages:
            files_to_sync.add(page)
    
    # Update differential sync manifest
    differential_sync = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'article_changes': {
            'changed': len(changes.get('changed', [])),
            'new': len(changes.get('new', [])),
            'removed': len(changes.get('removed', []))
        },
        'files_to_sync': list(files_to_sync),
        'article_metadata': article_metadata,
        'sync_strategy': 'intelligent_article_driven'
    }
    
    # Save enhanced differential sync manifest
    try:
        with open(differential_manifest_path, 'w', encoding='utf-8') as f:
            json.dump(differential_sync, f, indent=2, ensure_ascii=False)
        print(f"📊 Updated differential sync manifest with {len(files_to_sync)} files to sync")
        return True
    except Exception as e:
        print(f"❌ Error updating differential sync manifest: {e}")
        return False

def get_intelligent_sync_decisions(article_changes=None):
    """Get intelligent sync decisions based on article and file changes"""
    sync_manifest_path = os.path.join(OUTPUT_DIR, '.sync_manifest.json')
    baseline_path = os.path.join(OUTPUT_DIR, '.last_processed_articles.json')
    
    decisions = {
        'sync_required': False,
        'files_to_sync': set(),
        'sync_reasons': [],
        'estimated_files': 0
    }
    
    # Check if we have article changes from differential generation
    if article_changes:
        changed_count = len(article_changes.get('changed', []))
        new_count = len(article_changes.get('new', []))
        
        if changed_count > 0 or new_count > 0:
            decisions['sync_required'] = True
            decisions['sync_reasons'].append(f"{changed_count} changed + {new_count} new articles")
            
            # Estimate files to sync
            # Each article = 1 HTML file, affected categories, plus critical pages
            affected_categories = set()
            for article in article_changes.get('changed', []) + article_changes.get('new', []):
                category = article.get('category', DEFAULT_CATEGORY)
                affected_categories.add(category)
            
            estimated = changed_count + new_count + len(affected_categories) + 4  # +4 for critical pages
            decisions['estimated_files'] = estimated
    
    # Check for file-level changes if no article changes detected
    if not decisions['sync_required']:
        if os.path.exists(sync_manifest_path):
            try:
                # Check file modification times
                current_time = time.time()
                manifest_mtime = os.path.getmtime(sync_manifest_path)
                
                # If manifest is very recent, assume sync might be needed
                if current_time - manifest_mtime < 300:  # Within 5 minutes
                    decisions['sync_required'] = True
                    decisions['sync_reasons'].append("Recent manifest update detected")
                    decisions['estimated_files'] = 10  # Conservative estimate
                    
            except Exception:
                pass
    
    return decisions

def generate_differential_site(articles_data, unique_categories, changes):
    """Generate site with differential processing"""
    print(f"🔄 Differential generation mode - processing {len(changes['changed'])} changed + {len(changes['new'])} new articles")
    
    # Always regenerate critical pages
    print("📝 Regenerating critical pages...")
    generate_advanced_homepage(articles_data, unique_categories)
    generate_sitemap(articles_data)
    generate_robots_txt()
    generate_rss_feed(articles_data)
    
    # Generate static pages (these rarely change)
    if not os.path.exists(os.path.join(OUTPUT_DIR, 'about', 'index.html')):
        generate_static_pages(unique_categories)
    
    # Process changed and new articles only
    articles_to_process = changes['changed'] + changes['new']
    if articles_to_process:
        print(f"📄 Processing {len(articles_to_process)} changed/new articles...")
        
        # Create articles directory
        articles_dir = os.path.join(OUTPUT_DIR, 'articles')
        os.makedirs(articles_dir, exist_ok=True)
        
        # Precompute related articles for all articles (needed for context)
        related_map = compute_related_articles_map(articles_data)
        
        for i, article in enumerate(articles_to_process):
            generate_single_advanced_article(article, unique_categories, related_map.get(article.get('slug', ''), []))
            if (i + 1) % 10 == 0:
                print(f"   ✅ Processed {i + 1}/{len(articles_to_process)} articles")
    
    # Regenerate category pages if we have changes
    if articles_to_process:
        # Check which categories are affected
        affected_categories = set()
        for article in articles_to_process:
            affected_categories.add(article.get('category', DEFAULT_CATEGORY))
        
        print(f"📂 Regenerating {len(affected_categories)} affected category pages...")
        for category in affected_categories:
            category_articles = [a for a in articles_data if a.get('category', DEFAULT_CATEGORY) == category]
            category_articles.sort(key=lambda x: x.get('publishDate', ''), reverse=True)
            generate_single_category_page(category, category_articles, unique_categories)
        
        # If homepage categories changed, regenerate all category pages
        if len(affected_categories) > 5:  # Many categories affected
            print("📂 Many categories affected - regenerating all category pages...")
            generate_advanced_category_pages(articles_data, unique_categories)
    
    # Update sync manifest with intelligent article metadata
    update_sync_manifest_with_articles(articles_data, changes)
    
    print(f"✅ Differential generation completed")

def generate_full_site(articles_data, unique_categories):
    """Generate complete site (full regeneration mode)"""
    print("🔄 Full regeneration mode - processing all articles and pages")
    
    # Generate all pages with advanced features
    generate_advanced_homepage(articles_data, unique_categories)
    generate_advanced_article_pages(articles_data, unique_categories)
    generate_advanced_category_pages(articles_data, unique_categories)
    generate_static_pages(unique_categories)
    generate_sitemap(articles_data)
    generate_robots_txt()
    generate_rss_feed(articles_data)
    
    # For full regeneration, mark all articles as "changed" for sync purposes
    full_changes = {
        'changed': articles_data,  # All articles considered changed
        'new': [],
        'removed': []
    }
    
    # Update sync manifest with all articles
    update_sync_manifest_with_articles(articles_data, full_changes)
    
    print("✅ Full site generation completed")

def generate_advanced_site_with_mode(enhance_articles=False, mode="differential"):
    """Generate advanced website with differential or full mode"""
    
    print("🚀 Generating Advanced E-E-A-T Compliant Website...")
    print("=" * 60)
    print(f"📊 Generation Mode: {mode.upper()}")
    
    # Optionally enhance articles first
    if enhance_articles:
        if not enhance_existing_articles():
            print("⚠️  Article enhancement failed, continuing with existing articles...")
        else:
            print("✅ Articles enhanced successfully!")
    
    # CRITICAL: Pre-flight validation checks
    if not perform_preflight_checks():
        print("❌ CRITICAL ERROR: Pre-flight checks failed. Aborting generation.")
        return False
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Ensure placeholder image exists
    ensure_placeholder_image()
    
    # Copy static assets
    copy_static_assets()
    
    # Load articles
    articles_data = load_articles()
    if not articles_data:
        print("❌ No articles found!")
        return False
    
    print(f"✅ Loaded {len(articles_data)} articles")
    
    # Get unique categories
    unique_categories = get_unique_categories(articles_data)
    print(f"✅ Found {len(unique_categories)} categories")
    
    # Define baseline path
    baseline_path = os.path.join(OUTPUT_DIR, '.last_processed_articles.json')
    
    if mode == "differential":
        # Compare with baseline to find changes
        changes = compare_articles_differential(articles_data, baseline_path)
        
        print(f"📊 Differential Analysis Results:")
        print(f"   • Changed articles: {len(changes['changed'])}")
        print(f"   • New articles: {len(changes['new'])}")
        print(f"   • Removed articles: {len(changes['removed'])}")
        print(f"   • Total current: {changes['stats']['total_current']}")
        print(f"   • Total baseline: {changes['stats']['total_baseline']}")
        
        if not changes['changed'] and not changes['new'] and not changes['removed']:
            print("✅ No changes detected - site is already up to date!")
            return True
        
        # Generate differentially
        generate_differential_site(articles_data, unique_categories, changes)
        
    elif mode == "full":
        print("🔄 Full regeneration requested - processing all content")
        generate_full_site(articles_data, unique_categories)
        
    else:
        print(f"❌ Unknown generation mode: {mode}")
        return False
    
    # Save new baseline after successful generation
    if not save_articles_baseline(articles_data, baseline_path):
        print("⚠️  Warning: Could not save baseline - next run will reprocess all articles")
    
    # CRITICAL: Validate sitemap to prevent Google Search Console errors
    sitemap_valid = validate_and_fix_sitemap()
    if not sitemap_valid:
        print("❌ CRITICAL ERROR: Sitemap validation failed!")
        print("🚨 THIS WILL CAUSE GOOGLE SEARCH CONSOLE ERRORS!")
        print("🚨 GENERATION CANNOT CONTINUE SAFELY!")
        return False
    
    # Final validation checks
    if not perform_final_validation():
        print("❌ CRITICAL ERROR: Final validation failed!")
        return False
    
    print("\n🎉 Advanced E-E-A-T Website Generation Complete!")
    print(f"📁 Website files generated in: {OUTPUT_DIR}/")
    print("🌟 Features included: Ads, Lazy Loading, Social Media, SEO, E-E-A-T Compliance!")
    if mode == "differential":
        print(f"⚡ Differential mode: Processed {len(changes.get('changed', []))} changed + {len(changes.get('new', []))} new articles")
    print("✅ All critical validations passed - safe for deployment!")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate advanced E-E-A-T compliant website')
    parser.add_argument('action', nargs='?', default='generate', choices=['generate', 'enhance'], 
                       help='Action to perform (default: generate)')
    parser.add_argument('target', nargs='?', default='site', choices=['site'], 
                       help='Generation target (default: site)')
    parser.add_argument('--differential', action='store_true', default=True,
                       help='Use differential generation (default)')
    parser.add_argument('--full', action='store_false', dest='differential',
                       help='Force full regeneration of all files')
    parser.add_argument('--enhance', action='store_true', default=False,
                       help='Enhance articles before generation')
    
    args = parser.parse_args()
    
    if args.action == "enhance":
        print("🚀 Starting Article Enhancement...")
        result = enhance_existing_articles()
        sys.exit(0 if result else 1)
    else:
        mode = "differential" if args.differential else "full"
        result = generate_advanced_site_with_mode(enhance_articles=args.enhance, mode=mode)
        sys.exit(0 if result else 1)
