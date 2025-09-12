#!/usr/bin/env python3

"""
Final Static Pages Fix
Comprehensive fix for all potential static page issues
"""

import os
import re
import json
from datetime import datetime

def final_static_pages_fix():
    """Apply comprehensive fixes to all static pages"""
    
    print("🔧 Final Static Pages Comprehensive Fix")
    print("=" * 50)
    
    dist_dir = "/Users/kgt/Desktop/Projects/articleGen/dist"
    
    if not os.path.exists(dist_dir):
        print("❌ Dist directory not found. Please generate the site first.")
        return False
    
    fixes_applied = []
    
    # Fix contact page
    contact_fixes = fix_contact_page_final(dist_dir)
    fixes_applied.extend(contact_fixes)
    
    # Fix about page
    about_fixes = fix_about_page_final(dist_dir)
    fixes_applied.extend(about_fixes)
    
    # Fix navigation consistency
    nav_fixes = fix_navigation_links(dist_dir)
    fixes_applied.extend(nav_fixes)
    
    # Summary
    print("\\n" + "=" * 50)
    print("📊 FIXES APPLIED")
    print("=" * 50)
    
    if fixes_applied:
        for fix in fixes_applied:
            print(f"✅ {fix}")
        print(f"\\n🎉 Total fixes applied: {len(fixes_applied)}")
    else:
        print("ℹ️  No fixes needed - all pages are already working correctly!")
    
    return True

def fix_contact_page_final(dist_dir):
    """Final comprehensive fix for contact page"""
    
    print("📞 Fixing Contact Page...")
    
    contact_file = os.path.join(dist_dir, 'contact.html')
    fixes = []
    
    if not os.path.exists(contact_file):
        print("  ❌ Contact page not found")
        return fixes
    
    try:
        with open(contact_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Ensure subject field has correct name attribute
        if 'name="name"' in content and 'Subject</label>' in content:
            # Find the subject input and fix its name attribute
            pattern = r'(<label[^>]*>Subject</label>\s*<input[^>]+name=")[^"]*(")'
            if re.search(pattern, content):
                content = re.sub(pattern, r'\\1subject\\2', content)
                fixes.append("Fixed subject field name attribute")
        
        # Fix 2: Ensure form has proper IDs
        if 'id="contactForm"' not in content and '<form' in content:
            content = content.replace('<form ', '<form id="contactForm" ')
            fixes.append("Added form ID")
        
        # Fix 3: Ensure submit button has proper ID
        if 'id="submitBtn"' not in content and 'type="submit"' in content:
            content = content.replace('type="submit"', 'type="submit" id="submitBtn"')
            fixes.append("Added submit button ID")
        
        # Fix 4: Ensure all form fields have required attribute
        for field in ['name', 'email', 'subject', 'message']:
            if f'name="{field}"' in content and 'required' not in content:
                pattern = f'(name="{field}"[^>]*)'
                replacement = r'\\1 required'
                content = re.sub(pattern, replacement, content)
        
        # Fix 5: Add form validation JavaScript if missing
        if 'addEventListener' not in content:
            js_script = '''
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.getElementById('contactForm');
        if (form) {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                
                // Simple validation
                const name = form.querySelector('input[name="name"]').value;
                const email = form.querySelector('input[name="email"]').value;
                const subject = form.querySelector('input[name="subject"]').value;
                const message = form.querySelector('textarea[name="message"]').value;
                
                if (!name || !email || !subject || !message) {
                    alert('Please fill in all fields.');
                    return;
                }
                
                // Show success message
                alert('Thank you for your message! We\\'ll get back to you soon.');
                
                // Create mailto link
                const mailtoLink = `mailto:contact@countrysnews.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(`Name: ${name}\\nEmail: ${email}\\n\\nMessage:\\n${message}`)}`;
                window.location.href = mailtoLink;
                
                // Reset form
                form.reset();
            });
        }
    });
    </script>'''
            
            content = content.replace('</body>', js_script + '\\n</body>')
            fixes.append("Added form validation JavaScript")
        
        # Fix 6: Update contact information
        if '+1 (555) 123-4567' in content:
            content = content.replace('+1 (555) 123-4567', '+91 (011) 1234-5678')
            fixes.append("Updated phone number to Indian format")
        
        if '123 News Street<br>Media City, MC 12345' in content:
            content = content.replace('123 News Street<br>Media City, MC 12345', 'New Delhi, India<br>PIN: 110001')
            fixes.append("Updated address to Indian location")
        
        # Save changes if any were made
        if content != original_content:
            with open(contact_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Applied {len(fixes)} fixes to contact page")
        else:
            print("  ℹ️  Contact page already optimal")
        
    except Exception as e:
        print(f"  ❌ Error fixing contact page: {e}")
    
    return fixes

def fix_about_page_final(dist_dir):
    """Final comprehensive fix for about page"""
    
    print("📖 Fixing About Page...")
    
    about_file = os.path.join(dist_dir, 'about-us.html')
    fixes = []
    
    if not os.path.exists(about_file):
        print("  ❌ About page not found")
        return fixes
    
    try:
        with open(about_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix 1: Ensure proper heading structure
        if '<h1' not in content:
            # Add main heading if missing
            content = content.replace('<main', '<main>\\n<h1 class="text-4xl font-bold text-center mb-8">About Country\\'s News</h1>\\n<div')
            fixes.append("Added main heading")
        
        # Save changes if any were made
        if content != original_content:
            with open(about_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Applied {len(fixes)} fixes to about page")
        else:
            print("  ℹ️  About page already optimal")
        
    except Exception as e:
        print(f"  ❌ Error fixing about page: {e}")
    
    return fixes

def fix_navigation_links(dist_dir):
    """Fix any broken navigation links"""
    
    print("🧭 Fixing Navigation Links...")
    
    fixes = []
    static_pages = ['index.html', 'about-us.html', 'contact.html', 'privacy-policy.html', 'disclaimer.html']
    
    for page in static_pages:
        page_file = os.path.join(dist_dir, page)
        if os.path.exists(page_file):
            try:
                with open(page_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix incorrect navigation links
                incorrect_links = [
                    ('href="categories/contact.html"', 'href="contact.html"'),
                    ('href="categories/about-us.html"', 'href="about-us.html"'),
                    ('href="categories/privacy-policy.html"', 'href="privacy-policy.html"'),
                    ('href="categories/disclaimer.html"', 'href="disclaimer.html"')
                ]
                
                for incorrect, correct in incorrect_links:
                    if incorrect in content:
                        content = content.replace(incorrect, correct)
                        fixes.append(f"Fixed navigation link in {page}: {incorrect} → {correct}")
                
                # Save changes if any were made
                if content != original_content:
                    with open(page_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                
            except Exception as e:
                print(f"  ❌ Error fixing navigation in {page}: {e}")
    
    if not fixes:
        print("  ℹ️  All navigation links are already correct")
    
    return fixes

if __name__ == "__main__":
    print("🚀 Starting Final Static Pages Fix...")
    
    success = final_static_pages_fix()
    
    if success:
        print("\\n🎉 Final fix complete!")
        print("\\n📋 Next steps:")
        print("1. Start local server: cd dist && python3 -m http.server 8080")
        print("2. Test pages:")
        print("   • http://localhost:8080/contact.html")
        print("   • http://localhost:8080/about-us.html") 
        print("   • http://localhost:8080/test-static-pages.html")
        print("\\n✨ All static pages should now be working correctly!")
    else:
        print("\\n❌ Fix failed. Please check the error messages above.")
