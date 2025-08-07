#!/usr/bin/env python3
"""
Clean Site Generator
Generates a simple, clean website focused on displaying articles properly with thumbnails and categories.
"""

import json
import os
import shutil
from datetime import datetime
from urllib.parse import quote

OUTPUT_DIR = "dist"
ARTICLES_FILE = "perplexityArticles_eeat_enhanced.json"  # Using enhanced articles but without E-E-A-T display

def generate_clean_site():
    """Generate clean website focused on article display"""
    
    print("🌟 Generating Clean Article Website...")
    print("=" * 50)
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Copy static assets
    copy_static_assets()
    
    # Load articles
    articles_data = load_articles()
    if not articles_data:
        print("❌ No articles found!")
        return
    
    print(f"✅ Loaded {len(articles_data)} articles")
    
    # Generate all pages
    generate_homepage(articles_data)
    generate_article_pages(articles_data)
    generate_category_pages(articles_data)
    generate_static_pages()
    generate_sitemap(articles_data)
    generate_robots_txt()
    generate_rss_feed(articles_data)
    
    print("\n🎉 Clean Site Generation Complete!")
    print(f"📁 Website files generated in: {OUTPUT_DIR}/")

def copy_static_assets():
    """Copy logos and images"""
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
    """Load articles"""
    try:
        with open(ARTICLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Try regular articles file as fallback
        try:
            with open('perplexityArticles.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ No articles file found")
            return []
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing articles: {e}")
        return []

def generate_homepage(articles_data):
    """Generate clean homepage with properly displayed articles"""
    
    # Get recent articles for homepage
    recent_articles = sorted(articles_data, 
                           key=lambda x: x.get('publishDate', ''), 
                           reverse=True)[:12]
    
    # Generate clean article cards
    articles_html = ""
    for article in recent_articles:
        # Get proper thumbnail URL
        thumbnail_url = article.get('thumbnailImageUrl', '')
        if not thumbnail_url:
            thumbnail_url = article.get('ogImage', '')
        
        # Clean the URL path for proper display
        if thumbnail_url.startswith('dist/'):
            thumbnail_url = thumbnail_url.replace('dist/', '')
        
        article_card = f'''
        <article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
            <a href="articles/{article['slug']}.html" class="block">
                <img src="{thumbnail_url}" 
                     alt="{article.get('imageAltText', article['title'])}" 
                     class="w-full h-48 object-cover"
                     onerror="this.style.display='none'">
                <div class="p-6">
                    <div class="mb-3">
                        <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                            {article.get('category', 'News')}
                        </span>
                    </div>
                    
                    <h2 class="text-xl font-bold text-blue-800 mb-2 hover:text-blue-600 transition-colors">
                        {article['title'][:80]}{"..." if len(article['title']) > 80 else ""}
                    </h2>
                    <p class="text-gray-600 text-sm mb-4">
                        {article.get('excerpt', '')[:150]}{"..." if len(article.get('excerpt', '')) > 150 else ""}
                    </p>
                    
                    <div class="flex items-center justify-between text-sm text-gray-500">
                        <span>By {article.get('author', 'Editor')}</span>
                        <span>{article.get('publishDate', '')}</span>
                    </div>
                    <div class="text-xs text-gray-400 mt-1">
                        {article.get('readingTimeMinutes', 5)} min read
                    </div>
                </div>
            </a>
        </article>
        '''
        articles_html += article_card
    
    # Get main categories for navigation (limit to most popular)
    category_counts = {}
    for article in articles_data:
        category = article.get('category', 'News')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    # Sort by count and get top 5 categories
    top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    category_nav = ""
    for category, count in top_categories:
        category_slug = category.lower().replace(' ', '-')
        category_nav += f'<a href="categories/{category_slug}.html" class="text-gray-700 hover:text-blue-600">{category}</a>'
    
    homepage_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Country's News - Latest Articles & Analysis</title>
    <meta name="description" content="Stay updated with the latest news, analysis, and insights across various categories.">
    
    <link rel="canonical" href="https://countrysnews.com/">
    <link rel="icon" href="favicon.svg" type="image/svg+xml">
    
    <!-- Open Graph -->
    <meta property="og:title" content="Country's News - Latest Articles & Analysis">
    <meta property="og:description" content="Stay updated with the latest news and insights">
    <meta property="og:url" content="https://countrysnews.com/">
    <meta property="og:type" content="website">
    <meta property="og:image" content="https://countrysnews.com/logo.svg">
    
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-md sticky top-0 z-50">
        <div class="container mx-auto px-4">
            <div class="flex items-center justify-between py-4">
                <div class="flex items-center space-x-4">
                    <img src="logo-header.svg" alt="Country's News" class="h-10">
                    <span class="text-2xl font-bold text-blue-800">Country's News</span>
                </div>
                
                <!-- Desktop Navigation -->
                <div class="hidden md:flex items-center space-x-8">
                    <a href="index.html" class="text-gray-700 hover:text-blue-600 font-medium">Home</a>
                    
                    <!-- Categories Dropdown -->
                    <div class="relative group">
                        <button class="text-gray-700 hover:text-blue-600 flex items-center space-x-1">
                            <span>Categories</span>
                            <svg class="w-4 h-4 transform group-hover:rotate-180 transition-transform" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                            </svg>
                        </button>
                        
                        <!-- Dropdown Menu -->
                        <div class="absolute left-0 mt-2 w-64 bg-white rounded-md shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                            <div class="py-2 grid grid-cols-2 gap-1">
                                <!-- All categories dropdown links will be inserted here -->
                            </div>
                        </div>
                    </div>
                    
                    <!-- Top Categories -->
                    {category_nav}
                    
                    <a href="about-us.html" class="text-gray-700 hover:text-blue-600">About</a>
                </div>
                
                <!-- Mobile Menu Button -->
                <div class="md:hidden">
                    <button id="mobile-menu-btn" class="text-gray-700 hover:text-blue-600 focus:outline-none">
                        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                            <path fill-rule="evenodd" d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clip-rule="evenodd"></path>
                        </svg>
                    </button>
                </div>
            </div>
            
            <!-- Mobile Menu -->
            <div id="mobile-menu" class="md:hidden hidden border-t border-gray-200 py-4">
                <div class="flex flex-col space-y-3">
                    <a href="index.html" class="text-gray-700 hover:text-blue-600 font-medium">Home</a>
                    
                    <!-- Mobile Categories -->
                    <div class="border-l-2 border-blue-200 pl-4">
                        <div class="text-sm font-semibold text-gray-900 mb-2">Top Categories</div>
                        <div class="flex flex-col space-y-2">
                            {category_nav.replace('<a', '<a class="text-sm"').replace('text-gray-700', 'text-gray-600')}
                        </div>
                        <div class="mt-3">
                            <a href="#all-categories" class="text-sm text-blue-600 hover:text-blue-800">View all categories ↓</a>
                        </div>
                    </div>
                    
                    <a href="about-us.html" class="text-gray-700 hover:text-blue-600">About</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Hero Section -->
        <section class="text-center mb-12">
            <h1 class="text-4xl font-bold text-blue-800 mb-4">Latest News & Analysis</h1>
            <p class="text-xl text-gray-600 mb-8">Stay informed with our comprehensive coverage across multiple categories</p>
        </section>

        <!-- Category Overview -->
        <section class="mb-12" id="all-categories">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Browse by Category</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4" id="category-cards">
                <!-- Category cards will be inserted here -->
            </div>
        </section>

        <!-- Featured Articles -->
        <section>
            <div class="flex items-center justify-between mb-8">
                <h2 class="text-3xl font-bold text-gray-900">Recent Articles</h2>
                <div class="text-sm text-gray-600">
                    Updated: {datetime.now().strftime('%B %d, %Y')}
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {articles_html}
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-16">
        <div class="container mx-auto px-4 text-center">
            <div class="mb-4">
                <h3 class="text-lg font-semibold mb-2">Country's News</h3>
                <p class="text-gray-300 text-sm">Your source for comprehensive news and analysis</p>
            </div>
            <div class="border-t border-gray-700 pt-4">
                <p class="text-gray-300 text-sm">&copy; {datetime.now().year} Country's News. All rights reserved.</p>
            </div>
        </div>
    </footer>
    
    <!-- Mobile Menu JavaScript -->
    <script>
        document.getElementById('mobile-menu-btn').addEventListener('click', function() {{
            const mobileMenu = document.getElementById('mobile-menu');
            mobileMenu.classList.toggle('hidden');
        }});
    </script>
</body>
</html>'''

    # Generate all category links for dropdown
    all_category_links = ""
    all_categories = set()
    for article in articles_data:
        all_categories.add(article.get('category', 'News'))
    
    for category in sorted(all_categories):
        category_slug = category.lower().replace(' ', '-')
        all_category_links += f'''
                                <a href="categories/{category_slug}.html" class="block px-3 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded">
                                    {category}
                                </a>'''
    
    # Replace the placeholder in homepage_html
    homepage_html = homepage_html.replace('<!-- All categories dropdown links will be inserted here -->', all_category_links)

    # Generate category cards HTML
    category_cards_html = ""
    category_counts = {}
    category_counts = {}
    for article in articles_data:
        category = article.get('category', 'News')
        category_counts[category] = category_counts.get(category, 0) + 1
    
    for category, count in sorted(category_counts.items()):
        category_slug = category.lower().replace(' ', '-')
        category_cards_html += f'''
        <a href="categories/{category_slug}.html" class="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow text-center">
            <h3 class="font-semibold text-blue-800 mb-1">{category}</h3>
            <p class="text-sm text-gray-600">{count} articles</p>
        </a>
        '''
    
    # Replace the placeholder in homepage_html
    homepage_html = homepage_html.replace('<!-- Category cards will be inserted here -->', category_cards_html)

    # Write homepage
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(homepage_html)
    print("✅ Generated clean homepage")

def generate_article_pages(articles_data):
    """Generate individual article pages"""
    
    os.makedirs(os.path.join(OUTPUT_DIR, 'articles'), exist_ok=True)
    
    for article in articles_data:
        # Get proper image URL
        image_url = article.get('ogImage', '')
        if image_url.startswith('dist/'):
            image_url = image_url.replace('dist/', '../')
        elif image_url and not image_url.startswith('http'):
            image_url = f"../{image_url}"
        
        # Generate social hashtags if available
        social_hashtags = article.get('socialMediaHashtags', [])
        social_hashtags_html = ""
        if social_hashtags:
            hashtags_list = " ".join([f"#{tag}" for tag in social_hashtags[:8]])
            social_hashtags_html = f'''
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p class="text-sm text-gray-700">
                    <strong>Social Tags:</strong> 
                    <span class="text-blue-600">{hashtags_list}</span>
                </p>
            </div>'''
        
        # Generate key takeaways if available
        key_takeaways = article.get('keyTakeaways', [])
        key_takeaways_html = ""
        if key_takeaways:
            takeaways_list = ""
            for takeaway in key_takeaways:
                takeaways_list += f"<li class='mb-2 text-gray-700'>{takeaway}</li>"
            key_takeaways_html = f'''
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-6 my-8 rounded-r">
                <h3 class="text-lg font-semibold text-yellow-900 mb-3">📝 Key Points</h3>
                <ul class="list-disc list-inside space-y-1">
                    {takeaways_list}
                </ul>
            </div>'''
        
        article_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']}</title>
    <meta name="description" content="{article.get('metaDescription', article.get('excerpt', ''))}">
    
    <link rel="canonical" href="https://countrysnews.com/articles/{article['slug']}.html">
    <link rel="icon" href="../favicon.svg" type="image/svg+xml">
    
    <!-- Open Graph -->
    <meta property="og:title" content="{article['title']}">
    <meta property="og:description" content="{article.get('metaDescription', article.get('excerpt', ''))}">
    <meta property="og:url" content="https://countrysnews.com/articles/{article['slug']}.html">
    <meta property="og:type" content="article">
    <meta property="og:image" content="{article.get('ogImage', '')}">
    
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
                    <a href="../categories/{article.get('category', 'news').lower().replace(' ', '-')}.html" class="text-gray-700 hover:text-blue-600">{article.get('category', 'News')}</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Article Content -->
    <main class="container mx-auto px-4 py-8 max-w-4xl">
        <article class="bg-white rounded-lg shadow-lg overflow-hidden">
            <!-- Article Header -->
            <div class="p-8">
                <div class="mb-4">
                    <a href="../categories/{article.get('category', 'news').lower().replace(' ', '-')}.html" 
                       class="bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full hover:bg-blue-200">
                        {article.get('category', 'News')}
                    </a>
                </div>
                
                <h1 class="text-4xl font-extrabold text-blue-800 mb-6">{article['title']}</h1>
                
                <!-- Article Meta -->
                <div class="text-gray-600 text-sm mb-6 pb-4 border-b border-gray-200">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-4">
                            <span class="font-medium">By {article.get('author', 'Editor')}</span>
                            <span>{article.get('publishDate', '')}</span>
                        </div>
                        <div class="text-right">
                            <span class="text-gray-500">{article.get('readingTimeMinutes', 5)} min read</span>
                        </div>
                    </div>
                </div>
                
                <!-- Social Media Hashtags -->
                {social_hashtags_html}
                
                <!-- Main image -->
                {f'<img src="{image_url}" alt="{article.get("imageAltText", article["title"])}" class="w-full h-64 object-cover rounded-lg mb-8 shadow-md">' if image_url else ''}
                
                <!-- Article content -->
                <div class="prose prose-lg max-w-none text-gray-800">
                    {article['content']}
                </div>
                
                <!-- Key Takeaways -->
                {key_takeaways_html}
                
                <!-- Call to Action -->
                <div class="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-lg text-center my-8">
                    <h3 class="text-xl font-semibold mb-2">Explore More Articles</h3>
                    <p class="mb-4">Stay informed with our latest news and analysis</p>
                    <a href="../index.html" class="bg-white text-blue-600 px-6 py-2 rounded-full font-semibold hover:bg-gray-100 transition-colors">
                        Back to Home
                    </a>
                </div>
            </div>
        </article>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white py-8 mt-16">
        <div class="container mx-auto px-4 text-center">
            <p class="text-gray-300">&copy; {datetime.now().year} Country's News. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>'''

        # Write article file
        article_filename = f"{article['slug']}.html"
        with open(os.path.join(OUTPUT_DIR, 'articles', article_filename), 'w', encoding='utf-8') as f:
            f.write(article_html)
    
    print(f"✅ Generated {len(articles_data)} clean article pages")

def generate_category_pages(articles_data):
    """Generate category pages"""
    
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
            # Get proper thumbnail
            thumbnail_url = article.get('thumbnailImageUrl', '')
            if not thumbnail_url:
                thumbnail_url = article.get('ogImage', '')
            if thumbnail_url.startswith('dist/'):
                thumbnail_url = thumbnail_url.replace('dist/', '../')
            
            articles_html += f'''
            <article class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <a href="../articles/{article['slug']}.html" class="block">
                    {f'<img src="{thumbnail_url}" alt="{article.get("imageAltText", article["title"])}" class="w-full h-48 object-cover" onerror="this.style.display=\'none\'">' if thumbnail_url else ''}
                    <div class="p-6">
                        <h3 class="text-xl font-bold text-blue-800 mb-2 hover:text-blue-600">
                            {article['title']}
                        </h3>
                        <p class="text-gray-600 mb-3">{article.get('excerpt', '')[:150]}...</p>
                        <div class="flex items-center justify-between text-sm text-gray-500">
                            <span>By {article.get('author', 'Editor')}</span>
                            <span>{article.get('publishDate', '')}</span>
                        </div>
                    </div>
                </a>
            </article>
            '''
        
        category_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category} - Country's News</title>
    <meta name="description" content="Browse all {category.lower()} articles on Country's News.">
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
                </div>
            </div>
        </div>
    </nav>

    <main class="container mx-auto px-4 py-8">
        <div class="mb-8">
            <h1 class="text-4xl font-bold text-blue-800 mb-4">{category}</h1>
            <p class="text-gray-600">Browse all {category.lower()} articles</p>
            <div class="flex items-center mt-2 text-sm text-gray-500">
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
    
    print(f"✅ Generated {len(categories)} clean category pages")

def generate_static_pages():
    """Generate about page"""
    
    about_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About Us - Country's News</title>
    <meta name="description" content="Learn about Country's News and our commitment to quality journalism.">
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
        
        <div class="bg-white rounded-lg shadow-lg p-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Our Mission</h2>
            <p class="text-gray-700 mb-6">
                Country's News is dedicated to providing comprehensive, timely, and accurate news coverage 
                across multiple categories including politics, business, technology, sports, and more.
            </p>
            
            <h2 class="text-2xl font-bold text-gray-900 mb-4">What We Cover</h2>
            <ul class="list-disc list-inside text-gray-700 space-y-2 mb-6">
                <li>Breaking news and current events</li>
                <li>Business and economic analysis</li>
                <li>Technology trends and innovations</li>
                <li>Sports coverage and updates</li>
                <li>Culture and lifestyle topics</li>
            </ul>
            
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Contact Us</h2>
            <p class="text-gray-700">
                For inquiries, feedback, or story tips, please reach out to us at 
                <a href="mailto:contact@countrysnews.com" class="text-blue-600 hover:text-blue-800">contact@countrysnews.com</a>
            </p>
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
    
    print("✅ Generated clean about page")

def generate_sitemap(articles_data):
    """Generate sitemap"""
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
        date_modified = article.get('dateModified', article.get('publishDate', ''))
        if date_modified and date_modified.endswith('Z'):
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
    print("✅ Generated sitemap")

def generate_robots_txt():
    """Generate robots.txt"""
    robots_content = """User-agent: *
Allow: /

Sitemap: https://countrysnews.com/sitemap.xml
"""
    
    with open(os.path.join(OUTPUT_DIR, 'robots.txt'), 'w', encoding='utf-8') as f:
        f.write(robots_content)
    print("✅ Generated robots.txt")

def generate_rss_feed(articles_data):
    """Generate RSS feed"""
    recent_articles = sorted(articles_data, key=lambda x: x.get('publishDate', ''), reverse=True)[:10]
    
    rss_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Country's News</title>
        <description>Latest news and analysis from Country's News</description>
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
            <author>{article.get('author', 'Editor')}</author>
            <category>{article.get('category', 'News')}</category>
        </item>
'''
    
    rss_content += '''    </channel>
</rss>'''
    
    with open(os.path.join(OUTPUT_DIR, 'rss.xml'), 'w', encoding='utf-8') as f:
        f.write(rss_content)
    print("✅ Generated RSS feed")

if __name__ == "__main__":
    generate_clean_site()
