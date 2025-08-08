#!/usr/bin/env python3
"""
Streamlined Article Workflow
Complete workflow for generating articles and updating the website with clean categories.
"""

import subprocess
import sys
import os

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

def main():
    """Complete article generation and website update workflow"""
    
    print("🎯 Starting Complete Article Workflow")
    print("=" * 60)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if we're in a virtual environment
    venv_python = "venv/bin/python" if os.path.exists("venv/bin/python") else "python"
    
    # Step 1: Generate articles (user choice)
    print("\n📝 Options:")
    print("1. Generate from trends (cached data)")
    print("2. Fetch fresh trends + generate articles")
    print("3. Generate from keyword batch")
    print("4. Generate from custom keywords")
    print("5. Check trending keywords only (no generation)")
    print("6. Check trends by region")
    print("7. Fetch fresh trending data only")
    print("8. Skip generation and just update website")
    
    choice = input("\nSelect option (1-8): ").strip()
    
    if choice == "1":
        print("📚 Using cached trending data for faster generation...")
        success = run_command(
            f"{venv_python} super_article_manager.py generate trends --count 5",
            "Generating articles from cached trending topics"
        )
        if not success:
            return
            
    elif choice == "2":
        # Fresh trends + generation
        print("🌐 This will fetch fresh data from internet + generate articles")
        fresh_success = run_command(
            f"{venv_python} fetch_fresh_trends.py",
            "Fetching fresh trending data from Google Trends"
        )
        if fresh_success:
            success = run_command(
                f"{venv_python} super_article_manager.py generate trends --count 5",
                "Generating articles from fresh trending topics"
            )
            if not success:
                return
        else:
            print("⚠️  Fresh data fetch failed, using cached data instead...")
            success = run_command(
                f"{venv_python} super_article_manager.py generate trends --count 5",
                "Generating articles from cached trending topics"
            )
            if not success:
                return
            
    elif choice == "3":
        print("\n📦 Available batches: technology, business, health, sports, entertainment, science")
        batch = input("Enter batch name: ").strip()
        success = run_command(
            f"{venv_python} super_article_manager.py generate batch {batch}",
            f"Generating articles from {batch} batch"
        )
        if not success:
            return
            
    elif choice == "4":
        keywords = input("Enter keywords (comma separated): ").strip()
        if keywords:
            keyword_list = " ".join([f'"{k.strip()}"' for k in keywords.split(",")])
            success = run_command(
                f"{venv_python} super_article_manager.py generate keywords {keyword_list}",
                "Generating articles from custom keywords"
            )
            if not success:
                return
    
    elif choice == "5":
        run_command(
            f"{venv_python} getTrendInput.py",
            "Checking trending keywords across all regions"
        )
        return  # Exit after showing trends
        
    elif choice == "6":
        print("\nAvailable regions: IN (India), US (United States), GB (UK), CA (Canada), AU (Australia)")
        region = input("Enter region code (e.g., IN, US, GB): ").strip().upper()
        count = input("Number of keywords to show (default 15): ").strip() or "15"
        
        run_command(
            f"{venv_python} check_trends.py {region} {count}",
            f"Checking trending keywords for {region}"
        )
        return  # Exit after showing trends
    
    elif choice == "7":
        run_command(
            f"{venv_python} fetch_fresh_trends.py",
            "Fetching fresh trending data from Google Trends"
        )
        return  # Exit after fetching trends
    
    elif choice == "8":
        print("⏭️  Skipping article generation")
    else:
        print("❌ Invalid choice")
        return
    
    # Step 2: Show statistics
    run_command(
        f"{venv_python} super_article_manager.py stats",
        "Showing article statistics"
    )
    
    # Step 3: Generate website
    success = run_command(
        f"{venv_python} generateSite_advanced.py",
        "Generating website with consolidated categories"
    )
    
    if success:
        print("\n🎉 Workflow completed successfully!")
        print("📁 Website files are ready in the 'dist/' directory")
        print("🌐 Categories are automatically consolidated and clean")
        print("\n💡 Note: Category normalization is now built into the article generation process")
        print("   You don't need to run consolidate_categories.py manually anymore!")
    else:
        print("\n❌ Workflow failed during website generation")

if __name__ == "__main__":
    main()
