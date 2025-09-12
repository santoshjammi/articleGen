#!/usr/bin/env python3

"""
Comprehensive Static Pages Diagnostic Tool
Tests all functionality and identifies specific issues
"""

import os
import re
import json
from datetime import datetime

def test_static_pages_functionality():
    """Test all static pages for specific functionality issues"""
    
    print("🔧 Comprehensive Static Pages Diagnostic")
    print("=" * 50)
    
    dist_dir = "/Users/kgt/Desktop/Projects/articleGen/dist"
    
    if not os.path.exists(dist_dir):
        print("❌ Dist directory not found. Please generate the site first.")
        return False
    
    issues = []
    
    # Test each page
    test_results = {
        'contact.html': test_contact_page(dist_dir),
        'about-us.html': test_about_page(dist_dir),
        'privacy-policy.html': test_privacy_page(dist_dir),
        'disclaimer.html': test_disclaimer_page(dist_dir),
        'index.html': test_home_page(dist_dir)
    }
    
    # Collect all issues
    all_issues = []
    for page, result in test_results.items():
        if result['issues']:
            all_issues.extend([f"{page}: {issue}" for issue in result['issues']])
    
    # Summary
    print("\\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if all_issues:
        print("🚨 Issues Found:")
        for issue in all_issues:
            print(f"  • {issue}")
        print(f"\\n📈 Total Issues: {len(all_issues)}")
        
        # Provide specific fixes
        print("\\n🔧 RECOMMENDED FIXES:")
        provide_specific_fixes(all_issues)
        
        return False
    else:
        print("✅ All static pages are functioning correctly!")
        print("🎉 No issues detected!")
        return True

def test_contact_page(dist_dir):
    """Test contact page specifically"""
    print("\\n📞 Testing Contact Page...")
    
    contact_file = os.path.join(dist_dir, 'contact.html')
    issues = []
    
    if not os.path.exists(contact_file):
        issues.append("File missing")
        return {'status': 'error', 'issues': issues}
    
    try:
        with open(contact_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check form structure
        if '<form' not in content:
            issues.append("Contact form missing")
        elif 'id="contactForm"' not in content:
            issues.append("Form missing proper ID")
        
        # Check form fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if f'name="{field}"' not in content:
                issues.append(f"Form field '{field}' missing proper name attribute")
        
        # Check if there are duplicate field names
        name_matches = re.findall(r'name="([^"]*)"', content)
        field_counts = {}
        for field_name in name_matches:
            field_counts[field_name] = field_counts.get(field_name, 0) + 1
        
        for field_name, count in field_counts.items():
            if count > 1 and field_name not in ['viewport', 'description']:
                issues.append(f"Duplicate form field name '{field_name}' ({count} times)")
        
        # Check JavaScript functionality
        if 'addEventListener' not in content:
            issues.append("JavaScript form handling missing")
        
        # Check submit button
        if 'submitBtn' not in content:
            issues.append("Submit button missing proper ID")
        
        # Check contact information
        if 'contact@countrysnews.com' not in content:
            issues.append("Email address missing or incorrect")
            
    except Exception as e:
        issues.append(f"Error reading file: {str(e)}")
    
    status = 'ok' if not issues else 'error'
    print(f"  Status: {'✅ OK' if status == 'ok' else '❌ Issues found'}")
    
    if issues:
        for issue in issues:
            print(f"    • {issue}")
    
    return {'status': status, 'issues': issues}

def test_about_page(dist_dir):
    """Test about page specifically"""
    print("\\n📖 Testing About Us Page...")
    
    about_file = os.path.join(dist_dir, 'about-us.html')
    issues = []
    
    if not os.path.exists(about_file):
        issues.append("File missing")
        return {'status': 'error', 'issues': issues}
    
    try:
        with open(about_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check essential content
        required_content = [
            "About Country's News",
            "Our Mission",
            "verified journalism",
            "expert analysis"
        ]
        
        for content_item in required_content:
            if content_item not in content:
                issues.append(f"Missing content: '{content_item}'")
        
        # Check for proper structure
        if '<h1' not in content:
            issues.append("Missing main heading")
        
        if '<h2' not in content:
            issues.append("Missing section headings")
            
    except Exception as e:
        issues.append(f"Error reading file: {str(e)}")
    
    status = 'ok' if not issues else 'error'
    print(f"  Status: {'✅ OK' if status == 'ok' else '❌ Issues found'}")
    
    if issues:
        for issue in issues:
            print(f"    • {issue}")
    
    return {'status': status, 'issues': issues}

def test_privacy_page(dist_dir):
    """Test privacy policy page"""
    print("\\n🔒 Testing Privacy Policy Page...")
    
    privacy_file = os.path.join(dist_dir, 'privacy-policy.html')
    issues = []
    
    if not os.path.exists(privacy_file):
        issues.append("File missing")
        return {'status': 'error', 'issues': issues}
    
    try:
        with open(privacy_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check essential privacy content
        required_content = [
            "Privacy Policy",
            "Information We Collect",
            "How We Use Information",
            "Contact Us"
        ]
        
        for content_item in required_content:
            if content_item not in content:
                issues.append(f"Missing content: '{content_item}'")
                
    except Exception as e:
        issues.append(f"Error reading file: {str(e)}")
    
    status = 'ok' if not issues else 'error'
    print(f"  Status: {'✅ OK' if status == 'ok' else '❌ Issues found'}")
    
    if issues:
        for issue in issues:
            print(f"    • {issue}")
    
    return {'status': status, 'issues': issues}

def test_disclaimer_page(dist_dir):
    """Test disclaimer page"""
    print("\\n⚖️ Testing Disclaimer Page...")
    
    disclaimer_file = os.path.join(dist_dir, 'disclaimer.html')
    issues = []
    
    if not os.path.exists(disclaimer_file):
        issues.append("File missing")
        return {'status': 'error', 'issues': issues}
    
    try:
        with open(disclaimer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check essential disclaimer content
        required_content = [
            "Disclaimer",
            "General Information",
            "Editorial Standards"
        ]
        
        for content_item in required_content:
            if content_item not in content:
                issues.append(f"Missing content: '{content_item}'")
                
    except Exception as e:
        issues.append(f"Error reading file: {str(e)}")
    
    status = 'ok' if not issues else 'error'
    print(f"  Status: {'✅ OK' if status == 'ok' else '❌ Issues found'}")
    
    if issues:
        for issue in issues:
            print(f"    • {issue}")
    
    return {'status': status, 'issues': issues}

def test_home_page(dist_dir):
    """Test home page"""
    print("\\n🏠 Testing Home Page...")
    
    home_file = os.path.join(dist_dir, 'index.html')
    issues = []
    
    if not os.path.exists(home_file):
        issues.append("File missing")
        return {'status': 'error', 'issues': issues}
    
    try:
        with open(home_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check navigation links to static pages
        required_links = [
            'href="about-us.html"',
            'href="contact.html"',
            'href="privacy-policy.html"'
        ]
        
        for link in required_links:
            if link not in content:
                issues.append(f"Missing navigation link: {link}")
                
    except Exception as e:
        issues.append(f"Error reading file: {str(e)}")
    
    status = 'ok' if not issues else 'error'
    print(f"  Status: {'✅ OK' if status == 'ok' else '❌ Issues found'}")
    
    if issues:
        for issue in issues:
            print(f"    • {issue}")
    
    return {'status': status, 'issues': issues}

def provide_specific_fixes(issues):
    """Provide specific fixes for identified issues"""
    
    fixes = []
    
    for issue in issues:
        if "Form field 'subject' missing proper name attribute" in issue:
            fixes.append("🔧 Fix contact form subject field: Change name attribute from 'name' to 'subject'")
        
        if "Duplicate form field name" in issue:
            fixes.append("🔧 Fix duplicate form field names: Ensure each input has a unique name attribute")
        
        if "JavaScript form handling missing" in issue:
            fixes.append("🔧 Add JavaScript functionality to contact form for validation and submission")
        
        if "Missing navigation link" in issue:
            fixes.append("🔧 Add missing navigation links to header/footer sections")
        
        if "File missing" in issue:
            fixes.append("🔧 Regenerate site using: python generateSite_advanced.py")
    
    # Remove duplicates
    fixes = list(set(fixes))
    
    for fix in fixes:
        print(f"  {fix}")
    
    if not fixes:
        print("  🤷 No specific automated fixes available. Manual review required.")

def quick_fix_contact_form():
    """Quick fix for contact form issues"""
    print("\\n🚀 Attempting Quick Fix for Contact Form...")
    
    contact_file = "/Users/kgt/Desktop/Projects/articleGen/dist/contact.html"
    
    if not os.path.exists(contact_file):
        print("❌ Contact file not found")
        return False
    
    try:
        with open(contact_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix subject field name attribute
        # Look for the subject field pattern and fix it
        pattern = r'(<label[^>]*>Subject</label>\s*<input[^>]+name=")[^"]*(")'
        replacement = r'\1subject\2'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            
            with open(contact_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Fixed contact form subject field")
            return True
        else:
            print("⚠️  Subject field pattern not found for fixing")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing contact form: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Starting Comprehensive Static Pages Diagnostic...")
    
    # Run full diagnostic
    all_good = test_static_pages_functionality()
    
    # If issues found, attempt quick fixes
    if not all_good:
        print("\\n🔨 Attempting Quick Fixes...")
        quick_fix_contact_form()
        
        print("\\n🔄 Re-running diagnostic after fixes...")
        test_static_pages_functionality()
    
    print("\\n✨ Diagnostic complete!")
    print("\\n💡 If issues persist, try:")
    print("   1. python generateSite_advanced.py  # Regenerate site")
    print("   2. python fix_static_pages.py      # Apply comprehensive fixes")
    print("   3. Check browser console for JavaScript errors")
