import csv
import re
import os

# ---------------------------------------------------------------------------
# Pillar-alignment filter — reject trends that are clearly off-pillar
# The 4 PRD pillars: AI Infrastructure, Enterprise Transformation,
# Smart Mobility, India Digital Transformation
# ---------------------------------------------------------------------------
_OFFPILLAR_RE = re.compile(
    r'\b('
    # Sports
    r'cricket|ipl|bcci|t20|odi|wicket|batting|bowling|test match|innings|fielding|'
    r'football|soccer|fifa|premier league|la liga|bundesliga|serie a|ligue 1|'
    r'nba|nfl|mlb|nhl|nfl|tennis|wimbledon|us open|french open|australian open|'
    r'kabaddi|pro kabaddi|badminton|chess|wrestling|boxing|kho.kho|'
    r'olympics|commonwealth games|asian games|cwg|world cup cricket|'
    r'match score|live score|match result|scorecard|'
    # Entertainment
    r'bollywood|hollywood|tollywood|kollywood|mollywood|'
    r'\bactor\b|\bactress\b|\bsinger\b|\bchoreographer\b|'
    r'bigg boss|kaun banega|reality show|'
    r'box office|ott release|album launch|music video|song release|'
    r'movie review|film review|web series review|'
    # Pure lifestyle / tabloid
    r'recipe|diet plan|weight loss tips|beauty tips|makeup tutorial|hairstyle|'
    r'skincare routine|fashion week|celebrity wedding|celebrity baby|'
    r'horoscope|zodiac|astrology'
    r')\b',
    re.IGNORECASE,
)

# On-pillar override: if keyword contains any of these, allow it even if it
# also matched the blocklist (e.g. "AI scoring in cricket broadcasts")
_ONPILLAR_RE = re.compile(
    r'\b('
    r'ai|artificial intelligence|machine learning|deep learning|llm|generative ai|'
    r'large language model|neural network|gpu|tpu|data cent(?:er|re)|'
    r'cloud computing|semiconductor|chip|processor|nvidia|amd|intel|'
    r'electric vehicle|\bev\b|autonomous vehicle|self.driving|'
    r'digital india|upi|fintech|digital payment|startup india|'
    r'enterprise software|erp|automation|digital transformation|'
    r'robotics|internet of things|\biot\b|5g|6g|blockchain|cybersecurity|'
    r'data science|big data|quantum computing|edge computing'
    r')\b',
    re.IGNORECASE,
)


def _is_pillar_aligned(keyword: str) -> bool:
    """Return True if the keyword is relevant to one of the 4 PRD pillars."""
    if _OFFPILLAR_RE.search(keyword):
        # Allow hybrid keywords that also touch a PRD pillar topic
        return bool(_ONPILLAR_RE.search(keyword))
    return True


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
    offpillar_dropped = 0
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
                                if not _is_pillar_aligned(keyword):
                                    offpillar_dropped += 1
                                    continue
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
                            if not _is_pillar_aligned(keyword):
                                offpillar_dropped += 1
                                continue
                            key = (region, keyword)
                            region_keyword_searches[key] = region_keyword_searches.get(key, 0) + searches
                            trends_processed += 1
            except StopIteration:
                continue  # Skip empty files

    print(f"📈 Processed {trends_processed} pillar-aligned trends ({offpillar_dropped} off-pillar dropped)")
    
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