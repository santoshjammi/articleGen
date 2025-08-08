#!/usr/bin/env python3
"""
Fresh Trends Fetcher
Standalone script for fetching fresh trending data from the internet.
Run this independently before article generation for freshest data.
"""

import subprocess
import sys
import os
from datetime import datetime

def fetch_fresh_trends():
    """Fetch fresh trending data from Google Trends API"""
    print("🌐 Fetching Fresh Trending Data")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run trends.py to fetch fresh data from internet
        print("\n📡 Connecting to Google Trends API...")
        result = subprocess.run(
            ["python", "trends.py"], 
            check=True, 
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        print("\n✅ Fresh trending data fetched successfully!")
        print("\n📊 Updated trend files:")
        
        # Show updated files
        output_dir = "output"
        if os.path.exists(output_dir):
            csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
            for csv_file in sorted(csv_files):
                file_path = os.path.join(output_dir, csv_file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"  📁 {csv_file} (updated: {mod_time.strftime('%H:%M:%S')})")
        
        print(f"\n🎯 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n💡 You can now run super_article_manager.py to generate articles with fresh data!")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fetch fresh trends: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main execution"""
    print("🚀 Fresh Trends Fetcher")
    print("This script fetches the latest trending keywords from Google Trends")
    print("Run this before generating articles for the freshest data\n")
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if trends.py exists
    if not os.path.exists("trends.py"):
        print("❌ trends.py not found in current directory")
        return False
    
    # Fetch fresh trends
    success = fetch_fresh_trends()
    
    if success:
        print("\n🎉 Ready for article generation!")
        print("📝 Next steps:")
        print("  1. Run 'python workflow.py' and choose option 1 (trends)")
        print("  2. Or run 'python super_article_manager.py generate trends --count 5'")
    else:
        print("\n❌ Fresh data fetch failed")
        print("💡 You can still generate articles using cached trend data")
    
    return success

if __name__ == "__main__":
    main()
