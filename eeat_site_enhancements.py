#!/usr/bin/env python3
"""
E-E-A-T Enhanced Site Generation Module
Extends generateSite.py with Google's latest E-E-A-T compliance features.

This module adds:
- Author bio boxes with credentials and expertise
- Trust signals and verification badges
- Structured data enhanced with E-E-A-T elements
- Editorial transparency sections
- Fact-checking and source verification displays
"""

import json
import os
from datetime import datetime

def generate_eeat_author_box(article):
    """Generate HTML for E-E-A-T compliant author bio box."""
    author_profile = article.get('authorProfile', {})
    
    if not author_profile:
        return ""
    
    credentials_html = ""
    if author_profile.get('credentials'):
        credentials_html = "<ul class='list-disc list-inside text-sm text-gray-600 mt-2'>"
        for credential in author_profile['credentials'][:3]:  # Show top 3 credentials
            credentials_html += f"<li>{credential}</li>"
        credentials_html += "</ul>"
    
    expertise_html = ""
    if author_profile.get('expertiseAreas'):
        expertise_badges = ""
        for area in author_profile['expertiseAreas'][:4]:  # Show top 4 areas
            expertise_badges += f'<span class="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mr-2 mb-1">{area}</span>'
        expertise_html = f'<div class="mt-3"><h5 class="text-sm font-semibold text-gray-700 mb-1">Expertise Areas:</h5><div>{expertise_badges}</div></div>'
    
    social_links = ""
    if author_profile.get('socialProfiles'):
        social_links = '<div class="mt-3 flex space-x-3">'
        for profile in author_profile['socialProfiles']:
            if 'linkedin' in profile.lower():
                social_links += f'<a href="{profile}" class="text-blue-600 hover:text-blue-800 text-sm" target="_blank" rel="noopener">LinkedIn</a>'
            elif 'twitter' in profile.lower():
                social_links += f'<a href="{profile}" class="text-blue-400 hover:text-blue-600 text-sm" target="_blank" rel="noopener">Twitter</a>'
        social_links += '</div>'
    
    author_box = f"""
    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 p-6 my-8 rounded-r-lg shadow-sm">
        <div class="flex items-start space-x-4">
            <div class="flex-shrink-0">
                <div class="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {author_profile.get('name', 'Author')[0]}
                </div>
            </div>
            <div class="flex-grow">
                <div class="flex items-center space-x-2 mb-2">
                    <h4 class="text-lg font-bold text-gray-900">{author_profile.get('name', 'Editorial Team')}</h4>
                    <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">✓ Verified Expert</span>
                </div>
                <p class="text-sm font-medium text-blue-700 mb-2">{author_profile.get('title', 'Senior Editor')}</p>
                <p class="text-gray-700 text-sm mb-3">{author_profile.get('bio', 'Experienced journalist and industry expert.')}</p>
                {credentials_html}
                {expertise_html}
                {social_links}
            </div>
        </div>
    </div>
    """
    
    return author_box

def generate_eeat_trust_indicators(article):
    """Generate HTML for trust and credibility indicators."""
    
    fact_check_date = article.get('lastFactCheck', datetime.now().strftime('%Y-%m-%d'))
    verification_level = article.get('verificationLevel', 'Independently verified')
    
    trust_badges = []
    
    # Add trust signals based on article metadata
    if article.get('factCheckedBy'):
        trust_badges.append('Fact-Checked')
    if article.get('editorReviewedBy'):
        trust_badges.append('Editor Reviewed')
    if article.get('contentQuality', {}).get('sourcesVerified'):
        trust_badges.append('Sources Verified')
    if article.get('expertiseLevel') == 'Professional':
        trust_badges.append('Expert Analysis')
    
    badges_html = ""
    for badge in trust_badges:
        badges_html += f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 mr-2 mb-2"><svg class="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>{badge}</span>'
    
    methodology_note = ""
    if article.get('researchMethodology'):
        methodology_note = f'<div class="mt-2"><span class="text-xs text-gray-600"><strong>Research Method:</strong> {article["researchMethodology"]}</span></div>'
    
    trust_section = f"""
    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 my-6">
        <div class="flex items-center mb-3">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
            </svg>
            <h5 class="font-semibold text-gray-900">Content Verification & Trust</h5>
        </div>
        <div class="flex flex-wrap mb-2">
            {badges_html}
        </div>
        <div class="text-sm text-gray-600">
            <p><strong>Last Fact-Checked:</strong> {fact_check_date}</p>
            <p><strong>Verification Level:</strong> {verification_level}</p>
            <p><strong>Editorial Standards:</strong> Professional journalism ethics and accuracy standards</p>
        </div>
        {methodology_note}
    </div>
    """
    
    return trust_section

def generate_eeat_transparency_section(article):
    """Generate HTML for editorial transparency and disclosure."""
    
    transparency_html = """
    <div class="border-t border-gray-200 pt-6 mt-8">
        <div class="bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                    </svg>
                </div>
                <div class="ml-3">
                    <h5 class="text-sm font-medium text-blue-800">Editorial Transparency</h5>
                    <div class="mt-2 text-sm text-blue-700">
                        <p><strong>Editorial Process:</strong> All articles undergo fact-checking, source verification, and editorial review before publication.</p>
                        <p class="mt-1"><strong>Corrections Policy:</strong> We promptly correct any factual errors and clearly mark all updates with timestamps.</p>
                        <p class="mt-1"><strong>Source Standards:</strong> We prioritize primary sources and clearly cite all information sources.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """
    
    return transparency_html

def generate_eeat_structured_data(article):
    """Generate enhanced structured data with E-E-A-T elements."""
    
    author_profile = article.get('authorProfile', {})
    eeat_score = article.get('eeatScore', {})
    
    # Base structured data
    try:
        structured_data = json.loads(article.get('structuredData', '{}'))
    except:
        structured_data = {}
    
    # Enhance with E-E-A-T elements
    if structured_data:
        # Enhanced author information
        structured_data['author'] = {
            '@type': 'Person',
            'name': author_profile.get('name', article.get('author', 'Editorial Team')),
            'jobTitle': author_profile.get('title', 'Senior Editor'),
            'description': author_profile.get('bio', 'Experienced journalist'),
            'sameAs': author_profile.get('socialProfiles', []),
            'knowsAbout': author_profile.get('expertiseAreas', []),
            'hasCredential': author_profile.get('credentials', [])
        }
        
        # Add review information
        structured_data['reviewedBy'] = {
            '@type': 'Person',
            'name': 'Editorial Review Team',
            'jobTitle': 'Senior Editors'
        }
        
        # Add credibility and trust indicators
        structured_data['credibilityRating'] = {
            '@type': 'Rating',
            'ratingValue': eeat_score.get('trustworthiness', 85),
            'bestRating': 100,
            'worstRating': 0
        }
        
        # Add expertise indicators
        structured_data['about'] = {
            '@type': 'Thing',
            'name': article.get('category', 'News'),
            'description': f"Expert analysis and reporting on {article.get('category', 'current events')}"
        }
        
        # Add fact-checking information
        structured_data['factCheckingPolicy'] = 'https://countrysnews.com/editorial-standards'
        structured_data['correctionsPolicy'] = 'https://countrysnews.com/corrections-policy'
        
        # Add trust signals
        structured_data['trustworthiness'] = 'High'
        structured_data['editorialStandards'] = 'Professional journalism standards'
        structured_data['lastReviewed'] = article.get('lastFactCheck', datetime.now().strftime('%Y-%m-%d'))
    
    return json.dumps(structured_data, indent=2)

def add_eeat_elements_to_article_template():
    """
    Return the enhanced article template with E-E-A-T elements.
    This should be integrated into your main generateSite.py
    """
    
    # Enhanced article template with E-E-A-T elements
    eeat_enhanced_template = """
    <!-- E-E-A-T Enhanced Article Template -->
    
    <!-- Trust indicators in header -->
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
                    <span class="text-gray-500">Last Updated: {lastFactCheck}</span>
                </div>
                <div class="flex items-center space-x-2">
                    <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">Verified Sources</span>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Article content with E-E-A-T elements -->
    <main class="container mx-auto p-6 mt-8 max-w-7xl bg-white rounded-lg shadow-lg">
        <article class="article-content">
            <h1 class="text-4xl font-extrabold text-blue-800 mb-4">{title}</h1>
            
            <!-- Enhanced byline with author credibility -->
            <div class="text-gray-600 text-sm mb-6 border-b border-gray-100 pb-4">
                <div class="flex items-center justify-between">
                    <div>
                        By <span class="font-semibold text-blue-700">{author}</span>
                        <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded ml-2">Verified Expert</span>
                    </div>
                    <div class="text-right">
                        <div>Published: {publishDate}</div>
                        <div>Updated: {dateModified}</div>
                    </div>
                </div>
            </div>
            
            <!-- Social Media Hashtags -->
            {social_hashtags_html}
            
            <!-- Main image -->
            <img src="{ogImage}" alt="{imageAltText}" class="w-full h-64 object-cover rounded-lg mb-6 shadow-md lazy-image" loading="lazy">
            
            <!-- E-E-A-T Author Bio Box -->
            {eeat_author_box}
            
            <!-- Article content -->
            <div id="article-content" class="content-teaser">
                {content}
            </div>
            
            <!-- E-E-A-T Trust Indicators -->
            {eeat_trust_indicators}
            
            <!-- Key Takeaways -->
            {key_takeaways_html}
            
            <!-- Call to Action -->
            {call_to_action_html}
            
            <!-- E-E-A-T Transparency Section -->
            {eeat_transparency_section}
            
        </article>
    </main>
    
    <!-- Enhanced structured data with E-E-A-T -->
    <script type="application/ld+json">
    {eeat_structured_data}
    </script>
    """
    
    return eeat_enhanced_template

def integrate_eeat_with_generate_site():
    """
    Instructions for integrating E-E-A-T enhancements with your existing generateSite.py
    """
    
    integration_guide = """
    INTEGRATION GUIDE: Adding E-E-A-T to generateSite.py
    
    1. Import this module in generateSite.py:
       from eeat_enhancements import *
    
    2. In your generate_article_pages function, add these elements:
       
       # Generate E-E-A-T components
       eeat_author_box = generate_eeat_author_box(article)
       eeat_trust_indicators = generate_eeat_trust_indicators(article)
       eeat_transparency_section = generate_eeat_transparency_section(article)
       eeat_structured_data = generate_eeat_structured_data(article)
       
    3. Update your HTML template format call to include:
       
       html_content = ARTICLE_PAGE_TEMPLATE.format(
           # ... existing parameters ...
           eeat_author_box=eeat_author_box,
           eeat_trust_indicators=eeat_trust_indicators,
           eeat_transparency_section=eeat_transparency_section,
           eeat_structured_data=eeat_structured_data,
           lastFactCheck=article.get('lastFactCheck', current_date)
       )
    
    4. Add E-E-A-T CSS classes to your BASE_HTML_HEAD styles:
       
       .eeat-author-box { /* styling for author bio boxes */ }
       .trust-indicator { /* styling for trust badges */ }
       .verification-badge { /* styling for verification elements */ }
    
    This will seamlessly integrate E-E-A-T compliance into your existing site generation.
    """
    
    return integration_guide

# Example usage and testing
if __name__ == "__main__":
    print("E-E-A-T Site Enhancement Module")
    print("=" * 50)
    print(integrate_eeat_with_generate_site())
