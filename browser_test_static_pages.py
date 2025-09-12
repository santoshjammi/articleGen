#!/usr/bin/env python3

"""
Test Static Pages in Browser
Creates a simple test page to verify functionality
"""

import os
import webbrowser
import time

def test_contact_form_in_browser():
    """Test contact form functionality in browser"""
    
    print("🌐 Testing Contact Form in Browser...")
    
    # Create a test HTML page
    test_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Form Test</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-2xl mx-auto">
        <h1 class="text-3xl font-bold mb-8">Contact Form Test</h1>
        
        <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
            <h2 class="text-xl font-semibold mb-4">Quick Tests</h2>
            <div class="space-y-4">
                <div class="flex items-center space-x-2">
                    <button onclick="testContactPage()" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Test Contact Page
                    </button>
                    <span id="contactTest" class="text-gray-500">Not tested</span>
                </div>
                
                <div class="flex items-center space-x-2">
                    <button onclick="testAboutPage()" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                        Test About Page
                    </button>
                    <span id="aboutTest" class="text-gray-500">Not tested</span>
                </div>
                
                <div class="flex items-center space-x-2">
                    <button onclick="testFormValidation()" class="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600">
                        Test Form Validation
                    </button>
                    <span id="formTest" class="text-gray-500">Not tested</span>
                </div>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow-lg p-6">
            <h2 class="text-xl font-semibold mb-4">Test Results</h2>
            <div id="results" class="space-y-2 text-sm">
                <p>Click the test buttons above to verify functionality.</p>
            </div>
        </div>
    </div>
    
    <script>
        function testContactPage() {
            const resultDiv = document.getElementById('results');
            const testSpan = document.getElementById('contactTest');
            
            try {
                // Test if contact page is accessible
                fetch('contact.html')
                    .then(response => {
                        if (response.ok) {
                            testSpan.textContent = '✅ Accessible';
                            testSpan.className = 'text-green-600';
                            addResult('✅ Contact page is accessible');
                            return response.text();
                        } else {
                            throw new Error('Page not found');
                        }
                    })
                    .then(html => {
                        // Check if form exists
                        if (html.includes('contactForm')) {
                            addResult('✅ Contact form found');
                        } else {
                            addResult('❌ Contact form missing');
                        }
                        
                        // Check if form fields exist
                        const fields = ['name="name"', 'name="email"', 'name="subject"', 'name="message"'];
                        fields.forEach(field => {
                            if (html.includes(field)) {
                                addResult(`✅ Form field found: ${field}`);
                            } else {
                                addResult(`❌ Form field missing: ${field}`);
                            }
                        });
                    })
                    .catch(error => {
                        testSpan.textContent = '❌ Error';
                        testSpan.className = 'text-red-600';
                        addResult('❌ Contact page test failed: ' + error.message);
                    });
            } catch (error) {
                testSpan.textContent = '❌ Error';
                testSpan.className = 'text-red-600';
                addResult('❌ Contact page test error: ' + error.message);
            }
        }
        
        function testAboutPage() {
            const resultDiv = document.getElementById('results');
            const testSpan = document.getElementById('aboutTest');
            
            try {
                fetch('about-us.html')
                    .then(response => {
                        if (response.ok) {
                            testSpan.textContent = '✅ Accessible';
                            testSpan.className = 'text-green-600';
                            addResult('✅ About page is accessible');
                            return response.text();
                        } else {
                            throw new Error('Page not found');
                        }
                    })
                    .then(html => {
                        // Check for key content
                        const content = [
                            "About Country's News",
                            "Our Mission",
                            "verified journalism"
                        ];
                        
                        content.forEach(item => {
                            if (html.includes(item)) {
                                addResult(`✅ Content found: "${item}"`);
                            } else {
                                addResult(`❌ Content missing: "${item}"`);
                            }
                        });
                    })
                    .catch(error => {
                        testSpan.textContent = '❌ Error';
                        testSpan.className = 'text-red-600';
                        addResult('❌ About page test failed: ' + error.message);
                    });
            } catch (error) {
                testSpan.textContent = '❌ Error';
                testSpan.className = 'text-red-600';
                addResult('❌ About page test error: ' + error.message);
            }
        }
        
        function testFormValidation() {
            const testSpan = document.getElementById('formTest');
            
            // Open contact page in new window to test form
            const contactWindow = window.open('contact.html', '_blank');
            
            setTimeout(() => {
                try {
                    if (contactWindow && !contactWindow.closed) {
                        testSpan.textContent = '✅ Form opened';
                        testSpan.className = 'text-green-600';
                        addResult('✅ Contact form opened in new window');
                        addResult('👉 Please test the form validation manually in the new window');
                    } else {
                        testSpan.textContent = '❌ Failed to open';
                        testSpan.className = 'text-red-600';
                        addResult('❌ Failed to open contact form');
                    }
                } catch (error) {
                    testSpan.textContent = '❌ Error';
                    testSpan.className = 'text-red-600';
                    addResult('❌ Form test error: ' + error.message);
                }
            }, 1000);
        }
        
        function addResult(message) {
            const resultDiv = document.getElementById('results');
            const p = document.createElement('p');
            p.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
            resultDiv.appendChild(p);
        }
    </script>
</body>
</html>'''
    
    # Write test file
    test_file = "/Users/kgt/Desktop/Projects/articleGen/dist/test-static-pages.html"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    print(f"✅ Created test page: {test_file}")
    print("🌐 Test page created at: http://localhost:8080/test-static-pages.html")
    print("👉 Start your local server and visit the test page to verify functionality")
    
    return test_file

if __name__ == "__main__":
    print("🧪 Static Pages Browser Test Creator")
    print("=" * 40)
    
    test_file = test_contact_form_in_browser()
    
    print("\\n📋 Instructions:")
    print("1. Start local server: cd dist && python3 -m http.server 8080")
    print("2. Visit: http://localhost:8080/test-static-pages.html")
    print("3. Click the test buttons to verify functionality")
    print("4. Check the contact form manually")
    print("\\n🔍 This will help identify specific issues you're experiencing.")
