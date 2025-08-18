#!/usr/bin/env python3
"""
Smart Differential Manifest Generator
Compares current local state with original manifest to identify only changes
Detects: new files, changed files, new directories, size changes, time changes
"""

import os
import json
import time
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LOCAL_DIRECTORY = os.getenv("LOCAL_DIRECTORY")
MANIFEST_FILE_PATH = os.path.join(LOCAL_DIRECTORY, ".sync_manifest.json")
DIFFERENTIAL_MANIFEST_PATH = os.path.join(LOCAL_DIRECTORY, ".differential_sync.json")

def get_file_info(file_path):
    """Get comprehensive file information for comparison"""
    try:
        stat = os.stat(file_path)
        return {
            'size': stat.st_size,
            'mtime': stat.st_mtime,
            'exists': True,
            'path': file_path
        }
    except (OSError, IOError):
        return {
            'size': 0,
            'mtime': 0,
            'exists': False,
            'path': file_path
        }

def scan_current_files(local_dir):
    """Scan current local directory state with comprehensive file info"""
    current_state = {}
    directories = set()
    
    print(f"🔍 Scanning current state of {local_dir}...")
    
    for root, dirs, files in os.walk(local_dir):
        # Track directories
        for dir_name in dirs:
            local_subdir = os.path.join(root, dir_name)
            relative_dir = os.path.relpath(local_subdir, local_dir)
            directories.add(relative_dir.replace("\\", "/"))
        
        # Track files with comprehensive info
        for file_name in files:
            local_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(local_path, local_dir)
            remote_path = relative_path.replace("\\", "/")
            
            file_info = get_file_info(local_path)
            current_state[remote_path] = file_info
    
    return current_state, directories

def load_original_manifest():
    """Load the original manifest from Step 0"""
    if os.path.exists(MANIFEST_FILE_PATH):
        with open(MANIFEST_FILE_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("⚠️ Warning: Original manifest corrupted")
                return {}
    print("⚠️ Warning: No original manifest found")
    return {}

def compare_and_find_changes(original_manifest, current_state, current_directories):
    """Smart comparison to find all types of changes"""
    changes = {
        'new_files': [],
        'changed_files': [],
        'new_directories': list(current_directories),  # All current dirs (will create if not exist)
        'unchanged_files': [],
        'summary': {}
    }
    
    print("🧠 Performing smart differential analysis...")
    
    # Convert original manifest to comparable format
    original_files = {}
    for remote_path, size_or_info in original_manifest.items():
        if isinstance(size_or_info, dict):
            original_files[remote_path] = size_or_info
        else:
            # Old format - just size
            original_files[remote_path] = {
                'size': size_or_info,
                'mtime': 0,
                'exists': True
            }
    
    # Compare current state with original
    for remote_path, current_info in current_state.items():
        if remote_path not in original_files:
            # Completely new file
            changes['new_files'].append({
                'remote_path': remote_path,
                'local_path': current_info['path'],
                'size': current_info['size'],
                'reason': 'new_file'
            })
        else:
            original_info = original_files[remote_path]
            
            # Check for changes (size, mtime, existence)
            size_changed = current_info['size'] != original_info.get('size', 0)
            time_changed = current_info['mtime'] > original_info.get('mtime', 0)
            
            if size_changed or time_changed:
                reason = []
                if size_changed:
                    reason.append(f"size: {original_info.get('size', 0)} → {current_info['size']}")
                if time_changed:
                    reason.append(f"newer: {datetime.fromtimestamp(current_info['mtime']).strftime('%H:%M:%S')}")
                
                changes['changed_files'].append({
                    'remote_path': remote_path,
                    'local_path': current_info['path'],
                    'size': current_info['size'],
                    'reason': ', '.join(reason)
                })
            else:
                changes['unchanged_files'].append(remote_path)
    
    # Generate summary
    changes['summary'] = {
        'total_files_scanned': len(current_state),
        'new_files': len(changes['new_files']),
        'changed_files': len(changes['changed_files']),
        'unchanged_files': len(changes['unchanged_files']),
        'new_directories': len(changes['new_directories']),
        'files_to_upload': len(changes['new_files']) + len(changes['changed_files']),
        'scan_timestamp': time.time()
    }
    
    return changes

def save_differential_manifest(changes):
    """Save the differential manifest for sync scripts"""
    try:
        with open(DIFFERENTIAL_MANIFEST_PATH, 'w') as f:
            json.dump(changes, f, indent=2)
        
        summary = changes['summary']
        print("📊 DIFFERENTIAL ANALYSIS COMPLETE")
        print("=" * 50)
        print(f"📁 Total files scanned: {summary['total_files_scanned']}")
        print(f"🆕 New files: {summary['new_files']}")
        print(f"🔄 Changed files: {summary['changed_files']}")
        print(f"✅ Unchanged files: {summary['unchanged_files']}")
        print(f"📂 Directories: {summary['new_directories']}")
        print(f"⚡ Files to upload: {summary['files_to_upload']}")
        print("=" * 50)
        
        if summary['files_to_upload'] == 0:
            print("🎉 No changes detected - sync will be instant!")
        else:
            print(f"🚀 Ready for differential sync of {summary['files_to_upload']} files")
        
        return True
    except Exception as e:
        print(f"❌ Error saving differential manifest: {e}")
        return False

def main():
    """Main differential analysis function"""
    if not LOCAL_DIRECTORY:
        print("❌ Error: LOCAL_DIRECTORY not set in environment")
        return False
    
    start_time = time.time()
    print("🧠 Starting Smart Differential Analysis...")
    print(f"📍 Local Directory: {LOCAL_DIRECTORY}")
    
    # Scan current state
    current_state, current_directories = scan_current_files(LOCAL_DIRECTORY)
    
    # Load original manifest
    original_manifest = load_original_manifest()
    
    # Find changes
    changes = compare_and_find_changes(original_manifest, current_state, current_directories)
    
    # Save differential manifest
    if save_differential_manifest(changes):
        analysis_time = time.time() - start_time
        print(f"✅ Differential analysis completed in {analysis_time:.2f} seconds")
        return True
    else:
        print("❌ Differential analysis failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
