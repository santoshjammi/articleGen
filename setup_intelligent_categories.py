#!/usr/bin/env python3
"""
Setup script for intelligent categorization system
"""

import os
import sys

def setup_intelligent_categories():
    """Setup the intelligent categorization system"""
    print("🚀 Setting up Intelligent Category Management System")
    print("=" * 60)
    
    try:
        # Import and initialize
        from intelligent_categories import IntelligentCategoryManager
        
        # Create manager
        manager = IntelligentCategoryManager()
        
        # Save initial configuration
        manager.save_categories()
        
        print("✅ Intelligent categories initialized")
        print(f"📁 Configuration saved to: {manager.categories_file}")
        print(f"📁 Backups will be stored in: {manager.backup_dir}/")
        
        # Generate initial report
        report = manager.generate_category_report()
        print(f"\n📊 System Summary:")
        print(f"   Categories: {report['summary']['total_categories']}")
        print(f"   Subcategories: {report['summary']['total_subcategories']}")
        print(f"   Confidence Threshold: {report['summary']['confidence_threshold']}")
        
        print(f"\n🎯 Next Steps:")
        print("   1. Run: python super_article_manager.py intelligence report")
        print("   2. Run: python super_article_manager.py intelligence trends") 
        print("   3. Run: python super_article_manager.py intelligence learn --reprocess")
        print("   4. Your articles will now use intelligent categorization!")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_intelligent_categories()
    sys.exit(0 if success else 1)
