import json
import os
import re
import markdown # Import the markdown library

# --- Configuration ---
OUTPUT_DIR = "dist"
ARTICLES_DATA_FILE = "perplexityArticles.json"
DEFAULT_CATEGORY = "News" # Default category for articles without one

# --- HTML Templates ---
# These are multi-line strings representing the HTML structure.
# We'll use f-strings for easy variable substitution.

BASE_HTML_HEAD = """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <!-- Preconnect for performance -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <!-- Add RSS feed -->
    <link rel="alternate" type="application/rss+xml" title="Country's News RSS" href="/rss.xml">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6; /* Light gray background */
        }}
        .article-content h1, .article-content h2, .article-content h3, .article-content h4, .article-content h5, .article-content h6 {{
            margin-top: 1.5em;
            margin-bottom: 0.5em;
            font-weight: 600;
            color: #1e3a8a; /* Darker blue for headings */
        }}
        .article-content h1 {{ font-size: 2.5em; }}
        .article-content h2 {{ font-size: 2em; }}
        .article-content h3 {{ font-size: 1.75em; }}
        .article-content p {{
            margin-bottom: 1em;
            line-height: 1.7;
        }}
        .article-content ul, .article-content ol {{
            list-style-position: inside;
            margin-bottom: 1em;
            padding-left: 1.5em;
        }}
        .article-content ul li {{
            list-style-type: disc;
            margin-bottom: 0.5em;
        }}
        .article-content ol li {{
            list-style-type: decimal;
            margin-bottom: 0.5em;
        }}
        .article-card {{
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }}
        .article-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
        }}
        /* Style for inline images within article content */
        .article-content img {{
            max-width: 100%;
            height: auto;
            border-radius: 0.5rem; /* rounded-lg */
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* shadow-md */
            margin-top: 1.5rem; /* my-6 */
            margin-bottom: 1.5rem; /* my-6 */
            display: block; /* Ensures it takes up full width and allows margin auto */
            margin-left: auto;
            margin-right: auto;
        }}
        .article-content figure {{
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        .article-content figcaption {{
            text-align: center;
            color: #6b7280; /* text-gray-600 */
            font-size: 0.875rem; /* text-sm */
            margin-top: 0.5rem; /* mt-2 */
        }}
        
        /* Ad Optimization Styles */
        .ad-container {{
            margin: 2rem 0;
            padding: 1rem;
            text-align: center;
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        /* Mobile bottom ad specific styling */
        .ad-container.mobile-bottom {{
            margin: 0;
            min-height: 50px;
            border-radius: 0;
        }}
        
        .ad-placeholder {{
            color: #9ca3af;
            font-size: 0.875rem;
            font-style: italic;
        }}
        
        /* Read More / Lazy Loading Styles */
        .content-teaser {{
            max-height: 600px;
            overflow: hidden;
            position: relative;
        }}
        
        .content-teaser.expanded {{
            max-height: none;
        }}
        
        .content-fade {{
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 100px;
            background: linear-gradient(transparent, white);
            pointer-events: none;
        }}
        
        .content-teaser.expanded .content-fade {{
            display: none;
        }}
        
        .read-more-btn {{
            margin-top: 1rem;
            padding: 0.75rem 1.5rem;
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 0.5rem;
            cursor: pointer;
            font-weight: 600;
            transition: background-color 0.2s;
        }}
        
        .read-more-btn:hover {{
            background-color: #1d4ed8;
        }}
        
        /* Lazy loading placeholder */
        .lazy-image {{
            background-color: #f3f4f6;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .lazy-image.loaded {{
            background-color: transparent;
        }}
        
        /* Social Media Hashtags */
        .hashtags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .hashtag {{
            background-color: #eff6ff;
            color: #1e40af;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.875rem;
            text-decoration: none;
        }}
        
        .hashtag:hover {{
            background-color: #dbeafe;
        }}
        
        /* Load More Button Styles */
        .load-more-container {{
            text-align: center;
            margin-top: 3rem;
            margin-bottom: 2rem;
        }}
        
        .load-more-btn {{
            background-color: #2563eb;
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 0.5rem;
            font-size: 1.125rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .load-more-btn:hover {{
            background-color: #1d4ed8;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .load-more-btn:disabled {{
            background-color: #9ca3af;
            cursor: not-allowed;
            transform: none;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .loading-spinner {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s ease-in-out infinite;
            margin-right: 0.5rem;
        }}
        
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
    </style>
"""

HEADER_HTML = """
    <header class="bg-blue-800 text-white p-4 shadow-md">
        <div class="container mx-auto flex flex-wrap justify-between items-center px-4 sm:px-6 lg:px-8">
            <h1 class="text-3xl font-bold"><a href="{home_link}" class="hover:underline">Country's News</a></h1>
            <nav>
                <ul class="flex flex-wrap justify-center sm:justify-start space-x-2 sm:space-x-4">
                    <li><a href="{home_link}" class="hover:underline">Home</a></li>
                    {category_links}
                    <li><a href="#" class="hover:underline">About Us</a></li>
                    <li><a href="{contact_link}" class="hover:underline">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>
"""

FOOTER_HTML = """
    <footer class="bg-gray-800 text-white p-6 mt-12 shadow-inner">
        <div class="container mx-auto text-center">
            <p>&copy; 2025 Country's News. All rights reserved.</p>
            <div class="flex justify-center space-x-4 mt-3">
                <a href="about-us.html" class="hover:underline text-gray-400">About Us</a>
                <a href="contact.html" class="hover:underline text-gray-400">Contact</a>
                <a href="privacy-policy.html" class="hover:underline text-gray-400">Privacy Policy</a>
                <a href="disclaimer.html" class="hover:underline text-gray-400">Disclaimer</a>
            </div>
        </div>
    </footer>
"""

INDEX_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>Country's News - Latest Headlines</title>
    {BASE_HTML_HEAD}
    <!-- SEO Meta Tags for Index Page -->
    <meta name="description" content="Get the latest news and in-depth analysis from around the world on Country's News. Your source for global headlines.">
    <meta name="keywords" content="country news, global news, latest headlines, world news, news analysis">
    <meta property="og:title" content="Country's News - Latest Headlines">
    <meta property="og:description" content="Get the latest news and in-depth analysis from around the world on Country's News. Your source for global headlines.">
    <meta property="og:image" content="https://placehold.co/1200x630/1f2937/ffffff?text=Country's+News">
    <meta property="og:url" content="https://countrysnews.com/index.html">
    <meta name="twitter:card" content="summary_large_image">
</head>
<body class="antialiased text-gray-800">
    {{header_html}}
    
    <!-- Top Banner Ad - Prime Real Estate -->
    <div class="ad-container">
        <div class="ad-placeholder">Advertisement - Top Banner (728x90)</div>
    </div>
    
    <main class="container mx-auto p-6 mt-8 max-w-7xl bg-white rounded-lg shadow-lg">
        <h2 class="text-4xl font-extrabold text-center mb-10 text-blue-800">Latest Articles</h2>
        
        <!-- Featured Ad before articles -->
        <div class="ad-container">
            <div class="ad-placeholder">Advertisement - Featured Rectangle (300x250)</div>
        </div>
        
        <div id="articles-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {{initial_articles_cards}}
        </div>
        
        <!-- Mid-content Ad after initial articles -->
        <div class="ad-container">
            <div class="ad-placeholder">Advertisement - Large Rectangle (336x280)</div>
        </div>
        
        <!-- Load More Button -->
        <div class="load-more-container" id="load-more-container">
            <button id="load-more-btn" class="load-more-btn" onclick="loadMoreArticles()">
                Load More Articles
            </button>
        </div>
        
        <!-- Bottom Content Ad -->
        <div class="ad-container">
            <div class="ad-placeholder">Advertisement - Bottom Rectangle (300x250)</div>
        </div>
        
        <!-- No More Articles Message -->
        <div id="no-more-articles" class="text-center text-gray-600 mt-6" style="display: none;">
            <p class="text-lg">You've reached the end! No more articles to load.</p>
        </div>
        
        <!-- Newsletter Signup Section -->
        <div class="bg-blue-50 rounded-lg p-8 mt-12 text-center">
            <h3 class="text-3xl font-bold text-blue-800 mb-4">Stay Updated</h3>
            <p class="text-gray-600 mb-6">Subscribe to our newsletter for the latest news delivered to your inbox.</p>
            <form id="newsletter-form" class="flex flex-col sm:flex-row gap-4 max-w-md mx-auto" action="contact-handler.php" method="POST">
                <input type="hidden" name="form_type" value="newsletter">
                <input type="email" name="email" placeholder="Enter your email" required class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                <button type="submit" class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-colors">Subscribe</button>
            </form>
            <div id="newsletter-message" class="mt-4 text-sm" style="display: none;"></div>
        </div>
        
        <!-- Contact Us Call-to-Action -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg p-8 mt-12 text-center text-white">
            <h3 class="text-3xl font-bold mb-4">Have a Story to Share?</h3>
            <p class="text-blue-100 mb-6 max-w-2xl mx-auto">Got breaking news, tips, or stories? We'd love to hear from you. Contact our editorial team today.</p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center">
                <a href="contact.html" class="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 font-semibold transition-colors">Contact Us</a>
                <a href="mailto:news@countrysnews.com" class="inline-block px-8 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-400 font-semibold transition-colors">Email Editor</a>
            </div>
        </div>
        
        <!-- Newsletter Ad -->
        <div class="ad-container">
            <div class="ad-placeholder">Advertisement - Newsletter Rectangle (300x250)</div>
        </div>
        
        <!-- Footer Ad -->
        <div class="ad-container">
            <div class="ad-placeholder">Advertisement - Footer Banner (728x90)</div>
        </div>
    </main>
    
    <!-- Sticky Sidebar Ad -->
    <div class="fixed right-4 top-1/2 transform -translate-y-1/2 hidden lg:block z-10">
        <div class="ad-container w-40 h-80">
            <div class="ad-placeholder text-xs">Sidebar Ad (160x600)</div>
        </div>
    </div>
    
    <!-- Mobile Bottom Sticky Ad -->
    <div class="fixed bottom-0 left-0 right-0 bg-white shadow-lg border-t lg:hidden z-20">
        <div class="ad-container py-2 min-h-0">
            <div class="ad-placeholder text-xs">Mobile Bottom Ad (320x50)</div>
        </div>
    </div>
    
    {{javascript_content}}
    
    {FOOTER_HTML}
</body>
</html>"""

ARTICLE_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{title}} - Country's News</title>
    {BASE_HTML_HEAD}
    <!-- SEO Meta Tags for Article Page -->
    <meta name="description" content="{{metaDescription}}">
    <meta name="keywords" content="{{keywords}}">
    <meta property="og:title" content="{{ogTitle}}">
    <meta property="og:description" content="{{metaDescription}}">
    <meta property="og:image" content="{{ogImage}}">
    <meta property="og:url" content="{{ogUrl}}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{{ogTitle}}">
    <meta name="twitter:description" content="{{metaDescription}}">
    <meta name="twitter:image" content="{{ogImage}}">
    <link rel="canonical" href="{{canonicalUrl}}">
    <script type="application/ld+json">
        {{structuredData}}
    </script>
</head>
<body class="antialiased text-gray-800">
    {{header_html}}
    
    <!-- Top Banner Ad -->
    <div class="ad-container">
        <div class="ad-placeholder">Advertisement - Top Banner (728x90)</div>
    </div>
    
    <main class="container mx-auto p-6 mt-8 max-w-7xl bg-white rounded-lg shadow-lg">
        <article class="article-content">
            <h1 class="text-4xl font-extrabold text-blue-800 mb-4">{{title}}</h1>
            <div class="text-gray-600 text-sm mb-6">
                By <span class="font-semibold">{{author}}</span> | Published on {{publishDate}} | Last updated on {{dateModified}}
            </div>
            
            <!-- Social Media Hashtags at top -->
            {{social_hashtags_html}}
            
            <img src="{{ogImage}}" alt="{{imageAltText}}" class="w-full h-64 object-cover rounded-lg mb-6 shadow-md lazy-image" loading="lazy">
            
            <!-- First Ad after hero image -->
            <div class="ad-container">
                <div class="ad-placeholder">Advertisement - Rectangle (300x250)</div>
            </div>
            
            <!-- Content with Read More functionality -->
            <div id="article-content" class="content-teaser">
                {{content}}
                <div class="content-fade"></div>
            </div>
            
            <div class="text-center">
                <button id="read-more-btn" class="read-more-btn">Read Full Article</button>
            </div>
            
            <!-- Mid-content Ad -->
            <div class="ad-container">
                <div class="ad-placeholder">Advertisement - Large Rectangle (336x280)</div>
            </div>
            
            <div class="mt-8 pt-4 border-t border-gray-200 text-sm text-gray-700">
                <p class="font-semibold">Category: <a href="../categories/{{category_slug}}.html" class="text-blue-600 hover:underline">{{category}}</a></p>
                <p class="font-semibold">Tags: {{tags}}</p>
                <p class="font-semibold">Reading Time: {{readingTimeMinutes}} minutes</p>
                <p class="font-semibold">Word Count: {{wordCount}} words</p>
                <p class="font-semibold">Fact Checked By: {{factCheckedBy}}</p>
                <p class="font-semibold">Editor Reviewed By: {{editorReviewedBy}}</p>
                
                <!-- Key Takeaways -->
                {{key_takeaways_html}}
                
                <!-- Call to Action -->
                {{call_to_action_html}}
                
                <!-- Social Share Text -->
                <p class="font-semibold mt-4">Share this article: {{socialShareText}}</p>
            </div>
            
            <!-- Bottom Ad -->
            <div class="ad-container">
                <div class="ad-placeholder">Advertisement - Leaderboard (728x90)</div>
            </div>
        </article>
    </main>
    
    <!-- Sidebar Ad (Sticky) -->
    <div class="fixed right-4 top-1/2 transform -translate-y-1/2 hidden lg:block">
        <div class="ad-container w-40 h-80">
            <div class="ad-placeholder text-xs">Sidebar Ad (160x600)</div>
        </div>                         
    </div>
    
    {{javascript_content}}
    
    {FOOTER_HTML}
</body>
</html>"""

CATEGORY_TEMPLATE = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{category_name}} - Country's News</title>
    {BASE_HTML_HEAD}
    <meta name="description" content="Browse all articles in the {{category_name}} category on Country's News.">
    <meta name="keywords" content="{{category_name}}, news, articles, {{category_slug}} news">
    <meta property="og:title" content="{{category_name}} Articles - Country's News">
    <meta property="og:description" content="Browse all articles in the {{category_name}} category on Country's News.">
    <meta property="og:image" content="https://placehold.co/1200x630/1f2937/ffffff?text={{category_name}}+Category">
    <meta property="og:url" content="https://countrysnews.com/categories/{{category_slug}}.html">
    <meta name="twitter:card" content="summary_large_image">
</head>
<body class="antialiased text-gray-800">
    {{header_html}}
    
    <!-- Top Banner Ad -->
    <div class="ad-container">
        <div class="ad-placeholder">Advertisement - Top Banner (728x90)</div>
    </div>
    
    <main class="container mx-auto p-6 mt-8 max-w-7xl bg-white rounded-lg shadow-lg">
        <h2 class="text-4xl font-extrabold text-center mb-10 text-blue-800">Category: {{category_name}}</h2>
        
        <!-- Mid-page Ad before articles -->
        <div class="ad-container">
            <div class="ad-placeholder">Advertisement - Rectangle (300x250)</div>
        </div>
        
        <div id="articles-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {{articles_cards}}
        </div>
        
        <!-- Bottom Ad after articles -->
        <div class="ad-container">
            <div class="ad-placeholder">Advertisement - Large Rectangle (336x280)</div>
        </div>
        
        <!-- Footer Ad -->
        <div class="ad-container">
            <div class="ad-placeholder">Advertisement - Leaderboard (728x90)</div>
        </div>
    </main>
    
    <!-- Sidebar Ad (Sticky) -->
    <div class="fixed right-4 top-1/2 transform -translate-y-1/2 hidden lg:block">
        <div class="ad-container w-40 h-80">
            <div class="ad-placeholder text-xs">Sidebar Ad (160x600)</div>
        </div>                         
    </div>
    
    {FOOTER_HTML}
</body>
</html>"""

CONTACT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Contact Us - Country's News</title>
    {BASE_HTML_HEAD}
    <meta name="description" content="Contact Country's News editorial team. Send us news tips, story ideas, or general inquiries.">
    <meta name="keywords" content="contact, news tips, editorial team, Country's News contact">
    <meta property="og:title" content="Contact Us - Country's News">
    <meta property="og:description" content="Contact Country's News editorial team. Send us news tips, story ideas, or general inquiries.">
    <meta property="og:image" content="https://placehold.co/1200x630/1f2937/ffffff?text=Contact+Us">
    <meta property="og:url" content="https://countrysnews.com/contact.html">
    <meta name="twitter:card" content="summary_large_image">
</head>
<body class="antialiased text-gray-800">
    {{header_html}}
    
    <!-- Top Banner Ad -->
    <div class="ad-container">
        <div class="ad-placeholder">Advertisement - Top Banner (728x90)</div>
    </div>
    
    <main class="container mx-auto p-6 mt-8 max-w-4xl bg-white rounded-lg shadow-lg">
        <h1 class="text-4xl font-extrabold text-center mb-10 text-blue-800">Contact Us</h1>
        
        <div class="grid md:grid-cols-2 gap-12">
            <!-- Contact Form -->
            <div>
                <h2 class="text-2xl font-bold text-gray-800 mb-6">Send us a Message</h2>
                
                <form id="contact-form" action="contact-handler.php" method="POST" class="space-y-6">
                    <input type="hidden" name="form_type" value="contact">
                    
                    <div>
                        <label for="name" class="block text-sm font-medium text-gray-700 mb-2">Full Name *</label>
                        <input type="text" id="name" name="name" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    
                    <div>
                        <label for="email" class="block text-sm font-medium text-gray-700 mb-2">Email Address *</label>
                        <input type="email" id="email" name="email" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                    </div>
                    
                    <div>
                        <label for="subject" class="block text-sm font-medium text-gray-700 mb-2">Subject *</label>
                        <select id="subject" name="subject" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                            <option value="">Select a subject</option>
                            <option value="news_tip">News Tip</option>
                            <option value="story_idea">Story Idea</option>
                            <option value="press_release">Press Release</option>
                            <option value="general_inquiry">General Inquiry</option>
                            <option value="technical_issue">Technical Issue</option>
                            <option value="advertising">Advertising</option>
                        </select>
                    </div>
                    
                    <div>
                        <label for="message" class="block text-sm font-medium text-gray-700 mb-2">Message *</label>
                        <textarea id="message" name="message" rows="6" required placeholder="Tell us about your news tip, story idea, or inquiry..." class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"></textarea>
                    </div>
                    
                    <div>
                        <label class="flex items-center">
                            <input type="checkbox" name="newsletter_subscribe" value="yes" class="mr-2">
                            <span class="text-sm text-gray-600">Subscribe to our newsletter for latest updates</span>
                        </label>
                    </div>
                    
                    <button type="submit" class="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-colors">
                        Send Message
                    </button>
                </form>
                
                <div id="contact-message" class="mt-4 text-sm" style="display: none;"></div>
            </div>
            
            <!-- Contact Information -->
            <div>
                <h2 class="text-2xl font-bold text-gray-800 mb-6">Get in Touch</h2>
                
                <div class="space-y-6">
                    <div class="flex items-start space-x-4">
                        <div class="bg-blue-100 p-3 rounded-lg">
                            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                            </svg>
                        </div>
                        <div>
                            <h3 class="font-semibold text-gray-800">Email Us</h3>
                            <p class="text-gray-600">news@countrysnews.com</p>
                            <p class="text-gray-600">editor@countrysnews.com</p>
                        </div>
                    </div>
                    
                    <div class="flex items-start space-x-4">
                        <div class="bg-blue-100 p-3 rounded-lg">
                            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div>
                            <h3 class="font-semibold text-gray-800">Response Time</h3>
                            <p class="text-gray-600">We typically respond within 24 hours</p>
                            <p class="text-gray-600">Breaking news tips: within 2 hours</p>
                        </div>
                    </div>
                    
                    <div class="flex items-start space-x-4">
                        <div class="bg-blue-100 p-3 rounded-lg">
                            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div>
                            <h3 class="font-semibold text-gray-800">News Tips</h3>
                            <p class="text-gray-600">Have breaking news or story ideas?</p>
                            <p class="text-gray-600">We protect source confidentiality</p>
                        </div>
                    </div>
                </div>
                
                <!-- Contact Ad -->
                <div class="ad-container mt-8">
                    <div class="ad-placeholder">Advertisement - Contact Rectangle (300x250)</div>
                </div>
            </div>
        </div>
        
        <!-- FAQ Section -->
        <div class="mt-16">
            <h2 class="text-3xl font-bold text-center mb-8 text-blue-800">Frequently Asked Questions</h2>
            
            <div class="space-y-4">
                <div class="border border-gray-200 rounded-lg">
                    <button class="faq-toggle w-full p-4 text-left font-semibold hover:bg-gray-50 flex justify-between items-center">
                        How do I submit a news tip?
                        <span class="faq-icon">+</span>
                    </button>
                    <div class="faq-content hidden p-4 border-t border-gray-200">
                        <p class="text-gray-600">Use our contact form above and select "News Tip" as the subject. Provide as much detail as possible including who, what, when, where, and why. We protect source confidentiality.</p>
                    </div>
                </div>
                
                <div class="border border-gray-200 rounded-lg">
                    <button class="faq-toggle w-full p-4 text-left font-semibold hover:bg-gray-50 flex justify-between items-center">
                        Can I submit guest articles?
                        <span class="faq-icon">+</span>
                    </button>
                    <div class="faq-content hidden p-4 border-t border-gray-200">
                        <p class="text-gray-600">Yes! Send us your article ideas or drafts via the contact form. Select "Story Idea" and include a brief outline of your proposed article and your credentials.</p>
                    </div>
                </div>
                
                <div class="border border-gray-200 rounded-lg">
                    <button class="faq-toggle w-full p-4 text-left font-semibold hover:bg-gray-50 flex justify-between items-center">
                        How can I advertise on your website?
                        <span class="faq-icon">+</span>
                    </button>
                    <div class="faq-content hidden p-4 border-t border-gray-200">
                        <p class="text-gray-600">Contact us using the form above and select "Advertising" as the subject. We offer various ad formats and competitive rates for businesses looking to reach our audience.</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Bottom Ad -->
        <div class="ad-container mt-12">
            <div class="ad-placeholder">Advertisement - Bottom Banner (728x90)</div>
        </div>
    </main>
    
    <!-- Sidebar Ad (Sticky) -->
    <div class="fixed right-4 top-1/2 transform -translate-y-1/2 hidden lg:block z-10">
        <div class="ad-container w-40 h-80">
            <div class="ad-placeholder text-xs">Sidebar Ad (160x600)</div>
        </div>
    </div>
    
    <!-- Contact Form JavaScript -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Contact form submission
            const contactForm = document.getElementById('contact-form');
            const contactMessage = document.getElementById('contact-message');
            
            contactForm.addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const formData = new FormData(this);
                const submitBtn = this.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                
                // Show loading state
                submitBtn.textContent = 'Sending...';
                submitBtn.disabled = true;
                
                try {{
                    const response = await fetch('contact-handler.php', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    if (response.ok) {{
                        contactMessage.innerHTML = '<p class="text-green-600 font-semibold">✓ Message sent successfully! We\\'ll get back to you soon.</p>';
                        contactMessage.style.display = 'block';
                        this.reset();
                    }} else {{
                        throw new Error('Failed to send message');
                    }}
                }} catch (error) {{
                    contactMessage.innerHTML = '<p class="text-red-600 font-semibold">✗ Failed to send message. Please try again later.</p>';
                    contactMessage.style.display = 'block';
                }} finally {{
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                    
                    // Hide message after 5 seconds
                    setTimeout(() => {{
                        contactMessage.style.display = 'none';
                    }}, 5000);
                }}
            }});
            
            // FAQ toggle functionality
            const faqToggles = document.querySelectorAll('.faq-toggle');
            faqToggles.forEach(toggle => {{
                toggle.addEventListener('click', function() {{
                    const content = this.nextElementSibling;
                    const icon = this.querySelector('.faq-icon');
                    
                    if (content.classList.contains('hidden')) {{
                        content.classList.remove('hidden');
                        icon.textContent = '-';
                    }} else {{
                        content.classList.add('hidden');
                        icon.textContent = '+';
                    }}
                }});
            }});
        }});
    </script>
    
    {FOOTER_HTML}
</body>
</html>"""

# Privacy Policy Template
PRIVACY_POLICY_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Privacy Policy - Country's News</title>
    {BASE_HTML_HEAD}
    <meta name="description" content="Privacy Policy for Country's News. Learn how we collect, use, and protect your personal information.">
    <meta name="keywords" content="privacy policy, data protection, Country's News privacy">
    <meta property="og:title" content="Privacy Policy - Country's News">
    <meta property="og:description" content="Privacy Policy for Country's News. Learn how we collect, use, and protect your personal information.">
    <meta property="og:image" content="https://placehold.co/1200x630/1f2937/ffffff?text=Privacy+Policy">
    <meta property="og:url" content="https://countrysnews.com/privacy-policy.html">
    <meta name="twitter:card" content="summary_large_image">
</head>
<body class="antialiased text-gray-800">
    {{header_html}}
    
    <!-- Top Banner Ad -->
    <div class="ad-container">
        <div class="ad-placeholder">Advertisement - Top Banner (728x90)</div>
    </div>
    
    <main class="container mx-auto p-6 mt-8 max-w-4xl bg-white rounded-lg shadow-lg">
        <h1 class="text-4xl font-extrabold text-center mb-10 text-blue-800">Privacy Policy</h1>
        
        <div class="prose max-w-none">
            <p class="text-gray-600 mb-6"><strong>Last updated:</strong> August 5, 2025</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Introduction</h2>
            <p class="mb-4">Country's News ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website countrysnews.com.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Information We Collect</h2>
            <h3 class="text-xl font-semibold text-gray-800 mt-6 mb-3">Personal Information</h3>
            <p class="mb-4">We may collect personal information that you voluntarily provide to us when you:</p>
            <ul class="list-disc ml-6 mb-4">
                <li>Subscribe to our newsletter</li>
                <li>Contact us through our contact form</li>
                <li>Submit news tips or story ideas</li>
                <li>Comment on articles or engage with our content</li>
            </ul>
            
            <h3 class="text-xl font-semibold text-gray-800 mt-6 mb-3">Automatically Collected Information</h3>
            <p class="mb-4">When you visit our website, we may automatically collect certain information about your device, including:</p>
            <ul class="list-disc ml-6 mb-4">
                <li>IP address</li>
                <li>Browser type and version</li>
                <li>Operating system</li>
                <li>Referring website</li>
                <li>Pages viewed and time spent on our site</li>
                <li>Date and time of visits</li>
            </ul>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">How We Use Your Information</h2>
            <p class="mb-4">We use the information we collect to:</p>
            <ul class="list-disc ml-6 mb-4">
                <li>Provide and maintain our news service</li>
                <li>Send newsletters and updates (with your consent)</li>
                <li>Respond to your inquiries and provide customer support</li>
                <li>Improve our website and content</li>
                <li>Analyze website usage and trends</li>
                <li>Comply with legal obligations</li>
            </ul>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Information Sharing</h2>
            <p class="mb-4">We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except in the following circumstances:</p>
            <ul class="list-disc ml-6 mb-4">
                <li>To comply with legal requirements</li>
                <li>To protect our rights and safety</li>
                <li>With service providers who assist us in operating our website</li>
                <li>In connection with a business transfer or merger</li>
            </ul>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Cookies and Tracking Technologies</h2>
            <p class="mb-4">We may use cookies and similar tracking technologies to enhance your experience on our website. You can choose to disable cookies through your browser settings, though this may affect website functionality.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Data Security</h2>
            <p class="mb-4">We implement appropriate security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. However, no method of transmission over the internet is 100% secure.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Your Rights</h2>
            <p class="mb-4">You have the right to:</p>
            <ul class="list-disc ml-6 mb-4">
                <li>Access your personal information</li>
                <li>Correct inaccurate information</li>
                <li>Request deletion of your information</li>
                <li>Opt-out of marketing communications</li>
                <li>File a complaint with data protection authorities</li>
            </ul>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Third-Party Links</h2>
            <p class="mb-4">Our website may contain links to third-party websites. We are not responsible for the privacy practices of these external sites and encourage you to review their privacy policies.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Children's Privacy</h2>
            <p class="mb-4">Our website is not intended for children under 13 years of age. We do not knowingly collect personal information from children under 13.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Changes to This Privacy Policy</h2>
            <p class="mb-4">We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page with an updated effective date.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Contact Us</h2>
            <p class="mb-4">If you have any questions about this Privacy Policy, please contact us:</p>
            <ul class="list-disc ml-6 mb-4">
                <li>Email: privacy@countrysnews.com</li>
                <li>Contact form: <a href="contact.html" class="text-blue-600 hover:underline">Contact Us</a></li>
            </ul>
        </div>
        
        <!-- Bottom Ad -->
        <div class="ad-container mt-12">
            <div class="ad-placeholder">Advertisement - Bottom Banner (728x90)</div>
        </div>
    </main>
    
    <!-- Sidebar Ad (Sticky) -->
    <div class="fixed right-4 top-1/2 transform -translate-y-1/2 hidden lg:block z-10">
        <div class="ad-container w-40 h-80">
            <div class="ad-placeholder text-xs">Sidebar Ad (160x600)</div>
        </div>
    </div>
    
    {FOOTER_HTML}
</body>
</html>"""

# Disclaimer Template
DISCLAIMER_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Disclaimer - Country's News</title>
    {BASE_HTML_HEAD}
    <meta name="description" content="Disclaimer for Country's News. Important information about our content and services.">
    <meta name="keywords" content="disclaimer, terms, Country's News disclaimer">
    <meta property="og:title" content="Disclaimer - Country's News">
    <meta property="og:description" content="Disclaimer for Country's News. Important information about our content and services.">
    <meta property="og:image" content="https://placehold.co/1200x630/1f2937/ffffff?text=Disclaimer">
    <meta property="og:url" content="https://countrysnews.com/disclaimer.html">
    <meta name="twitter:card" content="summary_large_image">
</head>
<body class="antialiased text-gray-800">
    {{header_html}}
    
    <!-- Top Banner Ad -->
    <div class="ad-container">
        <div class="ad-placeholder">Advertisement - Top Banner (728x90)</div>
    </div>
    
    <main class="container mx-auto p-6 mt-8 max-w-4xl bg-white rounded-lg shadow-lg">
        <h1 class="text-4xl font-extrabold text-center mb-10 text-blue-800">Disclaimer</h1>
        
        <div class="prose max-w-none">
            <p class="text-gray-600 mb-6"><strong>Last updated:</strong> August 5, 2025</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">General Information</h2>
            <p class="mb-4">The information on this website is provided on an "as is" basis. To the fullest extent permitted by law, Country's News excludes all representations, warranties, obligations, and liabilities arising out of or in connection with this website and its contents.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">News Content Accuracy</h2>
            <p class="mb-4">While we strive to provide accurate and up-to-date news information, Country's News makes no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability, or availability of the information, products, services, or related graphics contained on the website.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Editorial Independence</h2>
            <p class="mb-4">Our editorial content is independent and based on journalistic principles. However, opinions expressed in articles are those of the individual authors and do not necessarily reflect the views of Country's News as an organization.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Third-Party Content</h2>
            <p class="mb-4">This website may include content from third parties, including:</p>
            <ul class="list-disc ml-6 mb-4">
                <li>Guest articles and opinion pieces</li>
                <li>User-generated content and comments</li>
                <li>Social media embeds</li>
                <li>External news sources and wire services</li>
            </ul>
            <p class="mb-4">We do not endorse or take responsibility for the accuracy of third-party content.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">External Links</h2>
            <p class="mb-4">Our website may contain links to external websites that are not provided or maintained by Country's News. We do not guarantee the accuracy, relevance, timeliness, or completeness of any information on these external websites.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Financial Information</h2>
            <p class="mb-4">Any financial information provided on this website is for informational purposes only and should not be considered as financial advice. Always consult with qualified financial professionals before making investment decisions.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Medical and Health Information</h2>
            <p class="mb-4">Health-related information on this website is for educational purposes only and is not intended as medical advice. Always consult with healthcare professionals for medical concerns.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Legal Information</h2>
            <p class="mb-4">Legal information provided on this website is for general informational purposes only and does not constitute legal advice. Consult with qualified legal professionals for specific legal matters.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Limitation of Liability</h2>
            <p class="mb-4">Country's News shall not be liable for any direct, indirect, incidental, consequential, or punitive damages arising out of your use of this website or reliance on any information provided.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Copyright and Fair Use</h2>
            <p class="mb-4">We respect intellectual property rights and operate under fair use principles for news reporting. If you believe any content infringes on your copyright, please contact us immediately.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Changes to This Disclaimer</h2>
            <p class="mb-4">We reserve the right to modify this disclaimer at any time. Changes will be effective immediately upon posting on this website.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Contact Information</h2>
            <p class="mb-4">If you have any questions about this disclaimer, please contact us:</p>
            <ul class="list-disc ml-6 mb-4">
                <li>Email: legal@countrysnews.com</li>
                <li>Contact form: <a href="contact.html" class="text-blue-600 hover:underline">Contact Us</a></li>
            </ul>
        </div>
        
        <!-- Bottom Ad -->
        <div class="ad-container mt-12">
            <div class="ad-placeholder">Advertisement - Bottom Banner (728x90)</div>
        </div>
    </main>
    
    <!-- Sidebar Ad (Sticky) -->
    <div class="fixed right-4 top-1/2 transform -translate-y-1/2 hidden lg:block z-10">
        <div class="ad-container w-40 h-80">
            <div class="ad-placeholder text-xs">Sidebar Ad (160x600)</div>
        </div>
    </div>
    
    {FOOTER_HTML}
</body>
</html>"""

# About Us Template
ABOUT_US_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>About Us - Country's News</title>
    {BASE_HTML_HEAD}
    <meta name="description" content="Learn about Country's News - your trusted source for global news and in-depth analysis.">
    <meta name="keywords" content="about us, Country's News, news team, journalism">
    <meta property="og:title" content="About Us - Country's News">
    <meta property="og:description" content="Learn about Country's News - your trusted source for global news and in-depth analysis.">
    <meta property="og:image" content="https://placehold.co/1200x630/1f2937/ffffff?text=About+Us">
    <meta property="og:url" content="https://countrysnews.com/about-us.html">
    <meta name="twitter:card" content="summary_large_image">
</head>
<body class="antialiased text-gray-800">
    {{header_html}}
    
    <!-- Top Banner Ad -->
    <div class="ad-container">
        <div class="ad-placeholder">Advertisement - Top Banner (728x90)</div>
    </div>
    
    <main class="container mx-auto p-6 mt-8 max-w-4xl bg-white rounded-lg shadow-lg">
        <h1 class="text-4xl font-extrabold text-center mb-10 text-blue-800">About Country's News</h1>
        
        <div class="prose max-w-none">
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Our Mission</h2>
            <p class="mb-4 text-lg">Country's News is dedicated to delivering accurate, timely, and comprehensive news coverage from around the world. We believe in the power of informed journalism to strengthen communities and democracies globally.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">What We Do</h2>
            <p class="mb-4">Our team of experienced journalists and contributors work around the clock to bring you:</p>
            <ul class="list-disc ml-6 mb-4">
                <li><strong>Breaking News:</strong> Real-time coverage of major events as they unfold</li>
                <li><strong>In-Depth Analysis:</strong> Comprehensive examination of complex issues</li>
                <li><strong>Sports Coverage:</strong> From local matches to international championships</li>
                <li><strong>Business & Economy:</strong> Market trends and economic developments</li>
                <li><strong>Technology:</strong> Latest innovations and digital trends</li>
                <li><strong>Environment:</strong> Climate change and sustainability reporting</li>
            </ul>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Our Values</h2>
            <div class="grid md:grid-cols-2 gap-6 mb-6">
                <div class="bg-blue-50 p-6 rounded-lg">
                    <h3 class="text-xl font-semibold text-blue-800 mb-3">Accuracy</h3>
                    <p>We fact-check our stories and correct errors promptly when they occur.</p>
                </div>
                <div class="bg-blue-50 p-6 rounded-lg">
                    <h3 class="text-xl font-semibold text-blue-800 mb-3">Independence</h3>
                    <p>Our editorial decisions are made free from political or commercial influence.</p>
                </div>
                <div class="bg-blue-50 p-6 rounded-lg">
                    <h3 class="text-xl font-semibold text-blue-800 mb-3">Transparency</h3>
                    <p>We clearly identify our sources and disclose potential conflicts of interest.</p>
                </div>
                <div class="bg-blue-50 p-6 rounded-lg">
                    <h3 class="text-xl font-semibold text-blue-800 mb-3">Fairness</h3>
                    <p>We strive to present multiple perspectives on controversial issues.</p>
                </div>
            </div>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Our Team</h2>
            <p class="mb-4">Country's News is powered by a diverse team of journalists, editors, and contributors from around the world. Our newsroom operates 24/7 to ensure you never miss important developments.</p>
            
            <div class="bg-gray-50 p-6 rounded-lg mb-6">
                <h3 class="text-xl font-semibold text-gray-800 mb-3">Editorial Team</h3>
                <p class="mb-3">Led by experienced editors with decades of journalism experience, our editorial team ensures every story meets our high standards for accuracy and relevance.</p>
                <p><strong>Editor-in-Chief:</strong> [Name]</p>
                <p><strong>Managing Editor:</strong> [Name]</p>
                <p><strong>Sports Editor:</strong> [Name]</p>
                <p><strong>Business Editor:</strong> [Name]</p>
            </div>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Coverage Areas</h2>
            <p class="mb-4">While we cover global news, we have particular expertise in:</p>
            <ul class="list-disc ml-6 mb-4">
                <li>International politics and diplomacy</li>
                <li>Economic trends and market analysis</li>
                <li>Sports from grassroots to professional levels</li>
                <li>Technology and innovation</li>
                <li>Environmental and climate issues</li>
                <li>Social and cultural developments</li>
            </ul>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Awards & Recognition</h2>
            <p class="mb-4">Our commitment to excellence in journalism has been recognized through various industry awards and reader testimonials. We're proud to be a trusted news source for readers worldwide.</p>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Get Involved</h2>
            <p class="mb-4">We encourage reader engagement and welcome:</p>
            <ul class="list-disc ml-6 mb-4">
                <li><strong>News Tips:</strong> Have a story idea? <a href="contact.html" class="text-blue-600 hover:underline">Contact us</a></li>
                <li><strong>Guest Articles:</strong> Share your expertise with our readers</li>
                <li><strong>Letters to the Editor:</strong> Join the conversation on important issues</li>
                <li><strong>Newsletter:</strong> Subscribe for daily updates delivered to your inbox</li>
            </ul>
            
            <h2 class="text-2xl font-bold text-blue-800 mt-8 mb-4">Contact Information</h2>
            <div class="bg-blue-50 p-6 rounded-lg">
                <p class="mb-2"><strong>General Inquiries:</strong> news@countrysnews.com</p>
                <p class="mb-2"><strong>Editorial Team:</strong> editor@countrysnews.com</p>
                <p class="mb-2"><strong>News Tips:</strong> tips@countrysnews.com</p>
                <p class="mb-2"><strong>Advertising:</strong> advertising@countrysnews.com</p>
                <p><strong>Contact Form:</strong> <a href="contact.html" class="text-blue-600 hover:underline">Submit a message</a></p>
            </div>
            
            <div class="mt-8 p-6 bg-gradient-to-r from-blue-600 to-blue-800 rounded-lg text-white text-center">
                <h3 class="text-2xl font-bold mb-4">Stay Connected</h3>
                <p class="mb-6">Follow us for the latest news updates and behind-the-scenes content.</p>
                <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <a href="contact.html" class="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg hover:bg-gray-100 font-semibold transition-colors">Contact Us</a>
                    <a href="#newsletter" class="inline-block px-8 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-400 font-semibold transition-colors">Subscribe to Newsletter</a>
                </div>
            </div>
        </div>
        
        <!-- Mid-page Ad -->
        <div class="ad-container mt-12">
            <div class="ad-placeholder">Advertisement - Rectangle (300x250)</div>
        </div>
        
        <!-- Bottom Ad -->
        <div class="ad-container">
            <div class="ad-placeholder">Advertisement - Bottom Banner (728x90)</div>
        </div>
    </main>
    
    <!-- Sidebar Ad (Sticky) -->
    <div class="fixed right-4 top-1/2 transform -translate-y-1/2 hidden lg:block z-10">
        <div class="ad-container w-40 h-80">
            <div class="ad-placeholder text-xs">Sidebar Ad (160x600)</div>
        </div>
    </div>
    
    {FOOTER_HTML}
</body>
</html>"""

# --- Helper Functions ---

def generate_slug(text):
    """Generates a URL-friendly slug from a given string."""
    if not text:
        return ""
    slug = re.sub(r'[^\w\s-]', '', text).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug

def create_directory(path):
    """Creates a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def generate_header_html(unique_categories, current_page_type="home"):
    """Generates the header HTML with dynamic category links."""
    category_links = ""
    for category in unique_categories:
        category_slug = generate_slug(category)
        # Adjust path based on current page type
        if current_page_type == "article":
            link_prefix = "../categories/"
        elif current_page_type == "category":
            link_prefix = "" # Already in categories directory
        else: # home page or contact page (both at root level)
            link_prefix = "categories/"
        category_links += f'<li><a href="{link_prefix}{category_slug}.html" class="hover:underline">{category}</a></li>'
    
    home_link = "../index.html" if current_page_type in ["article", "category"] else "index.html"
    contact_link = "../contact.html" if current_page_type in ["article", "category"] else "contact.html"

    return HEADER_HTML.format(home_link=home_link, category_links=category_links, contact_link=contact_link)

def adjust_image_url_for_path(image_url, current_page_type):
    """
    Adjusts an image URL (ogImage, thumbnailImageUrl) based on the current page type.
    If the URL is relative and starts with 'images/', it prepends '../' for article/category pages.
    """
    if image_url and not image_url.startswith(('http://', 'https://')):
        # Remove 'dist/' prefix if present, as it's an internal representation
        if image_url.startswith('dist/'):
            image_url = image_url[len('dist/'):]

        if current_page_type in ["article", "category"]:
            return "../" + image_url
    return image_url


def generate_article_card(article, current_page_type="home"):
    """Generates HTML for a single article card."""
    # Determine the prefix needed for links and image paths from this card's location
    link_prefix = ""
    if current_page_type == "category":
        link_prefix = "../"
    elif current_page_type == "article": # Article pages are in 'articles/' so links to other articles need '../'
        link_prefix = "../"

    # Create thumbnail URL - priority order: thumbnailImageUrl, ogImage with thumb.jpg, ogImage, placeholder
    thumbnail_url = ''
    
    # First, check if article has a dedicated thumbnailImageUrl
    if article.get('thumbnailImageUrl') and article['thumbnailImageUrl'] != article.get('ogImage', ''):
        thumbnail_url = article['thumbnailImageUrl']
    else:
        # Fall back to ogImage logic
        og_image = article.get('ogImage', '')
        if og_image and 'main.jpg' in og_image:
            # Replace main.jpg with thumb.jpg
            thumbnail_url = og_image.replace('main.jpg', 'thumb.jpg')
        elif og_image:
            # If ogImage exists but doesn't have main.jpg, use it as is
            thumbnail_url = og_image
    
    # Final fallback to placeholder if no valid thumbnail found
    if not thumbnail_url:
        thumbnail_url = 'https://placehold.co/400x200/cccccc/333333?text=No+Image'
    
    thumbnail_url = adjust_image_url_for_path(thumbnail_url, current_page_type)
    
    return f"""
    <div class="bg-white rounded-lg shadow-md overflow-hidden article-card">
        <a href="{link_prefix}articles/{article['slug']}.html">
            <img src="{thumbnail_url}" alt="{article.get('imageAltText', article['title'])}" class="w-full h-48 object-cover" loading="lazy">
        </a>
        <div class="p-6">
            <h3 class="font-bold text-xl mb-2 leading-tight">
                <a href="{link_prefix}articles/{article['slug']}.html" class="hover:text-blue-700">{article['title']}</a>
            </h3>
            <p class="text-gray-600 text-sm mb-4">
                By <span class="font-semibold">{article['author']}</span> on {article['publishDate']}
            </p>
            <p class="text-gray-700 text-base mb-4">
                {article['excerpt']}
            </p>
            <a href="{link_prefix}articles/{article['slug']}.html" class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full text-sm">
                Read More
            </a>
        </div>
    </div>
    """

def adjust_inline_image_paths_in_html(html_content, path_prefix):
    """
    Adjusts relative image paths within HTML content by prepending a path_prefix
    and adds loading="lazy" to img tags if not already present.
    This is for images whose src starts with 'images/' (relative to dist root).
    """
    def replace_src_and_add_lazy(match):
        original_src_attr_start = match.group(1) # e.g., src=" or src='
        original_src_value = match.group(2) # e.g., images/...
        rest_of_tag = match.group(3) # e.g., " alt="..." >

        # Adjust path
        if not original_src_value.startswith(('http://', 'https://', '/')):
            if original_src_value.startswith('dist/'):
                original_src_value = original_src_value[len('dist/'):]
            new_src_value = path_prefix + original_src_value
            new_src_attr = f'{original_src_attr_start}{new_src_value}' # Reconstruct src attribute

        else:
            new_src_attr = original_src_attr_start + original_src_value # No change if absolute or already adjusted

        # Add loading="lazy" if not already present
        if 'loading="lazy"' not in rest_of_tag and "loading='lazy'" not in rest_of_tag:
            # Insert loading="lazy" before the closing > of the img tag
            rest_of_tag = rest_of_tag.replace('>', ' loading="lazy">', 1)

        return f'{new_src_attr}{rest_of_tag}' # Return the reconstructed attribute and rest of tag

    # Regex to find src attributes in img tags
    # Group 1: src=" or src='
    # Group 2: the actual src value
    # Group 3: everything after the src value (closing quote and rest of tag)
    pattern = r'(src=["\'])([^"\']+)(["\'][^>]*>)'
    return re.sub(pattern, replace_src_and_add_lazy, html_content, flags=re.IGNORECASE)


def generate_index_page(articles_data, unique_categories):
    """Generates the main index.html page with load more functionality and ads."""
    print("Generating index.html...")
    index_path = os.path.join(OUTPUT_DIR, "index.html")
    
    # Configuration for load more functionality
    articles_per_page = 9  # Number of articles to show initially and per load
    
    # Sort articles by publish date, newest first for the index page
    sorted_articles = sorted(articles_data, key=lambda x: x['publishDate'], reverse=True)
    
    # Generate initial articles with interspersed ads (first page)
    initial_articles = sorted_articles[:articles_per_page]
    initial_articles_cards = ""
    
    for i, article in enumerate(initial_articles):
        # For index.html, current_page_type is "home", so image paths remain relative to dist/
        initial_articles_cards += generate_article_card(article, current_page_type="home")
        
        # Insert ad after every 3rd article (positions 3, 6, etc.)
        if (i + 1) % 3 == 0 and (i + 1) < len(initial_articles):
            ad_type = "Square" if (i + 1) % 6 == 0 else "Rectangle" 
            ad_size = "(300x300)" if ad_type == "Square" else "(300x250)"
            initial_articles_cards += f"""
                <div class="col-span-1 md:col-span-2 lg:col-span-3">
                    <div class="ad-container">
                        <div class="ad-placeholder">Advertisement - Grid {ad_type} {ad_size}</div>
                    </div>
                </div>
            """

    # Generate articles data JSON file for AJAX loading
    articles_data_path = os.path.join(OUTPUT_DIR, "articles-data.json")
    articles_json_data = {
        "articles": sorted_articles,
        "total": len(sorted_articles),
        "articlesPerPage": articles_per_page
    }
    
    try:
        with open(articles_data_path, 'w', encoding='utf-8') as f:
            json.dump(articles_json_data, f, ensure_ascii=False, indent=2)
        print(f"Generated {articles_data_path} for AJAX loading")
    except Exception as e:
        print(f"Error generating articles data JSON: {e}")

    header_html = generate_header_html(unique_categories, current_page_type="home")

    # Generate JavaScript content separately to avoid brace conflicts
    javascript_content = f"""
    <!-- JavaScript for Load More Functionality -->
    <script>
        let currentPage = 1;
        const articlesPerPage = {articles_per_page};
        let allArticles = [];
        let isLoading = false;
        
        // Load articles data
        async function loadArticlesData() {{
            try {{
                const response = await fetch('articles-data.json');
                const data = await response.json();
                allArticles = data.articles;
                
                // Check if we need to show the load more button
                if (allArticles.length <= articlesPerPage) {{
                    document.getElementById('load-more-container').style.display = 'none';
                }}
            }} catch (error) {{
                console.error('Error loading articles data:', error);
            }}
        }}
        
        async function loadMoreArticles() {{
            if (isLoading) return;
            
            isLoading = true;
            const loadMoreBtn = document.getElementById('load-more-btn');
            const originalText = loadMoreBtn.innerHTML;
            
            // Show loading state
            loadMoreBtn.innerHTML = '<span class="loading-spinner"></span>Loading...';
            loadMoreBtn.disabled = true;
            
            // Simulate loading delay for better UX
            await new Promise(resolve => setTimeout(resolve, 500));
            
            const startIndex = currentPage * articlesPerPage;
            const endIndex = startIndex + articlesPerPage;
            const articlesToLoad = allArticles.slice(startIndex, endIndex);
            
            if (articlesToLoad.length === 0) {{
                // No more articles
                document.getElementById('load-more-container').style.display = 'none';
                document.getElementById('no-more-articles').style.display = 'block';
                isLoading = false;
                return;
            }}
            
            // Add new articles to the container with interspersed ads
            const articlesContainer = document.getElementById('articles-container');
            let articlesAdded = 0;
            
            articlesToLoad.forEach((article, index) => {{
                const articleCard = createArticleCard(article);
                articlesContainer.insertAdjacentHTML('beforeend', articleCard);
                articlesAdded++;
                
                // Insert ad after every 3rd loaded article
                if ((articlesAdded) % 3 === 0 && (index + 1) < articlesToLoad.length) {{
                    const adType = (articlesAdded) % 6 === 0 ? 'Square' : 'Rectangle';
                    const adSize = adType === 'Square' ? '(300x300)' : '(300x250)';
                    const adHtml = `
                        <div class="col-span-1 md:col-span-2 lg:col-span-3">
                            <div class="ad-container">
                                <div class="ad-placeholder">Advertisement - Load More ${{adType}} ${{adSize}}</div>
                            </div>
                        </div>
                    `;
                    articlesContainer.insertAdjacentHTML('beforeend', adHtml);
                }}
            }});
            
            currentPage++;
            
            // Check if we've loaded all articles
            if (endIndex >= allArticles.length) {{
                document.getElementById('load-more-container').style.display = 'none';
                document.getElementById('no-more-articles').style.display = 'block';
            }} else {{
                // Reset button state
                loadMoreBtn.innerHTML = originalText;
                loadMoreBtn.disabled = false;
            }}
            
            isLoading = false;
        }}
        
        function createArticleCard(article) {{
            // Create thumbnail URL - priority order: thumbnailImageUrl, ogImage with thumb.jpg, ogImage, placeholder
            let thumbnailUrl = '';
            
            // First, check if article has a dedicated thumbnailImageUrl
            if (article.thumbnailImageUrl && article.thumbnailImageUrl !== article.ogImage) {{
                thumbnailUrl = article.thumbnailImageUrl;
            }} else {{
                // Fall back to ogImage logic
                thumbnailUrl = article.ogImage || '';
                if (thumbnailUrl && thumbnailUrl.includes('main.jpg')) {{
                    thumbnailUrl = thumbnailUrl.replace('main.jpg', 'thumb.jpg');
                }}
            }}
            
            // Final fallback to placeholder if no valid thumbnail found
            if (!thumbnailUrl) {{
                thumbnailUrl = 'https://placehold.co/400x200/cccccc/333333?text=No+Image';
            }}
            
            // Remove 'dist/' prefix if present since we're on the home page
            if (thumbnailUrl.startsWith('dist/')) {{
                thumbnailUrl = thumbnailUrl.substring(5); // Remove 'dist/' prefix
            }}
                
            return `
                <div class="bg-white rounded-lg shadow-md overflow-hidden article-card">
                    <a href="articles/${{article.slug}}.html">
                        <img src="${{thumbnailUrl}}" alt="${{article.imageAltText || article.title}}" class="w-full h-48 object-cover" loading="lazy">
                    </a>
                    <div class="p-6">
                        <h3 class="font-bold text-xl mb-2 leading-tight">
                            <a href="articles/${{article.slug}}.html" class="hover:text-blue-700">${{article.title}}</a>
                        </h3>
                        <p class="text-gray-600 text-sm mb-4">
                            By <span class="font-semibold">${{article.author}}</span> on ${{article.publishDate}}
                        </p>
                        <p class="text-gray-700 text-base mb-4">
                            ${{article.excerpt}}
                        </p>
                        <a href="articles/${{article.slug}}.html" class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-full text-sm">
                            Read More
                        </a>
                    </div>
                </div>
            `;
        }}
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {{
            loadArticlesData();
            
            // Newsletter form submission
            const newsletterForm = document.getElementById('newsletter-form');
            const newsletterMessage = document.getElementById('newsletter-message');
            
            newsletterForm.addEventListener('submit', async function(e) {{
                e.preventDefault();
                
                const formData = new FormData(this);
                const submitBtn = this.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                
                // Show loading state
                submitBtn.textContent = 'Subscribing...';
                submitBtn.disabled = true;
                
                try {{
                    const response = await fetch('contact-handler.php', {{
                        method: 'POST',
                        body: formData
                    }});
                    
                    const result = await response.text();
                    
                    if (response.ok) {{
                        newsletterMessage.innerHTML = '<p class="text-green-600 font-semibold">✓ Successfully subscribed! Check your email for confirmation.</p>';
                        newsletterMessage.style.display = 'block';
                        this.reset();
                    }} else {{
                        throw new Error('Subscription failed');
                    }}
                }} catch (error) {{
                    newsletterMessage.innerHTML = '<p class="text-red-600 font-semibold">✗ Subscription failed. Please try again later.</p>';
                    newsletterMessage.style.display = 'block';
                }} finally {{
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                    
                    // Hide message after 5 seconds
                    setTimeout(() => {{
                        newsletterMessage.style.display = 'none';
                    }}, 5000);
                }}
            }});
        }});
    </script>
    """

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(INDEX_TEMPLATE.format(
            header_html=header_html, 
            initial_articles_cards=initial_articles_cards,
            javascript_content=javascript_content
        ))
    print(f"Generated {index_path} with Load More functionality")
    print(f"Initial load: {len(initial_articles)} articles, Total available: {len(sorted_articles)} articles")

def generate_article_pages(articles_data, unique_categories):
    """Generates individual HTML pages for each article."""
    print("Generating article pages...")
    articles_dir = os.path.join(OUTPUT_DIR, "articles")
    create_directory(articles_dir)

    for article in articles_data:
        article_path = os.path.join(articles_dir, f"{article['slug']}.html")
        
        # Prepare dynamic SEO fields, with fallbacks
        meta_description = article.get('metaDescription', article['excerpt'])
        keywords = ", ".join(article.get('keywords', article.get('tags', [])))
        og_title = article.get('ogTitle', article['title'])
        
        # Adjust ogImage path for article page (needs ../)
        og_image = adjust_image_url_for_path(article.get('ogImage', 'https://placehold.co/1200x630/1f2937/ffffff?text=Country%27s+News'), "article")

        image_alt_text = article.get('imageAltText', article['title'])
        og_url = article.get('ogUrl', f"https://countrysnews.com/articles/{article['slug']}.html")
        canonical_url = article.get('canonicalUrl', f"https://countrysnews.com/articles/{article['slug']}.html")
        
        # Structured Data: Ensure it's a valid JSON string
        structured_data = article.get('structuredData', '{}')
        try:
            json.loads(structured_data)
        except json.JSONDecodeError:
            print(f"Warning: Malformed structuredData for article {article['id']}. Using empty JSON-LD.")
            structured_data = '{}'

        # Generate Key Takeaways HTML
        key_takeaways_html = ""
        if article.get('keyTakeaways'):
            key_takeaways_html = '<h4 class="font-bold text-lg mt-6 mb-2 text-blue-700">Key Takeaways:</h4><ul class="list-disc ml-6 mb-4">'
            for item in article['keyTakeaways']:
                key_takeaways_html += f'<li>{item}</li>'
            key_takeaways_html += '</ul>'

        # Generate Call to Action HTML
        call_to_action_html = ""
        if article.get('callToActionText'):
            call_to_action_html = f'<p class="mt-4 p-4 bg-blue-50 border-l-4 border-blue-400 text-blue-800 rounded-md italic">{article["callToActionText"]}</p>'

        # Generate Social Media Hashtags HTML
        social_hashtags_html = ""
        if article.get('socialMediaHashtags'):
            social_hashtags_html = '<div class="hashtags mb-6">'
            for hashtag in article['socialMediaHashtags']:
                social_hashtags_html += f'<span class="hashtag">{hashtag}</span>'
            social_hashtags_html += '</div>'

        # Generate JavaScript content separately to avoid brace conflicts
        javascript_content = """
    <!-- JavaScript for Read More and Lazy Loading -->
    <script>
        // Read More functionality
        document.addEventListener('DOMContentLoaded', function() {
            const content = document.getElementById('article-content');
            const readMoreBtn = document.getElementById('read-more-btn');
            
            readMoreBtn.addEventListener('click', function() {
                content.classList.toggle('expanded');
                if (content.classList.contains('expanded')) {
                    readMoreBtn.textContent = 'Show Less';
                    readMoreBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    readMoreBtn.textContent = 'Read Full Article';
                    content.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
            
            // Lazy loading for images
            const lazyImages = document.querySelectorAll('.lazy-image');
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                });
            });
            
            lazyImages.forEach(img => imageObserver.observe(img));
        });
    </script>
        """

        # Convert Markdown content to HTML
        html_content_from_markdown = markdown.markdown(article['content'])

        # Now, adjust inline image paths within the HTML content AND add lazy loading
        content_with_adjusted_inline_images = adjust_inline_image_paths_in_html(html_content_from_markdown, "../")
        
        header_html = generate_header_html(unique_categories, current_page_type="article")
        category_slug = generate_slug(article['category'])

        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(ARTICLE_TEMPLATE.format(
                title=article['title'],
                author=article['author'],
                publishDate=article['publishDate'],
                dateModified=article['dateModified'],
                content=content_with_adjusted_inline_images, # Use content with adjusted inline image paths
                category=article['category'],
                category_slug=category_slug,
                tags=", ".join(article.get('tags', [])),
                readingTimeMinutes=article.get('readingTimeMinutes', 'N/A'),
                wordCount=article.get('wordCount', 'N/A'),
                factCheckedBy=article.get('factCheckedBy', 'N/A'),
                editorReviewedBy=article.get('editorReviewedBy', 'N/A'),
                metaDescription=meta_description,
                keywords=keywords,
                ogTitle=og_title,
                ogImage=og_image, # Use adjusted ogImage path
                imageAltText=image_alt_text,
                ogUrl=og_url,
                canonicalUrl=canonical_url,
                structuredData=structured_data,
                socialShareText=article.get('socialShareText', ''),
                key_takeaways_html=key_takeaways_html,
                call_to_action_html=call_to_action_html,
                social_hashtags_html=social_hashtags_html,
                javascript_content=javascript_content,
                header_html=header_html
            ))
        print(f"Generated {article_path}")

def generate_category_pages(articles_data, unique_categories):
    """Generates HTML pages for each category with ads."""
    print("Generating category pages...")
    categories_dir = os.path.join(OUTPUT_DIR, "categories")
    create_directory(categories_dir)

    for category in unique_categories:
        category_slug = generate_slug(category)
        category_path = os.path.join(categories_dir, f"{category_slug}.html")
        
        articles_in_category = [
            article for article in articles_data if article['category'] == category
        ]
        # Sort articles by publish date, newest first for category pages
        sorted_articles_in_category = sorted(articles_in_category, key=lambda x: x['publishDate'], reverse=True)

        # Generate articles cards with ads interspersed
        articles_cards = ""
        for i, article in enumerate(sorted_articles_in_category):
            # Adjust link prefix for articles within category pages (needs ../ for images in cards)
            articles_cards += generate_article_card(article, current_page_type="category")
            
            # Insert ad after every 3rd article (positions 3, 6, 9, etc.)
            if (i + 1) % 3 == 0 and (i + 1) < len(sorted_articles_in_category):
                ad_type = "Square" if (i + 1) % 6 == 0 else "Rectangle"
                ad_size = "(300x300)" if ad_type == "Square" else "(300x250)"
                articles_cards += f"""
                    <div class="col-span-1 md:col-span-2 lg:col-span-3">
                        <div class="ad-container">
                            <div class="ad-placeholder">Advertisement - {ad_type} {ad_size}</div>
                        </div>
                    </div>
                """

        header_html = generate_header_html(unique_categories, current_page_type="category")

        with open(category_path, 'w', encoding='utf-8') as f:
            f.write(CATEGORY_TEMPLATE.format(
                category_name=category,
                category_slug=category_slug,
                header_html=header_html,
                articles_cards=articles_cards
            ))
        print(f"Generated {category_path} with {len(sorted_articles_in_category)} articles and integrated ads")

def generate_sitemap(articles_data):
    """Generates XML sitemap for SEO."""
    print("Generating sitemap.xml...")
    sitemap_path = os.path.join(OUTPUT_DIR, "sitemap.xml")
    
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://countrysnews.com/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://countrysnews.com/contact.html</loc>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>https://countrysnews.com/about-us.html</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://countrysnews.com/privacy-policy.html</loc>
        <changefreq>yearly</changefreq>
        <priority>0.3</priority>
    </url>
    <url>
        <loc>https://countrysnews.com/disclaimer.html</loc>
        <changefreq>yearly</changefreq>
        <priority>0.3</priority>
    </url>
"""
    
    for article in articles_data:
        sitemap_content += f"""    <url>
        <loc>https://countrysnews.com/articles/{article['slug']}.html</loc>
        <lastmod>{article['dateModified']}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
"""
    
    sitemap_content += "</urlset>"
    
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write(sitemap_content)
    print(f"Generated {sitemap_path}")

def generate_robots_txt():
    """Generates robots.txt for SEO."""
    print("Generating robots.txt...")
    robots_path = os.path.join(OUTPUT_DIR, "robots.txt")
    
    robots_content = """User-agent: *
Allow: /

Sitemap: https://countrysnews.com/sitemap.xml
"""
    
    with open(robots_path, 'w', encoding='utf-8') as f:
        f.write(robots_content)
    print(f"Generated {robots_path}")

def generate_rss_feed(articles_data):
    """Generates RSS feed for content syndication."""
    print("Generating rss.xml...")
    rss_path = os.path.join(OUTPUT_DIR, "rss.xml")
    
    # Sort articles by publish date, newest first
    sorted_articles = sorted(articles_data, key=lambda x: x['publishDate'], reverse=True)[:20]  # Latest 20 articles
    
    rss_content = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Country's News - Latest Headlines</title>
        <link>https://countrysnews.com</link>
        <description>Get the latest news and in-depth analysis from around the world</description>
        <language>en-us</language>
"""
    
    for article in sorted_articles:
        rss_content += f"""        <item>
            <title>{article['title']}</title>
            <link>https://countrysnews.com/articles/{article['slug']}.html</link>
            <description>{article.get('metaDescription', article['excerpt'])}</description>
            <pubDate>{article['publishDate']}</pubDate>
            <guid>https://countrysnews.com/articles/{article['slug']}.html</guid>
        </item>
"""
    
    rss_content += """    </channel>
</rss>"""
    
    with open(rss_path, 'w', encoding='utf-8') as f:
        f.write(rss_content)
    print(f"Generated {rss_path}")

def generate_contact_page(unique_categories):
    """Generates the contact.html page."""
    print("Generating contact.html...")
    contact_path = os.path.join(OUTPUT_DIR, "contact.html")
    
    header_html = generate_header_html(unique_categories, current_page_type="contact")
    
    try:
        with open(contact_path, 'w', encoding='utf-8') as f:
            # Replace {{header_html}} first, then format with BASE_HTML_HEAD and FOOTER_HTML
            # We need to temporarily replace double braces in CSS to avoid format conflicts
            temp_base_html = BASE_HTML_HEAD.replace('{{', '<<<DOUBLE_BRACE_OPEN>>>').replace('}}', '<<<DOUBLE_BRACE_CLOSE>>>')
            temp_footer_html = FOOTER_HTML.replace('{{', '<<<DOUBLE_BRACE_OPEN>>>').replace('}}', '<<<DOUBLE_BRACE_CLOSE>>>')
            
            template_with_header = CONTACT_TEMPLATE.replace('{{header_html}}', header_html)
            formatted_html = template_with_header.format(BASE_HTML_HEAD=temp_base_html, FOOTER_HTML=temp_footer_html)
            
            # Restore the CSS braces
            final_html = formatted_html.replace('<<<DOUBLE_BRACE_OPEN>>>', '{').replace('<<<DOUBLE_BRACE_CLOSE>>>', '}')
            f.write(final_html)
        print(f"Generated {contact_path}")
    except Exception as e:
        print(f"Error generating contact page: {e}")

def generate_privacy_policy_page(unique_categories):
    """Generates the privacy-policy.html page."""
    print("Generating privacy-policy.html...")
    privacy_path = os.path.join(OUTPUT_DIR, "privacy-policy.html")
    
    header_html = generate_header_html(unique_categories, current_page_type="privacy-policy")
    
    try:
        with open(privacy_path, 'w', encoding='utf-8') as f:
            # Replace {{header_html}} first, then format with BASE_HTML_HEAD and FOOTER_HTML
            # We need to temporarily replace double braces in CSS to avoid format conflicts
            temp_base_html = BASE_HTML_HEAD.replace('{{', '<<<DOUBLE_BRACE_OPEN>>>').replace('}}', '<<<DOUBLE_BRACE_CLOSE>>>')
            temp_footer_html = FOOTER_HTML.replace('{{', '<<<DOUBLE_BRACE_OPEN>>>').replace('}}', '<<<DOUBLE_BRACE_CLOSE>>>')
            
            template_with_header = PRIVACY_POLICY_TEMPLATE.replace('{{header_html}}', header_html)
            formatted_html = template_with_header.format(BASE_HTML_HEAD=temp_base_html, FOOTER_HTML=temp_footer_html)
            
            # Restore the CSS braces
            final_html = formatted_html.replace('<<<DOUBLE_BRACE_OPEN>>>', '{').replace('<<<DOUBLE_BRACE_CLOSE>>>', '}')
            f.write(final_html)
        print(f"Generated {privacy_path}")
    except Exception as e:
        print(f"Error generating privacy policy page: {e}")

def generate_disclaimer_page(unique_categories):
    """Generates the disclaimer.html page."""
    print("Generating disclaimer.html...")
    disclaimer_path = os.path.join(OUTPUT_DIR, "disclaimer.html")
    
    header_html = generate_header_html(unique_categories, current_page_type="disclaimer")
    
    try:
        with open(disclaimer_path, 'w', encoding='utf-8') as f:
            # Replace {{header_html}} first, then format with BASE_HTML_HEAD and FOOTER_HTML
            # We need to temporarily replace double braces in CSS to avoid format conflicts
            temp_base_html = BASE_HTML_HEAD.replace('{{', '<<<DOUBLE_BRACE_OPEN>>>').replace('}}', '<<<DOUBLE_BRACE_CLOSE>>>')
            temp_footer_html = FOOTER_HTML.replace('{{', '<<<DOUBLE_BRACE_OPEN>>>').replace('}}', '<<<DOUBLE_BRACE_CLOSE>>>')
            
            template_with_header = DISCLAIMER_TEMPLATE.replace('{{header_html}}', header_html)
            formatted_html = template_with_header.format(BASE_HTML_HEAD=temp_base_html, FOOTER_HTML=temp_footer_html)
            
            # Restore the CSS braces
            final_html = formatted_html.replace('<<<DOUBLE_BRACE_OPEN>>>', '{').replace('<<<DOUBLE_BRACE_CLOSE>>>', '}')
            f.write(final_html)
        print(f"Generated {disclaimer_path}")
    except Exception as e:
        print(f"Error generating disclaimer page: {e}")

def generate_about_us_page(unique_categories):
    """Generates the about-us.html page."""
    print("Generating about-us.html...")
    about_path = os.path.join(OUTPUT_DIR, "about-us.html")
    
    header_html = generate_header_html(unique_categories, current_page_type="about-us")
    
    try:
        with open(about_path, 'w', encoding='utf-8') as f:
            # Replace {{header_html}} first, then format with BASE_HTML_HEAD and FOOTER_HTML
            # We need to temporarily replace double braces in CSS to avoid format conflicts
            temp_base_html = BASE_HTML_HEAD.replace('{{', '<<<DOUBLE_BRACE_OPEN>>>').replace('}}', '<<<DOUBLE_BRACE_CLOSE>>>')
            temp_footer_html = FOOTER_HTML.replace('{{', '<<<DOUBLE_BRACE_OPEN>>>').replace('}}', '<<<DOUBLE_BRACE_CLOSE>>>')
            
            template_with_header = ABOUT_US_TEMPLATE.replace('{{header_html}}', header_html)
            formatted_html = template_with_header.format(BASE_HTML_HEAD=temp_base_html, FOOTER_HTML=temp_footer_html)
            
            # Restore the CSS braces
            final_html = formatted_html.replace('<<<DOUBLE_BRACE_OPEN>>>', '{').replace('<<<DOUBLE_BRACE_CLOSE>>>', '}')
            f.write(final_html)
        print(f"Generated {about_path}")
    except Exception as e:
        print(f"Error generating about us page: {e}")

def main():
    create_directory(OUTPUT_DIR)
    create_directory(os.path.join(OUTPUT_DIR, "articles"))
    create_directory(os.path.join(OUTPUT_DIR, "categories"))

    articles_data = []
    if os.path.exists(ARTICLES_DATA_FILE):
        try:
            with open(ARTICLES_DATA_FILE, 'r', encoding='utf-8') as f:
                articles_data = json.load(f)
            print(f"Successfully loaded {len(articles_data)} articles from {ARTICLES_DATA_FILE}")
            
            # Validate articles have required fields
            required_fields = ['id', 'title', 'slug', 'content']
            for i, article in enumerate(articles_data):
                for field in required_fields:
                    if not article.get(field):
                        print(f"Warning: Article {i+1} missing required field: {field}")
                        
        except FileNotFoundError:
            print(f"Error: {ARTICLES_DATA_FILE} not found. Please create it with your article data.")
            return
        except json.JSONDecodeError as e:
            print(f"Error: Could not decode JSON from {ARTICLES_DATA_FILE}: {e}")
            return
    else:
        print(f"Error: {ARTICLES_DATA_FILE} not found.")
        return
    
    # --- Logical Change: Assign default category "News" to uncategorized articles ---
    for article in articles_data:
        if not article.get('category') or article['category'].strip() == "":
            article['category'] = DEFAULT_CATEGORY
            print(f"Assigned '{DEFAULT_CATEGORY}' category to article: {article['title']}")
    # --- End of Logical Change ---

    # Get unique categories that actually have articles
    # This ensures we only link to and generate pages for non-empty categories
    unique_categories_with_articles = sorted(list(set(article['category'] for article in articles_data)))

    generate_index_page(articles_data, unique_categories_with_articles)
    generate_article_pages(articles_data, unique_categories_with_articles)
    generate_category_pages(articles_data, unique_categories_with_articles) # Generate category pages
    generate_contact_page(unique_categories_with_articles)  # Generate contact page
    generate_privacy_policy_page(unique_categories_with_articles)  # Generate privacy policy page
    generate_disclaimer_page(unique_categories_with_articles)  # Generate disclaimer page
    generate_about_us_page(unique_categories_with_articles)  # Generate about us page
    generate_sitemap(articles_data)  # Generate sitemap for SEO
    generate_robots_txt()  # Generate robots.txt
    generate_rss_feed(articles_data)  # Generate RSS feed

    print("\nStatic site generation complete! Check the 'dist' directory.")
    print(f"You can open '{os.path.join(OUTPUT_DIR, 'index.html')}' in your browser to view the site.")
    print("\nGenerated files:")
    print("- index.html (homepage with Load More functionality)")
    print("- contact.html (contact page with form)")
    print("- articles-data.json (for AJAX article loading)")
    print("- sitemap.xml (for SEO)")
    print("- robots.txt (for crawlers)")
    print("- rss.xml (RSS feed)")
    print(f"- {len(articles_data)} article pages")
    print(f"- {len(unique_categories_with_articles)} category pages")

if __name__ == "__main__":
    main()
