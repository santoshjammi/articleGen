#!/usr/bin/env python3
"""
Image Loading Test - Test specific image URLs directly
"""

import os
import json

def test_specific_images():
    """Create a simple test page to verify image loading"""
    
    print("🧪 Creating Image Loading Test Page")
    print("=" * 40)
    
    # Get first 5 articles to test
    try:
        with open('articles.json', 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("❌ articles.json not found")
        return
    
    test_articles = articles[:5]
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Thumbnail Loading Test</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .test-item { 
            margin: 20px 0; 
            padding: 15px; 
            border: 1px solid #ddd; 
            border-radius: 8px;
        }
        img { 
            max-width: 200px; 
            height: 120px; 
            object-fit: cover;
            border: 2px solid #ccc;
            margin: 10px 0;
        }
        .success { border-color: green; }
        .error { border-color: red; }
        .status { font-weight: bold; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>🧪 Thumbnail Loading Test</h1>
    <p>This page tests if thumbnails load correctly. Each image should appear below:</p>
'''
    
    for i, article in enumerate(test_articles):
        slug = article.get('slug', '')
        title = article.get('title', 'Unknown')
        
        # Different path variations to test
        paths_to_test = [
            f"images/{slug}/thumb.webp",
            f"images/{slug}/main.webp",
            f"dist/images/{slug}/thumb.webp",
            f"dist/images/{slug}/main.webp"
        ]
        
        html_content += f'''
    <div class="test-item">
        <h3>{i+1}. {title[:50]}...</h3>
        <p><strong>Slug:</strong> {slug}</p>
'''
        
        for j, path in enumerate(paths_to_test):
            # Check if file exists
            full_path = path if path.startswith('dist/') else f"dist/{path}"
            exists = "✅ EXISTS" if os.path.exists(full_path) else "❌ MISSING"
            
            html_content += f'''
        <div>
            <p><strong>Test {j+1}:</strong> {path} ({exists})</p>
            <img src="{path}" 
                 alt="Test image {j+1}" 
                 onload="this.parentElement.className='success'; this.nextElementSibling.innerHTML='✅ LOADED'"
                 onerror="this.parentElement.className='error'; this.nextElementSibling.innerHTML='❌ FAILED TO LOAD'"
                 style="display: block;">
            <div class="status">⏳ Loading...</div>
        </div>
'''
        
        html_content += '    </div>'
    
    html_content += '''
    
    <div style="margin-top: 30px; padding: 15px; background: #f0f0f0; border-radius: 8px;">
        <h3>🔍 How to use this test:</h3>
        <ol>
            <li>Open this page in your browser</li>
            <li>Check which images load (green border) vs fail (red border)</li>
            <li>Open browser Developer Tools → Network tab to see failed requests</li>
            <li>Look for 404 errors or other issues</li>
        </ol>
    </div>
    
    <script>
        // Log any console errors
        window.addEventListener('error', function(e) {
            console.error('Image loading error:', e);
        });
        
        // Count loaded vs failed images after 3 seconds
        setTimeout(function() {
            const loaded = document.querySelectorAll('.success').length;
            const failed = document.querySelectorAll('.error').length;
            const total = loaded + failed;
            
            console.log(`📊 Image Loading Results: ${loaded}/${total} loaded successfully`);
            
            // Add results to page
            const results = document.createElement('div');
            results.innerHTML = `
                <div style="position: fixed; top: 10px; right: 10px; background: white; padding: 10px; border: 2px solid #333; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <strong>📊 Results:</strong><br>
                    ✅ Loaded: ${loaded}<br>
                    ❌ Failed: ${failed}<br>
                    📊 Total: ${total}
                </div>
            `;
            document.body.appendChild(results);
        }, 3000);
    </script>
</body>
</html>'''
    
    # Write test file
    test_file = 'dist/thumbnail_test.html'
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Created test page: {test_file}")
    print(f"🌐 Open in browser: http://localhost:8080/thumbnail_test.html")
    print("\n💡 This will help us see:")
    print("   - Which images actually load")
    print("   - Browser network errors")
    print("   - Path issues")

if __name__ == "__main__":
    test_specific_images()
