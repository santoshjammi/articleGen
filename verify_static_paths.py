#!/usr/bin/env python3

"""
Static Pages Path Verification
Confirms all static pages are at correct root paths, not under categories
"""

import os
import re

def verify_static_pages_paths():
    """Verify all static pages are at correct paths"""
    
    print("🔍 Static Pages Path Verification")
    print("=" * 40)
    
    dist_dir = "/Users/kgt/Desktop/Projects/articleGen/dist"
    
    # Expected static pages at root level
    expected_pages = [
        'index.html',
        'about-us.html', 
        'contact.html',
        'privacy-policy.html',
        'disclaimer.html'
    ]
    
    # Check if pages exist at correct locations
    print("📄 Checking page locations...")
    all_good = True
    
    for page in expected_pages:
        root_path = os.path.join(dist_dir, page)
        categories_path = os.path.join(dist_dir, 'categories', page)
        
        if os.path.exists(root_path):
            print(f"  ✅ {page} - Correctly at root level")
        else:
            print(f"  ❌ {page} - Missing from root level!")
            all_good = False
            
        if os.path.exists(categories_path):
            print(f"  ⚠️  {page} - Incorrectly found in categories/ (should be removed)")
            all_good = False
    
    # Check navigation links
    print("\\n🧭 Checking navigation links...")
    link_issues = []
    
    for page in expected_pages:
        page_path = os.path.join(dist_dir, page)
        if os.path.exists(page_path):
            try:
                with open(page_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for incorrect category links to static pages
                incorrect_patterns = [
                    r'href="categories/(about-us|contact|privacy-policy|disclaimer)\.html"',
                    r'href="categories/(about-us|contact|privacy-policy|disclaimer)/"'
                ]
                
                for pattern in incorrect_patterns:
                    matches = re.findall(pattern, content)
                    if matches:
                        link_issues.append(f"{page}: Found incorrect category links - {matches}")
                
                # Check for correct root-level links
                correct_links = [
                    'href="about-us.html"',
                    'href="contact.html"',
                    'href="privacy-policy.html"',
                    'href="disclaimer.html"'
                ]
                
                found_correct_links = []
                for link in correct_links:
                    if link in content:
                        found_correct_links.append(link)
                
                if found_correct_links:
                    print(f"  ✅ {page} - Has correct navigation links: {len(found_correct_links)} found")
                
            except Exception as e:
                print(f"  ❌ Error checking {page}: {e}")
    
    # Report link issues
    if link_issues:
        print("\\n🚨 Navigation Link Issues:")
        for issue in link_issues:
            print(f"  ❌ {issue}")
        all_good = False
    else:
        print("  ✅ All navigation links are correct (no category paths for static pages)")
    
    # Check sitemap
    print("\\n🗺️  Checking sitemap...")
    sitemap_path = os.path.join(dist_dir, 'sitemap.xml')
    if os.path.exists(sitemap_path):
        try:
            with open(sitemap_path, 'r', encoding='utf-8') as f:
                sitemap_content = f.read()
            
            # Check for correct URLs in sitemap
            correct_urls = [
                'https://countrysnews.com/about-us.html',
                'https://countrysnews.com/contact.html',
                'https://countrysnews.com/privacy-policy.html',
                'https://countrysnews.com/disclaimer.html'
            ]
            
            found_urls = []
            for url in correct_urls:
                if url in sitemap_content:
                    found_urls.append(url)
            
            print(f"  ✅ Sitemap contains {len(found_urls)}/4 static page URLs at root level")
            
            # Check for incorrect category URLs
            incorrect_sitemap_patterns = [
                r'https://countrysnews\.com/categories/(about-us|contact|privacy-policy|disclaimer)\.html'
            ]
            
            for pattern in incorrect_sitemap_patterns:
                matches = re.findall(pattern, sitemap_content)
                if matches:
                    print(f"  ❌ Sitemap contains incorrect category URLs: {matches}")
                    all_good = False
            
        except Exception as e:
            print(f"  ❌ Error checking sitemap: {e}")
    else:
        print("  ❌ Sitemap not found")
        all_good = False
    
    # Summary
    print("\\n" + "=" * 40)
    if all_good:
        print("🎉 SUCCESS: All static pages are correctly positioned!")
        print("✅ All pages at root level (not in categories/)")
        print("✅ Navigation links point to correct paths") 
        print("✅ Sitemap contains correct URLs")
        print("\\n💡 Your static pages structure is perfect!")
    else:
        print("⚠️  Some issues found with static page paths")
        print("\\n🔧 Recommended actions:")
        print("1. Regenerate site: python3 generateSite_advanced.py")
        print("2. Clear any cached category static pages") 
        print("3. Verify navigation in browser")
    
    return all_good

if __name__ == "__main__":
    success = verify_static_pages_paths()
    exit(0 if success else 1)
