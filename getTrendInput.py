import csv
import re
import os

def get_top_region_keywords(input_dir="output", top_n=20, use_filtered_trends=True):
    """
    Get top trending keywords with optional filtering for daily criteria:
    - Global trends with >100K searches
    - India's TOP 15 articles (regardless of search volume)
    
    Now prioritizes SEO-filtered trends from the new trends.py filtering system.
    """
    region_keyword_searches = {}
    
    # Check if SEO-filtered trends file exists (new filtering system)
    seo_filtered_file = os.path.join(input_dir, "all_seo_filtered_trends.csv")
    master_keywords_file = os.path.join(input_dir, "master_seo_keywords.csv")
    
    if use_filtered_trends and os.path.exists(seo_filtered_file):
        print(f"🎯 Using SEO-filtered trends from {seo_filtered_file}")
        csv_files = [seo_filtered_file]
    elif use_filtered_trends and os.path.exists(master_keywords_file):
        print(f"🎯 Using master SEO keywords from {master_keywords_file}")
        csv_files = [master_keywords_file]
    else:
        # Fallback to country-specific filtered files
        filtered_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) 
                         if f.endswith("_daily_trends_filtered.csv")]
        
        if use_filtered_trends and filtered_files:
            print(f"📊 Using country-specific filtered trends: {len(filtered_files)} files")
            csv_files = filtered_files
        else:
            # Use all CSV files as last resort
            print("⚠️ No filtered trends found, using all available CSV files")
            csv_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".csv")]

    trends_processed = 0
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            continue
            
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                header = next(reader)  # Read header
                # Check if this is the new detailed format
                if 'formatted' in header:
                    # New detailed format with structured data
                    for row in reader:
                        if len(row) >= 4:  # country, keyword, estimated_volume, formatted
                            try:
                                region = row[0]
                                keyword = row[1]
                                searches = int(row[2])
                                key = (region, keyword)
                                region_keyword_searches[key] = region_keyword_searches.get(key, 0) + searches
                                trends_processed += 1
                            except (ValueError, IndexError):
                                continue
                else:
                    # Legacy format or simple keyword list
                    f.seek(0)  # Reset file pointer
                    next(reader)  # Skip header again
                    for row in reader:
                        if not row:
                            continue
                        line = row[0]
                        # Match [REGION] keyword: N searches format
                        match = re.match(r'\[([A-Z]{2})\]\s*(.*?):\s*([\d,]+)\s*searches', line)
                        if match:
                            region = match.group(1)
                            keyword = match.group(2).strip()
                            searches = int(match.group(3).replace(',', ''))
                            key = (region, keyword)
                            region_keyword_searches[key] = region_keyword_searches.get(key, 0) + searches
                            trends_processed += 1
            except StopIteration:
                continue  # Skip empty files

    print(f"📈 Processed {trends_processed} SEO-qualified trends")
    
    # Get top N (region, keyword) pairs by number of searches
    top_region_keywords = sorted(
        region_keyword_searches.items(), key=lambda x: x[1], reverse=True
    )[:top_n]

    # Return as list of (region, keyword, searches)
    result = [(region, keyword, searches) for ((region, keyword), searches) in top_region_keywords]
    
    if result:
        print(f"🎯 Top {len(result)} SEO-qualified trends selected for article generation")
        for i, (region, keyword, searches) in enumerate(result[:5], 1):
            print(f"  {i}. [{region}] {keyword}: {searches:,} searches")
        if len(result) > 5:
            print(f"  ... and {len(result) - 5} more high-traffic trends")
    else:
        print("⚠️ No SEO-qualified trends found - check filtering criteria")
    
    return result

# Example usage:
if __name__ == "__main__":
    for region, keyword, searches in get_top_region_keywords():
        print(f"[{region}] {keyword}: {searches}")