#!/usr/bin/env python3
"""
Non-Interactive Article Workflow
All the functionality of workflow.py without interactive prompts.
Perfect for automation and scripting.

Usage:
  python workflow_noninteractive.py trends-cached      # Option 1: Fast generation
  python workflow_noninteractive.py trends-fresh       # Option 2: Fresh data + generation  
  python workflow_noninteractive.py batch BATCH_NAME   # Option 3: Batch generation
  python workflow_noninteractive.py keywords "word1,word2,word3"  # Option 4: Custom keywords
  python workflow_noninteractive.py check-trends       # Option 5: Show all trends
  python workflow_noninteractive.py check-region REGION [COUNT]  # Option 6: Regional trends
  python workflow_noninteractive.py fetch-only         # Option 7: Fetch trends only
  python workflow_noninteractive.py site-only          # Option 8: Website only
"""

import subprocess
import sys
import os
import argparse

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print("=" * 60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def get_venv_python():
    """Get the correct Python executable"""
    return "venv/bin/python" if os.path.exists("venv/bin/python") else "python"

def workflow_trends_cached():
    """Option 1: Generate from trends (cached data) - FAST"""
    print("🎯 Starting Fast Trend-Based Generation (Cached Data)")
    print("=" * 60)
    
    venv_python = get_venv_python()
    
    success = run_command(
        f"{venv_python} super_article_manager.py generate trends --count 5",
        "Generating articles from cached trending topics"
    )
    if not success:
        return False
    
    run_command(
        f"{venv_python} super_article_manager.py stats",
        "Showing article statistics"
    )
    
    success = run_command(
        f"{venv_python} generateSite_advanced.py --enhance-articles",
        "Generating website with enhanced articles"
    )
    
    if success:
        print("\n🎉 Fast Workflow completed successfully!")
        print("📁 Website files are ready in the 'dist/' directory")
        print("✨ All articles enhanced with latest features")
    return success

def workflow_trends_fresh():
    """Option 2: Fetch fresh trends + generate articles - COMPREHENSIVE"""
    print("🎯 Starting Fresh Trend-Based Generation")
    print("=" * 60)
    
    venv_python = get_venv_python()
    
    print("🌐 Fetching fresh data from internet + generating articles")
    fresh_success = run_command(
        f"{venv_python} fetch_fresh_trends.py",
        "Fetching fresh trending data from Google Trends"
    )
    
    if fresh_success:
        success = run_command(
            f"{venv_python} super_article_manager.py generate trends --count 5",
            "Generating articles from fresh trending topics"
        )
    else:
        print("⚠️  Fresh data fetch failed, using cached data instead...")
        success = run_command(
            f"{venv_python} super_article_manager.py generate trends --count 5",
            "Generating articles from cached trending topics"
        )
    
    if not success:
        return False
    
    run_command(
        f"{venv_python} super_article_manager.py stats",
        "Showing article statistics"
    )
    
    success = run_command(
        f"{venv_python} generateSite_advanced.py --enhance-articles",
        "Generating website with enhanced articles"
    )
    
    if success:
        print("\n🎉 Fresh Workflow completed successfully!")
        print("📁 Website files are ready in the 'dist/' directory")
        print("✨ All articles enhanced with latest features")
    return success

def workflow_batch(batch_name):
    """Option 3: Generate from keyword batch"""
    print(f"🎯 Starting Batch Generation: {batch_name}")
    print("=" * 60)
    
    available_batches = ["technology", "business", "health", "sports", "entertainment", "science"]
    if batch_name.lower() not in available_batches:
        print(f"❌ Invalid batch name. Available: {', '.join(available_batches)}")
        return False
    
    venv_python = get_venv_python()
    
    success = run_command(
        f"{venv_python} super_article_manager.py generate batch {batch_name}",
        f"Generating articles from {batch_name} batch"
    )
    if not success:
        return False
    
    run_command(
        f"{venv_python} super_article_manager.py stats",
        "Showing article statistics"
    )
    
    success = run_command(
        f"{venv_python} generateSite_advanced.py --enhance-articles",
        "Generating website with enhanced articles"
    )
    
    if success:
        print(f"\n🎉 Batch Workflow ({batch_name}) completed successfully!")
        print("📁 Website files are ready in the 'dist/' directory")
    return success

def workflow_keywords(keywords_str):
    """Option 4: Generate from custom keywords"""
    print("🎯 Starting Custom Keywords Generation")
    print("=" * 60)
    
    keywords = [k.strip() for k in keywords_str.split(',')]
    if not keywords or not keywords[0]:
        print("❌ No keywords provided")
        return False
    
    venv_python = get_venv_python()
    keyword_list = " ".join([f'"{k}"' for k in keywords])
    
    print(f"📝 Generating articles for keywords: {', '.join(keywords)}")
    
    success = run_command(
        f"{venv_python} super_article_manager.py generate keywords {keyword_list}",
        "Generating articles from custom keywords"
    )
    if not success:
        return False
    
    run_command(
        f"{venv_python} super_article_manager.py stats",
        "Showing article statistics"
    )
    
    success = run_command(
        f"{venv_python} generateSite_advanced.py --enhance-articles",
        "Generating website with enhanced articles"
    )
    
    if success:
        print("\n🎉 Custom Keywords Workflow completed successfully!")
        print("📁 Website files are ready in the 'dist/' directory")
    return success

def workflow_check_trends():
    """Option 5: Check trending keywords only (no generation)"""
    print("🎯 Checking Trending Keywords Across All Regions")
    print("=" * 60)
    
    venv_python = get_venv_python()
    run_command(
        f"{venv_python} getTrendInput.py",
        "Checking trending keywords across all regions"
    )
    return True

def workflow_check_region(region, count=15):
    """Option 6: Check trends by region"""
    print(f"🎯 Checking Trending Keywords for {region}")
    print("=" * 60)
    
    available_regions = ["IN", "US", "GB", "CA", "AU"]
    region = region.upper()
    
    if region not in available_regions:
        print(f"❌ Invalid region. Available: {', '.join(available_regions)}")
        return False
    
    venv_python = get_venv_python()
    run_command(
        f"{venv_python} check_trends.py {region} {count}",
        f"Checking trending keywords for {region}"
    )
    return True

def workflow_fetch_only():
    """Option 7: Fetch fresh trending data only"""
    print("🎯 Fetching Fresh Trending Data Only")
    print("=" * 60)
    
    venv_python = get_venv_python()
    run_command(
        f"{venv_python} fetch_fresh_trends.py",
        "Fetching fresh trending data from Google Trends"
    )
    return True

def workflow_site_only():
    """Option 8: Skip generation and just update website"""
    print("🎯 Website Generation Only (No New Articles)")
    print("=" * 60)
    
    venv_python = get_venv_python()
    
    run_command(
        f"{venv_python} super_article_manager.py stats",
        "Showing article statistics"
    )
    
    success = run_command(
        f"{venv_python} generateSite_advanced.py --enhance-articles",
        "Generating website with enhanced articles"
    )
    
    if success:
        print("\n🎉 Website Generation completed successfully!")
        print("📁 Website files are ready in the 'dist/' directory")
        print("✨ All existing articles enhanced with latest features")
    return success

def main():
    parser = argparse.ArgumentParser(
        description="Non-Interactive Article Workflow - All workflow.py functionality without prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python workflow_noninteractive.py trends-cached
  python workflow_noninteractive.py trends-fresh  
  python workflow_noninteractive.py batch technology
  python workflow_noninteractive.py keywords "AI,blockchain,cybersecurity"
  python workflow_noninteractive.py check-trends
  python workflow_noninteractive.py check-region IN 20
  python workflow_noninteractive.py fetch-only
  python workflow_noninteractive.py site-only
        """
    )
    
    parser.add_argument('mode', choices=[
        'trends-cached', 'trends-fresh', 'batch', 'keywords', 
        'check-trends', 'check-region', 'fetch-only', 'site-only'
    ], help='Workflow mode to run')
    
    parser.add_argument('param1', nargs='?', help='Parameter 1 (batch name, keywords, or region)')
    parser.add_argument('param2', nargs='?', type=int, default=15, help='Parameter 2 (count for region)')
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Route to appropriate workflow
    if args.mode == 'trends-cached':
        return workflow_trends_cached()
    elif args.mode == 'trends-fresh':
        return workflow_trends_fresh()
    elif args.mode == 'batch':
        if not args.param1:
            print("❌ Batch name required. Available: technology, business, health, sports, entertainment, science")
            return False
        return workflow_batch(args.param1)
    elif args.mode == 'keywords':
        if not args.param1:
            print("❌ Keywords required (comma-separated)")
            return False
        return workflow_keywords(args.param1)
    elif args.mode == 'check-trends':
        return workflow_check_trends()
    elif args.mode == 'check-region':
        if not args.param1:
            print("❌ Region code required. Available: IN, US, GB, CA, AU")
            return False
        return workflow_check_region(args.param1, args.param2)
    elif args.mode == 'fetch-only':
        return workflow_fetch_only()
    elif args.mode == 'site-only':
        return workflow_site_only()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
