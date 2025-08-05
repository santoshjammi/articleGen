import csv
import re
import os

def get_top_region_keywords(input_dir="output", top_n=20):
    region_keyword_searches = {}

    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            csv_file = os.path.join(input_dir, filename)
            with open(csv_file, newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                try:
                    next(reader)  # Skip header
                except StopIteration:
                    continue  # Skip empty files
                for row in reader:
                    if not row:
                        continue
                    line = row[0]
                    # Match [REGION] keyword: N searches
                    match = re.match(r'\[([A-Z]{2})\]\s*(.*?):\s*([\d,]+)\s*searches', line)
                    if match:
                        region = match.group(1)
                        keyword = match.group(2).strip()
                        searches = int(match.group(3).replace(',', ''))
                        key = (region, keyword)
                        region_keyword_searches[key] = region_keyword_searches.get(key, 0) + searches

    # Get top N (region, keyword) pairs by number of searches
    top_region_keywords = sorted(
        region_keyword_searches.items(), key=lambda x: x[1], reverse=True
    )[:top_n]

    # Return as list of (region, keyword, searches)
    return [(region, keyword, searches) for ((region, keyword), searches) in top_region_keywords]

# Example usage:
if __name__ == "__main__":
    for region, keyword, searches in get_top_region_keywords():
        print(f"[{region}] {keyword}: {searches}")