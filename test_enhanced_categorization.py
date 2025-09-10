#!/usr/bin/env python3
"""
Test script for the enhanced category mapping system
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced functions
from super_article_manager import normalize_category_enhanced, categorize_by_subcategory, SUBCATEGORY_MAPPING

def test_enhanced_categorization():
    """Test the enhanced categorization system"""
    
    print("🧪 Testing Enhanced Categorization System")
    print("=" * 50)
    
    # Test cases based on the issues we found
    test_cases = [
        {
            'title': 'Agile User Story Best Practices',
            'category': 'World',
            'subcategory': 'Agile Methodologies',
            'expected': 'Technology'
        },
        {
            'title': 'Digital Marketing Strategy 2025',
            'category': 'World', 
            'subcategory': 'Digital Strategy',
            'expected': 'Business'
        },
        {
            'title': 'Project Management Tools Guide',
            'category': 'Business',
            'subcategory': 'Project Management', 
            'expected': 'Business'
        },
        {
            'title': 'Join the Indian Army',
            'category': 'World',
            'subcategory': 'Recruitment',
            'expected': 'Business'
        },
        {
            'title': 'Weather Update',
            'category': 'World',
            'subcategory': 'Weather',
            'expected': 'World'  # Should stay as World
        }
    ]
    
    print(f"Running {len(test_cases)} test cases...\n")
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['title']}")
        print(f"  Input: Category='{test['category']}', SubCategory='{test['subcategory']}'")
        
        # Test the enhanced categorization
        result = normalize_category_enhanced(test['category'], test['subcategory'])
        
        print(f"  Result: '{result}'")
        print(f"  Expected: '{test['expected']}'")
        
        if result == test['expected']:
            print("  ✅ PASSED")
            passed += 1
        else:
            print("  ❌ FAILED")
            failed += 1
        
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Enhanced categorization is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the categorization logic.")
    
    print("\n🔍 Available subcategory mappings:")
    print(f"Technology subcategories: {len([k for k, v in SUBCATEGORY_MAPPING.items() if v == 'Technology'])}")
    print(f"Business subcategories: {len([k for k, v in SUBCATEGORY_MAPPING.items() if v == 'Business'])}")
    
    return failed == 0

if __name__ == "__main__":
    test_enhanced_categorization()
