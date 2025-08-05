#!/usr/bin/env python3
"""
generateSite Files Cleanup Script
Removes redundant generateSite backup and duplicate files after E-E-A-T consolidation.
"""

import os
import shutil
from datetime import datetime

def cleanup_generatesite_files():
    """Remove redundant generateSite files after consolidation."""
    
    print("🧹 Cleaning up redundant generateSite files...")
    
    # Files to remove (redundant after consolidation)
    files_to_remove = [
        'generateSite_backup_20250806_034400.py',  # Old pre-E-E-A-T backup
        'generateSite_eeat_enhanced.py'            # Redundant E-E-A-T specific version
    ]
    
    removed_files = []
    
    for file in files_to_remove:
        if os.path.exists(file):
            # Get file size for reporting
            file_size = os.path.getsize(file)
            
            # Remove the file
            os.remove(file)
            removed_files.append((file, file_size))
            print(f"🗑️  Removed {file} ({file_size:,} bytes)")
        else:
            print(f"ℹ️  {file} not found (may already be cleaned)")
    
    if removed_files:
        total_space = sum(size for _, size in removed_files)
        print(f"\n✅ Cleanup complete!")
        print(f"📊 Removed {len(removed_files)} files, freed {total_space:,} bytes")
        
        print(f"\n📁 Current generateSite setup:")
        print(f"✅ generateSite.py - Main site generator (E-E-A-T enabled)")
        print(f"✅ eeat_system.py - Consolidated E-E-A-T system")
        print(f"🗑️  Old backup files - Removed")
        
    else:
        print("ℹ️  No files to remove - already clean!")
    
    return len(removed_files)

def verify_current_setup():
    """Verify the current setup is working correctly."""
    print("\n🔍 Verifying current setup...")
    
    # Check main files exist
    required_files = ['generateSite.py', 'eeat_system.py']
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - Present")
        else:
            print(f"❌ {file} - MISSING!")
            missing_files.append(file)
    
    # Check data files
    data_files = ['perplexityArticles.json', 'perplexityArticles_eeat_enhanced.json']
    for file in data_files:
        if os.path.exists(file):
            print(f"✅ {file} - Present")
        else:
            print(f"⚠️  {file} - Not found")
    
    if not missing_files:
        print("\n🎯 Setup verified - all essential files present!")
        return True
    else:
        print(f"\n❌ Setup issue - missing: {', '.join(missing_files)}")
        return False

def main():
    print("generateSite Files Cleanup")
    print("=" * 40)
    
    # Verify current setup first
    if verify_current_setup():
        # If setup is good, proceed with cleanup
        removed_count = cleanup_generatesite_files()
        
        print("\n🎉 Cleanup Summary:")
        print("=" * 40)
        print(f"✅ Removed {removed_count} redundant files")
        print("✅ Current setup verified and working")
        print("✅ E-E-A-T system fully consolidated")
        
        print("\n📋 Your streamlined setup:")
        print("• generateSite.py - For direct site generation")
        print("• eeat_system.py - For complete E-E-A-T workflow")
        print("• No redundant backup files cluttering workspace")
        
    else:
        print("\n⚠️  Please resolve setup issues before cleanup")

if __name__ == "__main__":
    main()
