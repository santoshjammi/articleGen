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
            # Old format - just size (this is the actual case)
            original_files[remote_path] = {
                'size': size_or_info,
                'mtime': None,  # No time info available from remote
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
            
            # Only check for size changes (no time comparison since remote doesn't have mtime)
            size_changed = current_info['size'] != original_info.get('size', 0)
            
            # Only mark as changed if size actually changed
            if size_changed:
                changes['changed_files'].append({
                    'remote_path': remote_path,
                    'local_path': current_info['path'],
                    'size': current_info['size'],
                    'reason': f"size: {original_info.get('size', 0)} → {current_info['size']}"
                })
            else:
                changes['unchanged_files'].append(remote_path)
    
    # Check for files that exist in original but not in current (deleted locally)
    for remote_path in original_files.keys():
        if remote_path not in current_state:
            print(f"⚠️  File deleted locally: {remote_path} (exists on remote)")
    
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

def load_article_sync_metadata():
    """Load article metadata from the site generator's differential sync file"""
    article_sync_path = os.path.join(LOCAL_DIRECTORY, ".differential_sync.json")
    
    if not os.path.exists(article_sync_path):
        return None
    
    try:
        with open(article_sync_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Could not load article sync metadata: {e}")
        return None

def enhance_with_article_intelligence(changes):
    """Enhance sync decisions with article-level intelligence"""
    article_metadata = load_article_sync_metadata()
    
    if not article_metadata:
        print("📊 No article metadata available - using file-level analysis only")
        return changes
    
    article_changes = article_metadata.get('article_changes', {})
    files_to_sync_priority = set(article_metadata.get('files_to_sync', []))
    
    print("🧠 Enhancing with article-level intelligence...")
    print(f"   📄 Article changes: {article_changes.get('changed', 0)} changed, {article_changes.get('new', 0)} new")
    print(f"   📋 Priority files from articles: {len(files_to_sync_priority)}")
    
    # Mark article-driven files as high priority
    for file_info in changes['new_files'] + changes['changed_files']:
        remote_path = file_info['remote_path']
        
        if remote_path in files_to_sync_priority:
            file_info['sync_priority'] = 'high'
            file_info['sync_reason'] = file_info.get('sync_reason', 'file_change') + '+article_driven'
        else:
            file_info['sync_priority'] = 'normal'
    
    # Add article-driven files that might not have been caught by file analysis
    existing_files = {f['remote_path'] for f in changes['new_files'] + changes['changed_files']}
    
    for priority_file in files_to_sync_priority:
        if priority_file not in existing_files:
            # Check if file exists locally
            local_path = os.path.join(LOCAL_DIRECTORY, priority_file)
            if os.path.exists(local_path):
                file_info = get_file_info(local_path)
                changes['changed_files'].append({
                    'remote_path': priority_file,
                    'local_path': local_path,
                    'size': file_info['size'],
                    'mtime': file_info['mtime'],
                    'reason': 'article_driven_priority',
                    'sync_priority': 'high',
                    'sync_reason': 'article_metadata_driven'
                })
    
    # Update summary with enhanced information
    changes['enhancement_info'] = {
        'article_driven_files': len(files_to_sync_priority),
        'high_priority_files': len([f for f in changes['new_files'] + changes['changed_files'] 
                                  if f.get('sync_priority') == 'high']),
        'sync_strategy': 'intelligent_article_driven',
        'article_metadata_timestamp': article_metadata.get('timestamp', ''),
        'article_changes_summary': article_changes
    }
    
    # Update summary counts (may have increased due to article-driven additions)
    changes['summary'].update({
        'changed_files': len(changes['changed_files']),
        'files_to_upload': len(changes['new_files']) + len(changes['changed_files']),
        'enhancement_applied': True
    })
    
    return changes

def get_sync_recommendations():
    """Get intelligent sync recommendations based on current state"""
    differential_path = os.path.join(LOCAL_DIRECTORY, ".differential_sync.json")
    
    recommendations = {
        'should_sync': False,
        'estimated_time': '< 1 minute',
        'priority_files': 0,
        'total_files': 0,
        'reasons': []
    }
    
    if os.path.exists(differential_path):
        try:
            with open(differential_path, 'r', encoding='utf-8') as f:
                sync_data = json.load(f)
            
            files_to_sync = sync_data.get('files_to_sync', [])
            article_changes = sync_data.get('article_changes', {})
            
            changed_count = article_changes.get('changed', 0)
            new_count = article_changes.get('new', 0)
            
            if changed_count > 0 or new_count > 0:
                recommendations['should_sync'] = True
                recommendations['total_files'] = len(files_to_sync)
                recommendations['priority_files'] = changed_count + new_count
                recommendations['reasons'].append(f"{changed_count} articles changed, {new_count} new articles")
                
                # Estimate sync time based on file count
                if recommendations['total_files'] < 10:
                    recommendations['estimated_time'] = '< 30 seconds'
                elif recommendations['total_files'] < 50:
                    recommendations['estimated_time'] = '1-2 minutes'
                else:
                    recommendations['estimated_time'] = '2-5 minutes'
            
        except Exception as e:
            print(f"⚠️  Could not analyze sync recommendations: {e}")
    
    return recommendations

def main():
    """Main differential analysis function"""
    if not LOCAL_DIRECTORY:
        print("❌ Error: LOCAL_DIRECTORY not set in environment")
        return False
    
    start_time = time.time()
    
    print("🚀 INTELLIGENT DIFFERENTIAL SYNC ANALYSIS")
    print("=" * 60)
    
    # Get sync recommendations first
    recommendations = get_sync_recommendations()
    if recommendations['should_sync']:
        print("🎯 SYNC RECOMMENDATIONS:")
        print(f"   📊 Should sync: {recommendations['should_sync']}")
        print(f"   📁 Estimated files: {recommendations['total_files']}")
        print(f"   ⚡ Priority files: {recommendations['priority_files']}")
        print(f"   ⏱️  Estimated time: {recommendations['estimated_time']}")
        print(f"   💡 Reasons: {', '.join(recommendations['reasons'])}")
        print()
    
    print(f"📍 Local Directory: {LOCAL_DIRECTORY}")
    print(f"📍 Manifest Path: {MANIFEST_FILE_PATH}")
    print(f"📍 Differential Path: {DIFFERENTIAL_MANIFEST_PATH}")
    
    # Scan current state
    current_state, current_directories = scan_current_files(LOCAL_DIRECTORY)
    print(f"📊 Current state: {len(current_state)} files in {len(current_directories)} directories")
    
    # Load original manifest
    original_manifest = load_original_manifest()
    print(f"📊 Original manifest: {len(original_manifest)} files")
    
    # Show sample comparison for debugging
    if original_manifest and current_state:
        sample_file = list(current_state.keys())[0]
        if sample_file in original_manifest:
            current_info = current_state[sample_file]
            original_size = original_manifest[sample_file]
            print(f"🔍 Sample comparison - {sample_file}:")
            print(f"   Current: size={current_info['size']}, mtime={current_info['mtime']}")
            print(f"   Original: size={original_size}")
            print(f"   Size match: {current_info['size'] == original_size}")
    
    # Find changes
    changes = compare_and_find_changes(original_manifest, current_state, current_directories)
    
    # Enhance with article-level intelligence
    changes = enhance_with_article_intelligence(changes)
    
    # Display enhanced results
    summary = changes['summary']
    enhancement_info = changes.get('enhancement_info', {})
    
    print()
    print("📊 ENHANCED DIFFERENTIAL ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"📁 Total files scanned: {summary.get('total_files_scanned', len(current_state))}")
    print(f"🆕 New files: {summary.get('new_files', len(changes.get('new_files', [])))}")
    print(f"🔄 Changed files: {summary.get('changed_files', len(changes.get('changed_files', [])))}")
    print(f"✅ Unchanged files: {summary.get('unchanged_files', 0)}")
    print(f"📂 Directories: {summary.get('new_directories', len(changes.get('new_directories', [])))}")
    print(f"⚡ Files to upload: {summary.get('files_to_upload', 0)}")
    
    if enhancement_info:
        print()
        print("🧠 ARTICLE INTELLIGENCE ENHANCEMENT:")
        print(f"   📄 Article-driven files: {enhancement_info.get('article_driven_files', 0)}")
        print(f"   🎯 High priority files: {enhancement_info.get('high_priority_files', 0)}")
        print(f"   🔧 Sync strategy: {enhancement_info.get('sync_strategy', 'file_based')}")
        article_summary = enhancement_info.get('article_changes_summary', {})
        if article_summary:
            print(f"   📊 Articles: {article_summary.get('changed', 0)} changed, {article_summary.get('new', 0)} new")
    
    print("=" * 60)
    
    if summary.get('files_to_upload', 0) == 0:
        print("🎉 No changes detected - sync will be instant!")
    else:
        print(f"🚀 Ready for intelligent differential sync of {summary.get('files_to_upload', 0)} files")
        if enhancement_info.get('high_priority_files', 0) > 0:
            print(f"   🎯 {enhancement_info['high_priority_files']} high-priority files (article-driven)")
    
    # Save differential manifest
    if save_differential_manifest(changes):
        analysis_time = time.time() - start_time
        print(f"✅ Enhanced differential analysis completed in {analysis_time:.2f} seconds")
        return True
    else:
        print("❌ Differential analysis failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
