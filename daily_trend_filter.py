#!/usr/bin/env python3
"""
Daily Trend Filter
Filters trends based on specific criteria:
- Global trends with >100K searches
- India's TOP 15 articles (regardless of search volume)
"""

import csv
import re
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/daily_filter_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_trend_line(line):
    """Parse a trend line to extract region, keyword, and search count"""
    # Match [REGION] keyword: N searches
    match = re.match(r'\[([A-Z]{2})\]\s*(.*?):\s*([\d,]+)\s*searches', line.strip())
    if match:
        region = match.group(1)
        keyword = match.group(2).strip()
        searches = int(match.group(3).replace(',', ''))
        return region, keyword, searches
    return None, None, None

def filter_trends_by_criteria(input_dir="output", output_dir="output"):
    """
    Filter trends based on criteria:
    - Global trends with >100K searches
    - India's TOP 15 articles (regardless of search volume)
    """
    logger.info("Starting daily trend filtering...")
    
    # Collect all trends
    all_trends = []
    india_trends = []
    
    # Process all CSV files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv") and "trending" in filename:
            csv_file = os.path.join(input_dir, filename)
            logger.info(f"Processing {filename}...")
            
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
                    region, keyword, searches = parse_trend_line(line)
                    
                    if region and keyword and searches is not None:
                        trend_data = {
                            'region': region,
                            'keyword': keyword,
                            'searches': searches,
                            'original_line': line
                        }
                        
                        # Separate India trends
                        if region == 'IN':
                            india_trends.append(trend_data)
                        else:
                            all_trends.append(trend_data)
    
    # Filter global trends (>100K searches)
    filtered_global_trends = [
        trend for trend in all_trends 
        if trend['searches'] > 100000
    ]
    
    # Sort India trends by search volume and take top 15
    india_trends.sort(key=lambda x: x['searches'], reverse=True)
    top_india_trends = india_trends[:15]
    
    # Combine filtered results
    final_trends = filtered_global_trends + top_india_trends
    
    # Sort by search volume for output
    final_trends.sort(key=lambda x: x['searches'], reverse=True)
    
    # Log statistics
    logger.info(f"Original trends processed: {len(all_trends) + len(india_trends)}")
    logger.info(f"Global trends >100K: {len(filtered_global_trends)}")
    logger.info(f"India top 15 trends: {len(top_india_trends)}")
    logger.info(f"Total filtered trends: {len(final_trends)}")
    
    # Save filtered results
    output_file = os.path.join(output_dir, "daily_filtered_trends.csv")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Trend'])  # Header
        
        for trend in final_trends:
            writer.writerow([trend['original_line']])
    
    logger.info(f"Filtered trends saved to {output_file}")
    
    # Create summary report
    summary_file = os.path.join(output_dir, "daily_filter_summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"Daily Trend Filter Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Original trends processed: {len(all_trends) + len(india_trends)}\n")
        f.write(f"Global trends >100K searches: {len(filtered_global_trends)}\n")
        f.write(f"India top 15 trends: {len(top_india_trends)}\n")
        f.write(f"Total filtered trends: {len(final_trends)}\n\n")
        
        f.write("TOP FILTERED TRENDS:\n")
        f.write("-" * 40 + "\n")
        for i, trend in enumerate(final_trends[:20], 1):
            f.write(f"{i:2d}. [{trend['region']}] {trend['keyword']}: {trend['searches']:,} searches\n")
        
        if len(final_trends) > 20:
            f.write(f"... and {len(final_trends) - 20} more trends\n")
    
    logger.info(f"Summary report saved to {summary_file}")
    
    return len(final_trends)

def main():
    """Main execution"""
    logger.info("🚀 Daily Trend Filter Starting")
    logger.info("Criteria: Global trends >100K searches + India TOP 15")
    
    try:
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Filter trends
        trend_count = filter_trends_by_criteria()
        
        if trend_count > 0:
            logger.info(f"✅ Successfully filtered {trend_count} trends")
            logger.info("📝 Ready for article generation using filtered trends")
        else:
            logger.warning("⚠️ No trends met the filtering criteria")
        
        return trend_count > 0
        
    except Exception as e:
        logger.error(f"❌ Error during trend filtering: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
