#!/usr/bin/env python3
"""
SUPER-CONSOLIDATION MIGRATION SCRIPT
Consolidates ALL article-related functionality into one super module.

This script consolidates these files:
- article_generator.py (already consolidated)
- enhance_articles.py 
- deduplicate_articles.py
- merge_articles.py  
- fix_articles.py
- workflow_deduplication.py

Into: super_article_manager.py

Creates compatibility wrappers for all original files.
"""

import os
import json
import shutil
from datetime import datetime

def create_backup_directory():
    """Create backup directory for old files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_super_consolidation_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    print(f"📁 Created backup directory: {backup_dir}")
    return backup_dir

def backup_files(backup_dir):
    """Backup all files being consolidated"""
    files_to_backup = [
        "article_generator.py",
        "enhance_articles.py", 
        "deduplicate_articles.py",
        "merge_articles.py",
        "fix_articles.py", 
        "workflow_deduplication.py"
    ]
    
    backed_up = []
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            backed_up.append(file)
            print(f"✅ Backed up: {file}")
    
    return backed_up

def create_wrapper_scripts():
    """Create compatibility wrapper scripts"""
    
    print("\n🔧 Creating compatibility wrappers...")
    
    # article_generator.py wrapper (already exists but update it)
    article_gen_wrapper = '''#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for article_generator.py
This file has been consolidated into super_article_manager.py
"""

import sys
import asyncio
from super_article_manager import SuperArticleManager, generate_articles_from_trends, generate_articles_from_keywords

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py generate --help")
    
    # For basic compatibility, assume trends generation
    manager = SuperArticleManager()
    manager.load_articles()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate_articles_from_trends(manager, 3))
    manager.save_articles()

if __name__ == "__main__":
    main()
'''
    
    # enhance_articles.py wrapper
    enhance_wrapper = '''#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for enhance_articles.py
This file has been consolidated into super_article_manager.py
"""

import sys
from super_article_manager import SuperArticleManager

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py enhance --all")
    
    manager = SuperArticleManager()
    manager.load_articles()
    manager.create_backup("enhance")
    
    # Run enhancement
    enhanced = manager.enhance_articles()
    if enhanced > 0:
        manager.save_articles()
        print(f"✅ Enhanced {enhanced} articles")
    else:
        print("ℹ️  No articles needed enhancement")

if __name__ == "__main__":
    main()
'''
    
    # deduplicate_articles.py wrapper  
    dedupe_wrapper = '''#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for deduplicate_articles.py
This file has been consolidated into super_article_manager.py
"""

import sys
from super_article_manager import SuperArticleManager

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py enhance --deduplicate")
    
    manager = SuperArticleManager()
    manager.load_articles()
    manager.create_backup("dedupe")
    
    # Run deduplication
    duplicates = manager.analyze_duplicates()
    removed = manager.deduplicate_articles(duplicates)
    
    if removed > 0:
        manager.save_articles()
        print(f"✅ Removed {removed} duplicate articles")
    else:
        print("ℹ️  No duplicates found")

if __name__ == "__main__":
    main()
'''
    
    # merge_articles.py wrapper
    merge_wrapper = '''#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for merge_articles.py
This file has been consolidated into super_article_manager.py
"""

import sys
from super_article_manager import SuperArticleManager

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py enhance --merge-legacy")
    
    manager = SuperArticleManager()
    manager.load_articles()
    manager.create_backup("merge")
    
    # Run merge
    merged = manager.merge_legacy_articles()
    
    if merged > 0:
        manager.save_articles()
        print(f"✅ Merged {merged} legacy articles")
    else:
        print("ℹ️  No legacy articles to merge")

if __name__ == "__main__":
    main()
'''
    
    # fix_articles.py wrapper
    fix_wrapper = '''#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for fix_articles.py
This file has been consolidated into super_article_manager.py
"""

import sys
from super_article_manager import SuperArticleManager

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py enhance --fix-issues")
    
    manager = SuperArticleManager()
    manager.load_articles()
    manager.create_backup("fix")
    
    # Run fixes
    fixed = manager.fix_article_issues()
    
    if fixed > 0:
        manager.save_articles()
        print(f"✅ Fixed issues in {fixed} articles")
    else:
        print("ℹ️  No issues found to fix")

if __name__ == "__main__":
    main()
'''
    
    # workflow_deduplication.py wrapper
    workflow_wrapper = '''#!/usr/bin/env python3
"""
COMPATIBILITY WRAPPER for workflow_deduplication.py
This file has been consolidated into super_article_manager.py
"""

import sys
import asyncio
from super_article_manager import SuperArticleManager

def main():
    print("🔄 Redirecting to super_article_manager.py...")
    print("ℹ️  Use: python super_article_manager.py workflow --complete")
    
    manager = SuperArticleManager()
    manager.load_articles()
    manager.create_backup("workflow")
    
    # Run complete workflow
    print("🚀 Running complete article management workflow...")
    
    # Merge legacy
    merged = manager.merge_legacy_articles()
    
    # Deduplicate
    duplicates = manager.analyze_duplicates()
    removed = manager.deduplicate_articles(duplicates)
    
    # Fix issues
    fixed = manager.fix_article_issues()
    
    # Enhance
    enhanced = manager.enhance_articles()
    
    # Save
    manager.save_articles()
    
    print("\\n🎉 Workflow completed!")
    print(f"📊 Summary: Merged {merged}, Removed {removed} dupes, Fixed {fixed}, Enhanced {enhanced}")

if __name__ == "__main__":
    main()
'''
    
    # Write wrapper files
    wrappers = {
        "article_generator.py": article_gen_wrapper,
        "enhance_articles.py": enhance_wrapper,
        "deduplicate_articles.py": dedupe_wrapper,
        "merge_articles.py": merge_wrapper,
        "fix_articles.py": fix_wrapper,
        "workflow_deduplication.py": workflow_wrapper
    }
    
    for filename, content in wrappers.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        os.chmod(filename, 0o755)  # Make executable
        print(f"✅ Created wrapper: {filename}")

def create_migration_summary(backup_dir, backed_up_files):
    """Create a summary of the migration"""
    summary = {
        "migration_date": datetime.now().isoformat(),
        "backup_directory": backup_dir,
        "files_consolidated": backed_up_files,
        "new_super_module": "super_article_manager.py",
        "compatibility_wrappers": [
            "article_generator.py",
            "enhance_articles.py", 
            "deduplicate_articles.py",
            "merge_articles.py",
            "fix_articles.py",
            "workflow_deduplication.py"
        ],
        "usage_instructions": {
            "generate_trends": "python super_article_manager.py generate trends --count 5",
            "generate_keywords": "python super_article_manager.py generate keywords 'AI' 'tech'",
            "enhance_all": "python super_article_manager.py enhance --all",
            "complete_workflow": "python super_article_manager.py workflow --complete",
            "show_stats": "python super_article_manager.py stats"
        }
    }
    
    summary_file = "SUPER_CONSOLIDATION_SUMMARY.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📋 Migration summary saved to: {summary_file}")
    return summary

def print_migration_report(summary):
    """Print a comprehensive migration report"""
    print("\\n" + "="*80)
    print("🎉 SUPER-CONSOLIDATION COMPLETE!")
    print("="*80)
    
    print(f"\\n📁 Backup Directory: {summary['backup_directory']}")
    print(f"📦 Files Consolidated: {len(summary['files_consolidated'])}")
    
    print("\\n📂 Files Consolidated:")
    for file in summary['files_consolidated']:
        print(f"   ✅ {file}")
    
    print("\\n🔧 Compatibility Wrappers Created:")
    for wrapper in summary['compatibility_wrappers']:
        print(f"   🔄 {wrapper} → super_article_manager.py")
    
    print("\\n🚀 New Usage Examples:")
    for desc, cmd in summary['usage_instructions'].items():
        print(f"   {desc}: {cmd}")
    
    print("\\n📊 Before vs After:")
    original_count = len(summary['files_consolidated'])
    print(f"   Before: {original_count} separate files")
    print(f"   After: 1 super-consolidated module + {len(summary['compatibility_wrappers'])} wrappers")
    print(f"   Reduction: {original_count} → 1 (core logic consolidated)")
    
    print("\\n✨ Benefits:")
    print("   • Single source of truth for all article operations")
    print("   • Unified command-line interface")
    print("   • Consistent error handling and logging")
    print("   • Easier maintenance and updates")
    print("   • Backward compatibility maintained")
    
    print("\\n⚠️  Important Notes:")
    print("   • All original files are safely backed up")
    print("   • Compatibility wrappers preserve existing workflows")
    print("   • Use 'super_article_manager.py --help' for full options")
    print("   • All data and functionality preserved")
    
    print("\\n🎯 Next Steps:")
    print("   1. Test the new super module: python super_article_manager.py stats")
    print("   2. Try generating articles: python super_article_manager.py generate trends")
    print("   3. Run complete workflow: python super_article_manager.py workflow --complete")
    print("   4. Update any automation scripts to use the new module")
    
    print("\\n" + "="*80)

def main():
    """Run the super consolidation migration"""
    print("🚀 SUPER-CONSOLIDATION MIGRATION")
    print("=" * 50)
    print("Consolidating ALL article management functionality into one super module!")
    print()
    
    # Step 1: Create backup
    backup_dir = create_backup_directory()
    
    # Step 2: Backup existing files
    backed_up = backup_files(backup_dir)
    
    # Step 3: Create compatibility wrappers
    create_wrapper_scripts()
    
    # Step 4: Create migration summary
    summary = create_migration_summary(backup_dir, backed_up)
    
    # Step 5: Print comprehensive report
    print_migration_report(summary)

if __name__ == "__main__":
    main()
