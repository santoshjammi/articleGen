#!/usr/bin/env python3
"""
Google Trends Diagnostic Tool
Verifies if trends data is current and analyzes the data structure.
"""

import pandas as pd
from trendspy import Trends
import logging
import os
from datetime import datetime, timedelta
import re

def test_current_trends():
    """Test if we're getting current trends data."""
    print("🔍 Google Trends Live Data Diagnostic")
    print("=" * 50)
    
    try:
        trends = Trends()
        
        # Test with US trends
        print("📊 Fetching current US trends...")
        us_trends = trends.trending_now(geo='US')
        
        if not us_trends:
            print("❌ No trends data received!")
            return False
            
        print(f"✅ Received {len(us_trends)} trending topics")
        
        # Convert to DataFrame to analyze structure
        df = pd.DataFrame(us_trends)
        print(f"\n📋 Data Structure:")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Shape: {df.shape}")
        
        # Show sample data
        print(f"\n📝 Sample Data (first 5 items):")
        if '0' in df.columns:
            for i, item in enumerate(df['0'].head(5)):
                print(f"   {i+1}. {item}")
        elif 'title' in df.columns:
            for i, item in enumerate(df['title'].head(5)):
                print(f"   {i+1}. {item}")
        
        # Parse and analyze trending topics
        print(f"\n🔥 Current Trending Analysis:")
        current_topics = []
        
        for item in df.iloc[:, 0].head(10):  # First column, first 10 items
            # Extract topic name from the format: "[US] topic: N searches, ..."
            match = re.match(r'\[US\]\s*(.*?):\s*', str(item))
            if match:
                topic = match.group(1).strip()
                current_topics.append(topic)
                print(f"   • {topic}")
        
        # Check if topics seem current (basic validation)
        print(f"\n⏰ Data Freshness Check:")
        print(f"   Total topics extracted: {len(current_topics)}")
        
        # Look for indicators of current events
        current_indicators = ['2024', '2025', 'today', 'breaking', 'live']
        fresh_indicators = sum(1 for topic in current_topics 
                             for indicator in current_indicators 
                             if indicator.lower() in topic.lower())
        
        if fresh_indicators > 0:
            print(f"   ✅ Found {fresh_indicators} indicators of current events")
        else:
            print(f"   ⚠️  No obvious current event indicators found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing trends: {e}")
        return False

def analyze_output_files():
    """Analyze existing output files to check their currency."""
    print(f"\n📁 Output Files Analysis:")
    print("=" * 30)
    
    output_dir = "output"
    if not os.path.exists(output_dir):
        print("❌ Output directory not found!")
        return
    
    files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
    if not files:
        print("❌ No CSV files found in output directory!")
        return
    
    for filename in files:
        filepath = os.path.join(output_dir, filename)
        
        # Check file timestamp
        modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))
        age = datetime.now() - modified_time
        
        print(f"\n📄 {filename}:")
        print(f"   Last modified: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if age.days == 0:
            print(f"   🟢 Current (updated today)")
        elif age.days <= 1:
            print(f"   🟡 Recent (updated yesterday)")
        else:
            print(f"   🔴 Stale (updated {age.days} days ago)")
        
        # Check file content
        try:
            df = pd.read_csv(filepath)
            print(f"   Records: {len(df)}")
            
            # Show sample current trends
            if len(df) > 0:
                sample_trends = df.iloc[:3, 0].tolist() if '0' in df.columns else df.iloc[:3].iloc[:, 0].tolist()
                print(f"   Sample trends:")
                for i, trend in enumerate(sample_trends, 1):
                    # Clean up trend text for display
                    trend_clean = str(trend).replace('"', '').replace('[US]', '').replace('[IN]', '').replace('[AU]', '').replace('[CA]', '').replace('[GB]', '')
                    if ':' in trend_clean:
                        trend_clean = trend_clean.split(':')[0].strip()
                    print(f"     {i}. {trend_clean}")
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")

def main():
    """Main diagnostic function."""
    print("🚀 Starting Google Trends Diagnostic...")
    
    # Test live data fetching
    live_test_passed = test_current_trends()
    
    # Analyze existing files
    analyze_output_files()
    
    # Summary and recommendations
    print(f"\n📊 DIAGNOSTIC SUMMARY:")
    print("=" * 40)
    
    if live_test_passed:
        print("✅ TRENDS API IS WORKING - Getting live data!")
        print("✅ Your script can fetch current Google Trends")
        print("🔧 Issue is likely in data processing/DataFrame creation")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print("1. Fix the DataFrame creation error in trends.py")
        print("2. Data structure has changed - using column '0' instead of 'title'")
        print("3. Adjust column mappings to match actual data structure")
        print("4. Consider simplifying the data processing logic")
        
    else:
        print("❌ TRENDS API NOT WORKING")
        print("🔧 Need to investigate API connection issues")
        
        print(f"\n💡 TROUBLESHOOTING:")
        print("1. Check internet connection")
        print("2. Verify trendspy-lite library version")
        print("3. Check for API rate limiting")
        print("4. Consider alternative trends libraries")

if __name__ == "__main__":
    main()
