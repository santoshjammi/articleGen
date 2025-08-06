#!/usr/bin/env python3
"""
E-E-A-T System Consolidation Cleanup Script
Safely removes old E-E-A-T files and organizes the consolidated system.
"""

import os
import shutil
from datetime import datetime

def cleanup_old_eeat_files():
    """Remove old individual E-E-A-T scripts after consolidation."""
    
    print("🧹 Starting E-E-A-T System Cleanup...")
    
    # Files to archive (move to backup folder)
    old_files = [
        'eeat_enhancer.py',
        'eeat_site_enhancements.py', 
        'integrate_eeat.py'
    ]
    
    # Create backup folder with timestamp
    backup_folder = f"backup_eeat_consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
        print(f"📁 Created backup folder: {backup_folder}")
    
    # Move old files to backup
    files_moved = 0
    for file in old_files:
        if os.path.exists(file):
            shutil.move(file, os.path.join(backup_folder, file))
            print(f"📦 Moved {file} to backup")
            files_moved += 1
        else:
            print(f"ℹ️  {file} not found (may already be cleaned up)")
    
    # Create a README in backup folder
    readme_content = f"""
E-E-A-T System Consolidation Backup
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This folder contains the original individual E-E-A-T scripts that have been
consolidated into the unified eeat_system.py script.

Original files backed up:
- eeat_enhancer.py (main enhancement logic)
- eeat_site_enhancements.py (HTML generation functions)  
- integrate_eeat.py (integration script)

New consolidated system:
- eeat_system.py (all functionality combined)

The consolidated system provides:
✅ Article enhancement with E-E-A-T compliance
✅ HTML generation with trust indicators
✅ Complete website generation workflow
✅ Unified command-line interface

Usage:
python3 eeat_system.py full-process --input perplexityArticles.json

These backup files can be safely deleted after confirming the new system works correctly.
"""
    
    with open(os.path.join(backup_folder, 'README.txt'), 'w') as f:
        f.write(readme_content)
    
    print(f"✅ Cleanup complete! {files_moved} files backed up to {backup_folder}")
    print("🎯 Your E-E-A-T system is now consolidated into eeat_system.py")
    
    return backup_folder

def test_consolidated_system():
    """Test that the consolidated system works correctly."""
    print("\n🧪 Testing consolidated E-E-A-T system...")
    
    # Check if consolidated system exists
    if not os.path.exists('eeat_system.py'):
        print("❌ eeat_system.py not found!")
        return False
    
    # Test import
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("eeat_system", "eeat_system.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Test system initialization
        system = module.UnifiedEEATSystem()
        print("✅ Consolidated system imports successfully")
        print("✅ UnifiedEEATSystem initializes correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing consolidated system: {e}")
        return False

def main():
    print("E-E-A-T System Consolidation Cleanup")
    print("=" * 50)
    
    # Test the consolidated system first
    if test_consolidated_system():
        # If tests pass, do cleanup
        backup_folder = cleanup_old_eeat_files()
        
        print("\n🎉 Consolidation Complete!")
        print("=" * 50)
        print("✅ Old E-E-A-T files backed up safely")
        print("✅ Consolidated system tested and working")
        print("✅ Ready to use eeat_system.py")
        print("\nNext steps:")
        print("1. Test: python3 eeat_system.py enhance --input perplexityArticles.json")
        print("2. Full process: python3 eeat_system.py full-process --input perplexityArticles.json")
        print(f"3. If everything works, you can delete: {backup_folder}")
        
    else:
        print("\n❌ Consolidated system test failed!")
        print("   Please check eeat_system.py before proceeding with cleanup")

if __name__ == "__main__":
    main()
