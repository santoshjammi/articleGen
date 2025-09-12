#!/usr/bin/env python3

"""
Static Pages Checker and Validator
Validates all static pages for common issues and broken links
"""

import os
import re
from urllib.parse import urlparse, urljoin

def check_static_pages():
    """Check all static pages for issues"""
    
    print("🔍 Checking static pages for issues...")
    print("=" * 50)
    
    dist_dir = "/Users/kgt/Desktop/Projects/articleGen/dist"
    
    if not os.path.exists(dist_dir):
        print("❌ Dist directory not found. Please generate the site first.")
        return False
    
    # Pages to check
    pages_to_check = [
        ('index.html', 'Home Page'),
        ('about-us.html', 'About Us'),
        ('contact.html', 'Contact'),
        ('privacy-policy.html', 'Privacy Policy'),
        ('disclaimer.html', 'Disclaimer')
    ]
    
    issues_found = []
    
    for filename, page_name in pages_to_check:
        print(f"\\n📄 Checking {page_name} ({filename})...")
        
        file_path = os.path.join(dist_dir, filename)
        if not os.path.exists(file_path):
            issues_found.append(f"❌ {page_name}: File not found")
            continue
        
        page_issues = check_single_page(file_path, page_name)
        if page_issues:
            issues_found.extend(page_issues)
        else:
            print(f"✅ {page_name}: No issues found")
    
    # Check navigation consistency
    nav_issues = check_navigation_consistency(dist_dir)
    if nav_issues:
        issues_found.extend(nav_issues)
    
    # Summary
    print("\\n" + "=" * 50)
    if issues_found:
        print("🚨 Issues Found:")
        for issue in issues_found:
            print(f"  {issue}")
        print(f"\\n📊 Total Issues: {len(issues_found)}")
        return False
    else:
        print("🎉 All static pages are working correctly!")
        print("✅ No issues found")
        return True

def check_single_page(file_path, page_name):
    """Check a single page for issues"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for basic HTML structure
        if not content.strip().startswith('<!DOCTYPE html>'):
            issues.append(f"❌ {page_name}: Missing or incorrect DOCTYPE")
        
        if '<html' not in content:
            issues.append(f"❌ {page_name}: Missing HTML tag")
        
        if '<head>' not in content or '</head>' not in content:
            issues.append(f"❌ {page_name}: Missing or malformed head section")
        
        if '<body>' not in content or '</body>' not in content:
            issues.append(f"❌ {page_name}: Missing or malformed body section")
        
        # Check for essential meta tags
        if '<meta charset=' not in content:
            issues.append(f"⚠️  {page_name}: Missing charset meta tag")
        
        if 'viewport' not in content:
            issues.append(f"⚠️  {page_name}: Missing viewport meta tag")
        
        if '<title>' not in content:
            issues.append(f"⚠️  {page_name}: Missing title tag")
        
        # Check for SEO meta tags
        if 'meta name="description"' not in content:
            issues.append(f"⚠️  {page_name}: Missing meta description")
        
        # Check for accessibility
        if 'alt=' not in content and '<img' in content:
            issues.append(f"⚠️  {page_name}: Images missing alt attributes")
        
        # Check for forms (specific to contact page)
        if 'contact' in file_path.lower():
            if '<form' not in content:
                issues.append(f"❌ Contact page: Missing contact form")
            elif 'name=' not in content or 'email=' not in content:
                issues.append(f"⚠️  Contact page: Form fields missing name attributes")
        
        # Check for broken internal links
        internal_links = re.findall(r'href="([^"]*\.html[^"]*)"', content)
        for link in internal_links:
            if not link.startswith('http'):
                # Remove fragments for file checking
                clean_link = link.split('#')[0]
                if clean_link and not os.path.exists(os.path.join(os.path.dirname(file_path), clean_link)):
                    issues.append(f"🔗 {page_name}: Broken internal link - {link}")
        
        # Check for missing CSS/JS resources
        css_links = re.findall(r'href="([^"]*\.css[^"]*)"', content)
        for css_link in css_links:
            if not css_link.startswith('http') and not css_link.startswith('//'):
                css_path = os.path.join(os.path.dirname(file_path), css_link)
                if not os.path.exists(css_path):
                    issues.append(f"🎨 {page_name}: Missing CSS file - {css_link}")
        
        js_links = re.findall(r'src="([^"]*\.js[^"]*)"', content)
        for js_link in js_links:
            if not js_link.startswith('http') and not js_link.startswith('//'):
                js_path = os.path.join(os.path.dirname(file_path), js_link)
                if not os.path.exists(js_path):
                    issues.append(f"⚡ {page_name}: Missing JS file - {js_link}")
        
        print(f"  ✓ Basic structure check passed")
        print(f"  ✓ Meta tags check completed")
        print(f"  ✓ Internal links check completed")
        
    except Exception as e:
        issues.append(f"❌ {page_name}: Error reading file - {str(e)}")
    
    return issues

def check_navigation_consistency(dist_dir):
    """Check if navigation is consistent across all pages"""
    issues = []
    
    print("\\n🧭 Checking navigation consistency...")
    
    pages = ['index.html', 'about-us.html', 'contact.html', 'privacy-policy.html', 'disclaimer.html']
    nav_patterns = {}
    
    for page in pages:
        file_path = os.path.join(dist_dir, page)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract navigation links
                nav_links = set()
                nav_matches = re.findall(r'<a[^>]+href="([^"]*)"[^>]*>', content)
                for link in nav_matches:
                    if link.endswith('.html') and not link.startswith('http'):
                        nav_links.add(link)
                
                nav_patterns[page] = nav_links
                
            except Exception as e:
                issues.append(f"❌ Navigation check failed for {page}: {str(e)}")
    
    # Check for inconsistencies
    if nav_patterns:
        first_page = list(nav_patterns.keys())[0]
        first_nav = nav_patterns[first_page]
        
        for page, nav_links in nav_patterns.items():
            if page != first_page:
                missing_links = first_nav - nav_links
                extra_links = nav_links - first_nav
                
                if missing_links:
                    issues.append(f"🧭 {page}: Missing navigation links - {', '.join(missing_links)}")
                
                if extra_links:
                    issues.append(f"🧭 {page}: Extra navigation links - {', '.join(extra_links)}")
    
    print("  ✓ Navigation consistency check completed")
    return issues

def check_responsive_design(dist_dir):
    """Check if pages have responsive design elements"""
    issues = []
    
    print("\\n📱 Checking responsive design...")
    
    pages = ['index.html', 'about-us.html', 'contact.html', 'privacy-policy.html', 'disclaimer.html']
    
    for page in pages:
        file_path = os.path.join(dist_dir, page)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for responsive elements
                has_viewport = 'viewport' in content
                has_tailwind = 'tailwindcss' in content
                has_responsive_classes = any(cls in content for cls in ['md:', 'lg:', 'sm:', 'xl:'])
                
                if not has_viewport:
                    issues.append(f"📱 {page}: Missing viewport meta tag for mobile")
                
                if not (has_tailwind or has_responsive_classes):
                    issues.append(f"📱 {page}: No responsive design framework detected")
                
            except Exception as e:
                issues.append(f"❌ Responsive check failed for {page}: {str(e)}")
    
    print("  ✓ Responsive design check completed")
    return issues

def generate_static_pages_report():
    """Generate a comprehensive report of static pages status"""
    
    print("📊 Generating Static Pages Report...")
    print("=" * 50)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'pages_checked': [],
        'issues_found': [],
        'recommendations': []
    }
    
    # Run all checks
    basic_issues = check_static_pages()
    
    # Add recommendations
    recommendations = [
        "✨ Consider adding structured data (JSON-LD) for better SEO",
        "🔒 Implement HTTPS security headers",
        "⚡ Add service worker for offline functionality",
        "📊 Implement analytics tracking",
        "🌐 Add internationalization support",
        "♿ Conduct accessibility audit with WCAG guidelines",
        "🎨 Optimize images for web (WebP format)",
        "📱 Test on various mobile devices"
    ]
    
    report['recommendations'] = recommendations
    
    print("\\n📋 Recommendations for improvement:")
    for rec in recommendations:
        print(f"  {rec}")
    
    return report

if __name__ == "__main__":
    from datetime import datetime
    
    print("🔍 Static Pages Checker & Validator")
    print("=" * 50)
    
    # Run comprehensive check
    all_good = check_static_pages()
    
    # Check responsive design
    responsive_issues = check_responsive_design("/Users/kgt/Desktop/Projects/articleGen/dist")
    if responsive_issues:
        print("\\n📱 Responsive Design Issues:")
        for issue in responsive_issues:
            print(f"  {issue}")
    else:
        print("\\n✅ Responsive design: All pages are mobile-friendly")
    
    # Generate report
    report = generate_static_pages_report()
    
    if all_good and not responsive_issues:
        print("\\n🎉 All static pages are in excellent condition!")
        print("💡 Consider implementing the recommendations for even better performance.")
    else:
        print("\\n🔧 Some issues were found. Please address them for optimal performance.")
