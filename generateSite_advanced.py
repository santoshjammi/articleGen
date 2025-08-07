#!/usr/bin/env python3
"""
Advanced Site Generator with E-E-A-T Standards
Generates a comprehensive website with all advanced features including ads, lazy loading, 
social features, SEO optimization, and E-E-A-T compliance.
"""

import json
import os
import shutil
import re
from datetime import datetime
from urllib.parse import quote

OUTPUT_DIR = "dist"
ARTICLES_FILE = "perplexityArticles_eeat_enhanced.json"
DEFAULT_CATEGORY = "News"

def generate_advanced_site():
    """Generate advanced website with all features"""
    
    print("🚀 Generating Advanced E-E-A-T Compliant Website...")
    print("=" * 60)
    
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
    generate_robots_txt()
    generate_rss_feed(articles_data)
    
    print("\n🎉 Advanced E-E-A-T Website Generation Complete!")
    print(f"📁 Website files generated in: {OUTPUT_DIR}/")
    print("🌟 Features included: Ads, Lazy Loading, Social Media, SEO, E-E-A-T Compliance!")

def ensure_placeholder_image():
    """Ensure placeholder image exists"""
    placeholder_path = os.path.join('images', 'placeholder.jpg')
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
            
            # Save the image
            img.save(placeholder_path)
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
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Favicon and Logo -->
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
        }
        
        /* Article Content Styling */
        .article-content h1, .article-content h2, .article-content h3, 
        .article-content h4, .article-content h5, .article-content h6 {
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
            color: #1e3a8a;
        }
        .article-content h1 { font-size: 2.5em; }
        .article-content h2 { font-size: 2em; }
        .article-content h3 { font-size: 1.75em; }
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
        .ad-container {
            margin: 2rem 0;
            padding: 1rem;
            text-align: center;
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 0.75rem;
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
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
        
        .ad-placeholder {
            color: #9ca3af;
            font-size: 0.875rem;
            font-style: italic;
            text-align: center;
        }
        
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
    
    home_link = "index.html" if current_page_type == "home" else "../index.html"
    logo_path = "logo-header.svg" if current_page_type == "home" else "../logo-header.svg"
    
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
                                <a href="about-us.html" class="border-t border-blue-600">About Us</a>
                                <a href="contact.html">Contact</a>
                            </div>
                        </li>
                    </ul>
                </nav>
                
                <!-- Mobile Menu Button -->
                <button id="mobile-menu-btn" class="lg:hidden text-white hover:text-blue-200">
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
                {category_links.replace('<li><a', '<a').replace('</a></li>', '</a>').replace(' class="hover:text-blue-200 transition-colors px-2 py-1 rounded"', ' class="block py-2 hover:text-blue-200"')}
                <a href="about-us.html" class="block py-2 hover:text-blue-200">About Us</a>
                <a href="contact.html" class="block py-2 hover:text-blue-200">Contact</a>
            </div>
        </div>
    </header>
    
    <!-- Top Banner Ad -->
    <div class="ad-container banner">
        <div class="ad-placeholder">Advertisement - 728x90 Banner</div>
    </div>
    '''

def generate_footer_html(current_page_type="home"):
    """Generate advanced footer with social links and ads"""
    logo_path = "logo-header.svg" if current_page_type == "home" else "../logo-header.svg"
    rss_link = "rss.xml" if current_page_type == "home" else "../rss.xml"
    
    return f'''
    <!-- Footer Ad -->
    <div class="ad-container banner mt-12">
        <div class="ad-placeholder">Advertisement - 728x90 Footer Banner</div>
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
                    <h3 class="text-lg font-semibold mb-4 text-blue-400">Categories</h3>
                    <div class="space-y-2 text-sm">
                        <a href="categories/news.html" class="block hover:text-blue-400 transition-colors text-gray-400">News</a>
                        <a href="categories/business.html" class="block hover:text-blue-400 transition-colors text-gray-400">Business</a>
                        <a href="categories/technology.html" class="block hover:text-blue-400 transition-colors text-gray-400">Technology</a>
                        <a href="categories/sports.html" class="block hover:text-blue-400 transition-colors text-gray-400">Sports</a>
                    </div>
                </div>
                
                <!-- Quick Links -->
                <div class="text-center md:text-left">
                    <h3 class="text-lg font-semibold mb-4 text-blue-400">Quick Links</h3>
                    <div class="space-y-2 text-sm">
                        <a href="about-us.html" class="block hover:text-blue-400 transition-colors text-gray-400">About Us</a>
                        <a href="contact.html" class="block hover:text-blue-400 transition-colors text-gray-400">Contact</a>
                        <a href="privacy-policy.html" class="block hover:text-blue-400 transition-colors text-gray-400">Privacy Policy</a>
                        <a href="disclaimer.html" class="block hover:text-blue-400 transition-colors text-gray-400">Disclaimer</a>
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
        <div class="ad-placeholder">Mobile Ad - 320x50</div>
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
    
    # Get featured articles (top 6)
    featured_articles = sorted_articles[:6]
    
    # Get recent articles (next 12 for initial load)
    recent_articles = sorted_articles[6:18]
    
    # Get remaining articles for load more functionality
    remaining_articles = sorted_articles[18:]
    
    # Build article cards HTML
    featured_cards_html = ""
    for i, article in enumerate(featured_articles):
        featured_cards_html += generate_article_card(article, "home")
        # Add ad after every 2 articles
        if (i + 1) % 2 == 0 and i < len(featured_articles) - 1:
            featured_cards_html += '''
            <div class="col-span-full">
                <div class="ad-container">
                    <div class="ad-placeholder">Advertisement - 728x90 In-Content</div>
                </div>
            </div>
            '''
    
    recent_cards_html = ""
    for i, article in enumerate(recent_articles):
        recent_cards_html += generate_article_card(article, "home")
        # Add ad after every 3 articles
        if (i + 1) % 3 == 0 and i < len(recent_articles) - 1:
            recent_cards_html += '''
            <div class="col-span-full">
                <div class="ad-container">
                    <div class="ad-placeholder">Advertisement - 728x90 In-Content</div>
                </div>
            </div>
            '''
    
    # Generate structured data for E-E-A-T
    structured_data = generate_homepage_structured_data(articles_data)
    
    # Generate remaining articles JSON data for Load More functionality
    remaining_articles_json = json.dumps([{
        'title': article['title'],
        'slug': article['slug'],
        'author': article.get('author', 'Editorial Team'),
        'publishDate': article.get('publishDate', ''),
        'category': article.get('category', 'News'),
        'excerpt': article.get('excerpt', ''),
        'imageUrl': article.get('imageUrl', ''),
        'thumbnail': article.get('thumbnail', ''),
        'thumbnailImageUrl': article.get('thumbnailImageUrl', ''),
        'ogImage': article.get('ogImage', ''),
        'imageAltText': article.get('imageAltText', article['title']),
        'readingTimeMinutes': article.get('readingTimeMinutes', 5),
        'socialMediaHashtags': article.get('socialMediaHashtags', [])
    } for article in remaining_articles] if remaining_articles else [])
    
    homepage_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Country's News - Professional Journalism</title>
        <meta name="description" content="Country's News delivers comprehensive coverage and professional journalism with fact-checked content from authoritative reporters.">
        <meta name="keywords" content="news, professional journalism, fact-checked, current events, comprehensive coverage">
        
        <!-- E-E-A-T Meta Tags -->
        <meta name="author" content="Country's News Editorial Team">
        <meta name="publisher" content="Country's News">
        <meta name="copyright" content="© {datetime.now().year} Country's News">
        
        <!-- Open Graph -->
        <meta property="og:title" content="Country's News - Professional Journalism">
        <meta property="og:description" content="Country's News delivers comprehensive coverage and professional journalism with fact-checked content.">
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://countrynews.com/">
        <meta property="og:site_name" content="Country's News">
        
        <!-- Twitter Card -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="Country's News - Professional Journalism">
        <meta name="twitter:description" content="Professional journalism with comprehensive coverage and fact-checked content.">
        
        <!-- Canonical URL -->
        <link rel="canonical" href="https://countrynews.com/">
        
        {get_base_html_head()}
        
        <!-- Structured Data for E-E-A-T -->
        {structured_data}
    </head>
    <body>
        {generate_header_html(unique_categories, "home")}
        
        <main class="min-h-screen">
            <!-- Hero Section with Sidebar Ad -->
            <section class="container mx-auto px-4 py-8">
                <div class="flex flex-col lg:flex-row gap-8">
                    <div class="flex-1">
                        <div class="text-center mb-8">
                            <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-4">
                                Verified News & 
                                <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                                    Expert Analysis
                                </span>
                            </h1>
                        </div>
                        
                        <!-- Featured Articles -->
                        <section class="mb-12">
                            <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">Featured Stories</h2>
                            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                                {featured_cards_html}
                            </div>
                        </section>
                    </div>
                    
                    <!-- Sidebar with Ads -->
                    <aside class="lg:w-80 space-y-6">
                        <!-- Sidebar Ad 1 -->
                        <div class="ad-container sidebar">
                            <div class="ad-placeholder">Sidebar Ad - 300x250</div>
                        </div>
                        
                        <!-- Newsletter Signup -->
                        <div class="bg-gradient-to-br from-blue-50 to-indigo-100 p-6 rounded-xl border border-blue-200">
                            <h3 class="text-xl font-bold text-gray-900 mb-3">Stay Informed</h3>
                            <p class="text-gray-600 text-sm mb-4">Get verified news updates from our expert team.</p>
                            <div class="space-y-3">
                                <input type="email" placeholder="Your email address" 
                                       class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                                <button class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-2 px-4 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-medium">
                                    Subscribe Now
                                </button>
                            </div>
                        </div>
                        
                        <!-- Sidebar Ad 2 -->
                        <div class="ad-container sidebar">
                            <div class="ad-placeholder">Sidebar Ad - 300x250</div>
                        </div>
                        
                        <!-- Trending Categories -->
                        <div class="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
                            <h3 class="text-xl font-bold text-gray-900 mb-4">Trending Topics</h3>
                            <div class="space-y-3">
                                {generate_trending_categories_html(unique_categories[:6])}
                            </div>
                        </div>
                        
                        <!-- Sidebar Ad 3 -->
                        <div class="ad-container sidebar">
                            <div class="ad-placeholder">Sidebar Ad - 300x600 Skyscraper</div>
                        </div>
                    </aside>
                </div>
            </section>
            
            <!-- Recent Articles Section -->
            <section class="bg-gray-50 py-12">
                <div class="container mx-auto px-4">
                    <h2 class="text-3xl font-bold text-gray-900 mb-8 text-center">Latest News</h2>
                    <div id="recent-articles-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {recent_cards_html}
                    </div>
                    
                    <!-- Load More Button -->
                    <div class="text-center mt-12">
                        <button id="load-more-btn" class="load-more-btn">
                            Load More Articles
                        </button>
                    </div>
                </div>
            </section>
        </main>
        
        {generate_footer_html("home")}
        
        <!-- Homepage Load More JavaScript -->
        <script>
        // Homepage specific load more functionality
        (function() {{
            const remainingArticles = {remaining_articles_json};
            
            let currentPage = 0;
            const articlesPerPage = 6;
            const loadMoreBtn = document.getElementById('load-more-btn');
            const articlesGrid = document.getElementById('recent-articles-grid');
            
            function generateArticleCardHTML(article) {{
                // Remove 'dist/' prefix from thumbnailImageUrl if present
                let thumbnailUrl = article.thumbnailImageUrl || article.thumbnail || article.imageUrl || 'images/placeholder.jpg';
                if (thumbnailUrl.startsWith('dist/')) {{
                    thumbnailUrl = thumbnailUrl.substring(5); // Remove 'dist/' prefix
                }}
                const articleUrl = `articles/${{article.slug}}.html`;
                
                return `
                    <article class="article-card bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100">
                        <a href="${{articleUrl}}" class="block">
                            <div class="relative">
                                <img src="${{thumbnailUrl}}" 
                                     alt="${{article.imageAltText}}"
                                     class="w-full h-48 object-cover" 
                                     loading="lazy"
                                     onerror="this.src='images/placeholder.jpg'">
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
    
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(homepage_html)
    
    print(f"✅ Homepage generated with {len(featured_articles)} featured and {len(recent_articles)} recent articles")

def generate_trending_categories_html(categories):
    """Generate trending categories HTML"""
    html = ""
    for category in categories:
        category_slug = generate_slug(category)
        html += f'''
        <a href="categories/{category_slug}.html" 
           class="flex items-center justify-between p-3 bg-gray-50 hover:bg-blue-50 rounded-lg transition-colors group">
            <span class="font-medium text-gray-700 group-hover:text-blue-600">{category}</span>
            <svg class="w-4 h-4 text-gray-400 group-hover:text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path>
            </svg>
        </a>
        '''
    return html

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
                    "url": "https://countrynews.com/logo.svg"
                }
            }
        }
        articles_json.append(article_data)
    
    structured_data = {
        "@context": "https://schema.org",
        "@type": "NewsMediaOrganization",
        "name": "Country's News",
        "url": "https://countrynews.com/",
        "logo": "https://countrynews.com/logo.svg",
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
                    <div class="ad-placeholder">Category Page Advertisement - 728x90</div>
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
        <meta property="og:url" content="https://countrynews.com/categories/{category_slug}.html">
        <meta property="og:site_name" content="Country's News">
        
        <!-- Twitter Card -->
        <meta name="twitter:card" content="summary">
        <meta name="twitter:title" content="{category} News | Country's News">
        <meta name="twitter:description" content="Latest {category.lower()} news and expert analysis.">
        
        <!-- Canonical URL -->
        <link rel="canonical" href="https://countrynews.com/categories/{category_slug}.html">
        
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
                                    <div class="ad-placeholder">Category Sidebar Ad - 300x250</div>
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
                                    <div class="ad-placeholder">Category Sidebar Ad - 300x600</div>
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
                let thumbnailUrl = article.thumbnailImageUrl || article.thumbnail || article.imageUrl || '../images/placeholder.jpg';
                if (thumbnailUrl.startsWith('dist/')) {{
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
                                     onerror="this.src='../images/placeholder.jpg'">
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
        "url": f"https://countrynews.com/categories/{generate_slug(category)}.html",
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
    """Generate About Us page"""
    about_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>About Us | Country's News</title>
        <meta name="description" content="Learn about Country's News - your trusted source for verified journalism, expert analysis, and fact-checked content.">
        
        {get_base_html_head()}
    </head>
    <body>
        {generate_header_html(unique_categories, "home")}
        
        <main class="min-h-screen py-12">
            <div class="container mx-auto px-4 max-w-4xl">
                <h1 class="text-4xl font-bold text-gray-900 mb-8 text-center">About Country's News</h1>
                
                <div class="prose prose-lg max-w-none">
                    <p class="text-xl text-gray-600 mb-8 text-center">
                        Your trusted source for verified journalism, expert analysis, and comprehensive news coverage.
                    </p>
                    
                    <div class="grid md:grid-cols-3 gap-8 mb-12">
                        <div class="text-center">
                            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg class="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                                </svg>
                            </div>
                            <h3 class="text-xl font-bold mb-2">Verified Content</h3>
                            <p class="text-gray-600">All our articles are fact-checked by expert journalists.</p>
                        </div>
                        
                        <div class="text-center">
                            <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg class="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path>
                                </svg>
                            </div>
                            <h3 class="text-xl font-bold mb-2">Expert Authors</h3>
                            <p class="text-gray-600">Our team consists of experienced journalists and industry experts.</p>
                        </div>
                        
                        <div class="text-center">
                            <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                <svg class="w-8 h-8 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                                    <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                                </svg>
                            </div>
                            <h3 class="text-xl font-bold mb-2">Trusted Sources</h3>
                            <p class="text-gray-600">We maintain the highest standards of journalistic integrity.</p>
                        </div>
                    </div>
                    
                    <h2>Our Mission</h2>
                    <p>
                        At Country's News, we are committed to delivering accurate, timely, and comprehensive news coverage 
                        that helps our readers stay informed about the world around them. Our mission is to provide 
                        verified journalism that meets the highest standards of accuracy, expertise, authoritativeness, 
                        and trustworthiness.
                    </p>
                    
                    <h2>Our Team</h2>
                    <p>
                        Our editorial team comprises seasoned journalists, subject matter experts, and fact-checkers 
                        who work tirelessly to ensure every story meets our rigorous standards. We believe in 
                        transparent reporting and maintaining the trust our readers place in us.
                    </p>
                </div>
                
                <!-- Ad -->
                <div class="ad-container my-12">
                    <div class="ad-placeholder">About Page Advertisement - 728x90</div>
                </div>
            </div>
        </main>
        
        {generate_footer_html("home")}
    </body>
    </html>
    '''
    
    with open(os.path.join(OUTPUT_DIR, 'about-us.html'), 'w', encoding='utf-8') as f:
        f.write(about_html)

def generate_contact_page(unique_categories):
    """Generate Contact page with form"""
    contact_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Contact Us | Country's News</title>
        <meta name="description" content="Get in touch with Country's News. We value your feedback and are here to help.">
        
        {get_base_html_head()}
    </head>
    <body>
        {generate_header_html(unique_categories, "home")}
        
        <main class="min-h-screen py-12">
            <div class="container mx-auto px-4 max-w-4xl">
                <h1 class="text-4xl font-bold text-gray-900 mb-8 text-center">Contact Us</h1>
                
                <div class="grid md:grid-cols-2 gap-12">
                    <!-- Contact Form -->
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-6">Send us a message</h2>
                        <form class="space-y-6">
                            <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Name</label>
                                <input type="text" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                            </div>
                            <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Email</label>
                                <input type="email" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                            </div>
                            <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Subject</label>
                                <input type="text" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                            </div>
                            <div>
                                <label class="block text-sm font-semibold text-gray-700 mb-2">Message</label>
                                <textarea rows="6" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"></textarea>
                            </div>
                            <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-lg hover:from-blue-700 hover:to-blue-800 transition-all font-semibold">
                                Send Message
                            </button>
                        </form>
                    </div>
                    
                    <!-- Contact Info -->
                    <div>
                        <h2 class="text-2xl font-bold text-gray-900 mb-6">Get in touch</h2>
                        <div class="space-y-6">
                            <div class="flex items-start space-x-4">
                                <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                    <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path>
                                        <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path>
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold text-gray-900">Email</h3>
                                    <p class="text-gray-600">contact@countrynews.com</p>
                                </div>
                            </div>
                            
                            <div class="flex items-start space-x-4">
                                <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                    <svg class="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"></path>
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold text-gray-900">Phone</h3>
                                    <p class="text-gray-600">+1 (555) 123-4567</p>
                                </div>
                            </div>
                            
                            <div class="flex items-start space-x-4">
                                <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                                    <svg class="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clip-rule="evenodd"></path>
                                    </svg>
                                </div>
                                <div>
                                    <h3 class="text-lg font-semibold text-gray-900">Address</h3>
                                    <p class="text-gray-600">123 News Street<br>Media City, MC 12345</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Ad -->
                        <div class="ad-container sidebar mt-8">
                            <div class="ad-placeholder">Contact Sidebar Ad - 300x250</div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
        
        {generate_footer_html("home")}
    </body>
    </html>
    '''
    
    with open(os.path.join(OUTPUT_DIR, 'contact.html'), 'w', encoding='utf-8') as f:
        f.write(contact_html)

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
                    <p>If you have any questions about this Privacy Policy, please contact us at privacy@countrynews.com.</p>
                </div>
                
                <!-- Ad -->
                <div class="ad-container my-12">
                    <div class="ad-placeholder">Privacy Policy Ad - 728x90</div>
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
                    <div class="ad-placeholder">Disclaimer Ad - 728x90</div>
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
    """Generate XML sitemap"""
    print("📝 Generating XML sitemap...")
    
    sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <!-- Homepage -->
    <url>
        <loc>https://countrynews.com/</loc>
        <changefreq>hourly</changefreq>
        <priority>1.0</priority>
    </url>
    
    <!-- Static Pages -->
    <url>
        <loc>https://countrynews.com/about-us.html</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>https://countrynews.com/contact.html</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    
'''
    
    # Add category pages
    categories = set([article.get('category', DEFAULT_CATEGORY) for article in articles_data])
    for category in categories:
        category_slug = generate_slug(category)
        sitemap_content += f'''    <url>
        <loc>https://countrynews.com/categories/{category_slug}.html</loc>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
'''
    
    # Add article pages
    for article in articles_data:
        sitemap_content += f'''    <url>
        <loc>https://countrynews.com/articles/{article['slug']}.html</loc>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>
'''
    
    sitemap_content += '</urlset>'
    
    with open(os.path.join(OUTPUT_DIR, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    
    print("✅ XML sitemap generated")

def generate_robots_txt():
    """Generate robots.txt"""
    robots_content = '''User-agent: *
Allow: /

Sitemap: https://countrynews.com/sitemap.xml
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
        <link>https://countrynews.com/</link>
        <language>en-us</language>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S')} GMT</lastBuildDate>
        
'''
    
    for article in sorted_articles:
        rss_content += f'''        <item>
            <title><![CDATA[{article['title']}]]></title>
            <description><![CDATA[{article.get('excerpt', '')[:500]}]]></description>
            <link>https://countrynews.com/articles/{article['slug']}.html</link>
            <guid>https://countrynews.com/articles/{article['slug']}.html</guid>
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
    
    for i, article in enumerate(articles_data):
        generate_single_advanced_article(article, unique_categories)
        if (i + 1) % 20 == 0:
            print(f"   ✅ Generated {i + 1}/{len(articles_data)} articles")
    
    print(f"✅ All {len(articles_data)} advanced article pages generated")

def generate_single_advanced_article(article, unique_categories):
    """Generate single advanced article page"""
    
    # Generate author profile HTML
    author_profile_html = generate_author_profile(article)
    
    # Generate related articles
    related_articles_html = generate_related_articles(article)
    
    # Generate social sharing
    social_sharing_html = generate_social_sharing(article)
    
    # Generate structured data for article
    structured_data = generate_article_structured_data(article)
    
    # Get article image
    article_image = article.get('thumbnailImageUrl', '')
    if article_image and article_image.startswith('dist/'):
        article_image = article_image.replace('dist/', '../')
    
    # Generate social hashtags
    hashtags_html = ""
    social_hashtags = article.get('socialMediaHashtags', [])
    if social_hashtags:
        hashtags_html = f'''
        <div class="hashtags">
            <h3 class="text-sm font-semibold text-gray-500 mb-2">TRENDING TOPICS</h3>
            <div class="flex flex-wrap gap-2">
                {' '.join([f'<a href="#" class="hashtag">#{tag}</a>' for tag in social_hashtags[:8]])}
            </div>
        </div>
        '''
    
    article_html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>{article['title']} | Country's News</title>
        <meta name="description" content="{article.get('excerpt', '')[:160]}">
        <meta name="keywords" content="{', '.join(article.get('keywords', []))}">
        
        <!-- E-E-A-T Meta Tags -->
        <meta name="author" content="{article.get('author', 'Editorial Team')}">
        <meta name="publisher" content="Country's News">
        <meta name="article:published_time" content="{article.get('publishDate', '')}">
        <meta name="article:modified_time" content="{article.get('lastUpdated', article.get('publishDate', ''))}">
        <meta name="article:section" content="{article.get('category', 'News')}">
        
        <!-- Open Graph -->
        <meta property="og:title" content="{article['title']}">
        <meta property="og:description" content="{article.get('excerpt', '')[:160]}">
        <meta property="og:type" content="article">
        <meta property="og:url" content="https://countrynews.com/articles/{article['slug']}.html">
        <meta property="og:image" content="{article_image}">
        <meta property="og:site_name" content="Country's News">
        
        <!-- Twitter Card -->
        <meta name="twitter:card" content="summary_large_image">
        <meta name="twitter:title" content="{article['title']}">
        <meta name="twitter:description" content="{article.get('excerpt', '')[:160]}">
        <meta name="twitter:image" content="{article_image}">
        
        <!-- Canonical URL -->
        <link rel="canonical" href="https://countrynews.com/articles/{article['slug']}.html">
        
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
                        <!-- Article Body -->
                        <div class="article-content prose prose-lg max-w-none">
                            {article.get('content', article.get('body', ''))}
                        </div>
                        
                        <!-- In-Content Ad -->
                        <div class="ad-container my-8">
                            <div class="ad-placeholder">In-Content Advertisement - 728x90</div>
                        </div>
                        
                        <!-- Social Hashtags -->
                        {hashtags_html}
                        
                        <!-- Author Profile -->
                        {author_profile_html}
                        
                        <!-- Second In-Content Ad -->
                        <div class="ad-container my-8">
                            <div class="ad-placeholder">In-Content Advertisement - 728x90</div>
                        </div>
                    </div>
                    
                    <!-- Sidebar -->
                    <aside class="lg:w-1/3">
                        <!-- Sticky Sidebar -->
                        <div class="sticky top-24 space-y-6">
                            <!-- Sidebar Ad -->
                            <div class="ad-container sidebar">
                                <div class="ad-placeholder">Sidebar Ad - 300x250</div>
                            </div>
                            
                            <!-- Table of Contents (if headings exist) -->
                            <div class="bg-blue-50 p-6 rounded-xl border border-blue-200">
                                <h3 class="text-lg font-bold text-gray-900 mb-4">In This Article</h3>
                                <nav class="space-y-2 text-sm">
                                    <a href="#introduction" class="block text-blue-600 hover:text-blue-800">Introduction</a>
                                    <a href="#main-content" class="block text-blue-600 hover:text-blue-800">Key Points</a>
                                    <a href="#conclusion" class="block text-blue-600 hover:text-blue-800">Conclusion</a>
                                </nav>
                            </div>
                            
                            <!-- Related Articles -->
                            {related_articles_html}
                            
                            <!-- Another Sidebar Ad -->
                            <div class="ad-container sidebar">
                                <div class="ad-placeholder">Sidebar Ad - 300x600</div>
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
    """Generate author profile section"""
    author_name = article.get('author', 'Editorial Team')
    author_profile = article.get('authorProfile', {})
    
    return f'''
    <div class="author-profile">
        <div class="flex items-start space-x-4">
            <img src="../images/author-placeholder.svg" 
                 alt="{author_name}" 
                 class="w-16 h-16 rounded-full bg-blue-100 p-2"
                 onerror="this.style.display='none'">
            <div class="flex-1">
                <h3 class="text-xl font-bold text-gray-900 mb-2">About {author_name}</h3>
                <p class="text-gray-600 text-sm mb-3">
                    {author_profile.get('bio', f'{author_name} is an experienced journalist and expert analyst at Country\'s News, specializing in comprehensive news coverage with a focus on accuracy and reliability.')}
                </p>
            </div>
        </div>
    </div>
    '''

def generate_social_sharing(article):
    """Generate social sharing buttons"""
    article_url = f"https://countrynews.com/articles/{article['slug']}.html"
    article_title = quote(article['title'])
    
    return f'''
    <div class="flex items-center gap-4 py-4 border-y border-gray-200 mb-8">
        <span class="text-sm font-semibold text-gray-700">Share:</span>
        <div class="flex gap-2">
            <a href="https://twitter.com/intent/tweet?text={article_title}&url={article_url}" 
               target="_blank" 
               class="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-lg transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84"/>
                </svg>
            </a>
            <a href="https://www.facebook.com/sharer/sharer.php?u={article_url}" 
               target="_blank"
               class="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-lg transition-colors">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M20 10c0-5.523-4.477-10-10-10S0 4.477 0 10c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V10h2.54V7.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V10h2.773l-.443 2.89h-2.33v6.988C16.343 19.128 20 14.991 20 10z" clip-rule="evenodd"/>
                </svg>
            </a>
        </div>
    </div>
    '''

def generate_related_articles(article):
    """Generate related articles section"""
    return '''
    <div class="bg-white p-6 rounded-xl shadow-lg border border-gray-100">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Related Articles</h3>
        <div class="space-y-4">
            <a href="#" class="block group">
                <div class="flex space-x-3">
                    <div class="w-16 h-12 bg-gray-200 rounded flex-shrink-0"></div>
                    <div class="flex-1">
                        <h4 class="text-sm font-semibold text-gray-900 group-hover:text-blue-600 line-clamp-2">
                            Related Article Title Here
                        </h4>
                        <p class="text-xs text-gray-500 mt-1">2 hours ago</p>
                    </div>
                </div>
            </a>
        </div>
    </div>
    '''

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
                "url": "https://countrynews.com/logo.svg"
            }
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://countrynews.com/articles/{article['slug']}.html"
        }
    }
    
    # Add image if available
    if article.get('thumbnailImageUrl'):
        structured_data["image"] = {
            "@type": "ImageObject",
            "url": article['thumbnailImageUrl']
        }
    
    return f'<script type="application/ld+json">{json.dumps(structured_data, indent=2)}</script>'

if __name__ == "__main__":
    generate_advanced_site()
