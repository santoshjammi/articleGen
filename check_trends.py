#!/usr/bin/env python3
"""
Regional Trend Checker
Check trending keywords for specific regions without generating articles.
"""

import csv
import re
import os
from collections import defaultdict

REGION_MAPPING = {
    'IN': 'india_daily_trends.csv',
    'US': 'united_states_daily_trends.csv', 
    'GB': 'united_kingdom_daily_trends.csv',
    'UK': 'united_kingdom_daily_trends.csv',
    'CA': 'canada_daily_trends.csv',
    'AU': 'australia_daily_trends.csv'
}

REGION_NAMES = {
    'IN': 'India',
    'US': 'United States',
    'GB': 'United Kingdom', 
    'UK': 'United Kingdom',
    'CA': 'Canada',
    'AU': 'Australia'
}

def get_trends_by_region(region_code=None, top_n=20, input_dir="output"):
    """Get trending keywords for a specific region or all regions"""
    
    if region_code:
        # Get trends for specific region
        region_code = region_code.upper()
        if region_code not in REGION_MAPPING:
            print(f"❌ Region '{region_code}' not supported")
            print(f"Available regions: {', '.join(REGION_MAPPING.keys())}")
            return []
        
        csv_file = os.path.join(input_dir, REGION_MAPPING[region_code])
        if not os.path.exists(csv_file):
            print(f"❌ Trend data not found for {REGION_NAMES[region_code]}")
            return []
        
        print(f"🔥 Trending Keywords in {REGION_NAMES[region_code]} ({region_code}):")
        print("=" * 60)
        
        trends = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                next(reader)  # Skip header
            except StopIteration:
                return []
            
            for row in reader:
                if not row:
                    continue
                line = row[0]
                # Match [REGION] keyword: N searches
                match = re.match(r'\[([A-Z]{2})\]\s*(.*?):\s*([\d,]+)\s*searches', line)
                if match:
                    keyword = match.group(2).strip()
                    searches = int(match.group(3).replace(',', ''))
                    trends.append((keyword, searches))
        
        # Sort by searches and get top N
        trends.sort(key=lambda x: x[1], reverse=True)
        for i, (keyword, searches) in enumerate(trends[:top_n], 1):
            print(f"{i:2d}. {keyword:<40} {searches:>10,} searches")
        
        return trends[:top_n]
    
    else:
        # Get trends for all regions
        print("🌍 Trending Keywords by Region:")
        print("=" * 60)
        
        all_trends = {}
        for region, filename in REGION_MAPPING.items():
            csv_file = os.path.join(input_dir, filename)
            if not os.path.exists(csv_file):
                continue
            
            trends = []
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    next(reader)  # Skip header
                except StopIteration:
                    continue
                
                for row in reader:
                    if not row:
                        continue
                    line = row[0]
                    match = re.match(r'\[([A-Z]{2})\]\s*(.*?):\s*([\d,]+)\s*searches', line)
                    if match:
                        keyword = match.group(2).strip()
                        searches = int(match.group(3).replace(',', ''))
                        trends.append((keyword, searches))
            
            if trends:
                trends.sort(key=lambda x: x[1], reverse=True)
                all_trends[region] = trends[:5]  # Top 5 per region
        
        # Display trends by region
        for region in ['US', 'IN', 'GB', 'CA', 'AU']:
            if region in all_trends:
                print(f"\n🔥 {REGION_NAMES[region]} ({region}):")
                for i, (keyword, searches) in enumerate(all_trends[region], 1):
                    print(f"   {i}. {keyword:<35} {searches:>8,}")
        
        return all_trends

def compare_regions(regions, top_n=10, input_dir="output"):
    """Compare trending keywords across multiple regions"""
    
    print(f"🔍 Comparing Trends Across Regions: {', '.join(regions)}")
    print("=" * 60)
    
    region_trends = {}
    for region in regions:
        region = region.upper()
        if region not in REGION_MAPPING:
            print(f"⚠️  Skipping unknown region: {region}")
            continue
        
        trends = get_trends_by_region(region, top_n, input_dir)
        if trends:
            region_trends[region] = trends
    
    # Find common keywords
    if len(region_trends) > 1:
        print(f"\n🎯 Common Trending Keywords:")
        
        all_keywords = set()
        for trends in region_trends.values():
            all_keywords.update([keyword for keyword, _ in trends])
        
        common_keywords = []
        for keyword in all_keywords:
            regions_with_keyword = []
            total_searches = 0
            for region, trends in region_trends.items():
                for kw, searches in trends:
                    if kw == keyword:
                        regions_with_keyword.append(region)
                        total_searches += searches
                        break
            
            if len(regions_with_keyword) > 1:
                common_keywords.append((keyword, regions_with_keyword, total_searches))
        
        common_keywords.sort(key=lambda x: x[2], reverse=True)
        
        for keyword, regions, total_searches in common_keywords:
            print(f"   • {keyword:<35} ({', '.join(regions)}) - {total_searches:,} total")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        region = sys.argv[1]
        top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        get_trends_by_region(region, top_n)
    else:
        print("🌍 Regional Trend Checker")
        print("=" * 30)
        print("Usage:")
        print("  python check_trends.py [region] [count]")
        print("  python check_trends.py US 10")
        print("  python check_trends.py IN 15")
        print("")
        print("Available regions: IN, US, GB/UK, CA, AU")
        print("")
        print("Showing all regions (top 5 each):")
        get_trends_by_region()
