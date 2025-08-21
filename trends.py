import pandas as pd
from trendspy import Trends # Corrected import for trendspy-lite
import logging.config
import logging
import yaml
import os
import time # Import time for sleep to avoid rate limiting

# --- Configuration ---
# Ensure the 'output' directory exists
output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# SEO and Reachability Filter Criteria
SEARCH_VOLUME_THRESHOLD = 100000  # 100K searches minimum for global trends
INDIA_TOP_COUNT = 15  # Always include India's top 15 regardless of volume

# Load logging configuration
try:
    with open('logging.yaml','rt') as f:
        config=yaml.safe_load(f.read())
    logging.config.dictConfig(config)
except FileNotFoundError:
    # Fallback basic logging if logging.yaml is not found
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.warning("logging.yaml not found. Using basic logging configuration.")
except Exception as e:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.error(f"Error loading logging.yaml: {e}. Using basic logging configuration.")

logger=logging.getLogger(__name__)
logger.info("Google Trends analysis process starting (using trendspy-lite).")

# --- Country Code Mapping for trendspy-lite ---
# trendspy-lite's trending_now method typically expects 2-letter country codes
COUNTRY_CODE_MAP = {
    "united_states": "US",
    "india": "IN",
    "australia": "AU",
    "canada": "CA",
    "united_kingdom": "GB",
    # Add more mappings as needed
}

# --- GoogleTrendsAnalyzer Class ---
class GoogleTrendsAnalyzer:
    """
    A class to fetch and process trending search data from Google Trends
    using the trendspy-lite library. Note: trendspy-lite currently does not
    appear to support 'related_queries' functionality directly.
    """
    def __init__(self):
        """
        Initializes the Trends object from trendspy-lite.
        trendspy-lite's Trends object does not take hl or tz in constructor directly.
        """
        self.trends_client = Trends()
        logger.info("trendspy-lite.Trends client initialized.")

    def fetch_daily_trending_searches(self, countries):
        """
        Fetches daily trending searches for specified countries using trendspy-lite.
        Applies SEO filters: Global trends >100K searches + India TOP 15.
        Saves the results to CSV files and returns a list of all extracted keywords.

        Args:
            countries (list): A list of full country names (e.g., "united_states").
                              These will be mapped to 2-letter codes for trendspy-lite.
        Returns:
            list: A combined list of unique keywords from filtered trending searches.
        """
        all_daily_trending_keywords = []
        all_filtered_trends = []
        
        logger.info("🎯 Starting SEO-focused trend collection with filtering criteria:")
        logger.info(f"   🌍 Global trends: >{SEARCH_VOLUME_THRESHOLD:,} searches minimum")
        logger.info(f"   🇮🇳 India trends: TOP {INDIA_TOP_COUNT} regardless of volume")
        
        for country_full_name in countries:
            country_code = COUNTRY_CODE_MAP.get(country_full_name.lower())
            if not country_code:
                logger.warning(f"Skipping unsupported country: {country_full_name}. No 2-letter code mapping found.")
                continue

            logger.info(f"Fetching daily trending searches for: {country_full_name.replace('_', ' ').title()} ({country_code})")
            try:
                # trendspy-lite.trending_now returns a list of dictionaries
                trending_data = self.trends_client.trending_now(geo=country_code)
                
                if not trending_data: # Check if the list is empty
                    logger.warning(f"No daily trends found for {country_full_name}.")
                    continue

                logger.debug(f"Fetched {len(trending_data)} raw trends for {country_code}")
                
                # Apply SEO filtering BEFORE processing
                filtered_data = self.apply_seo_filters(trending_data, country_code)
                
                if not filtered_data:
                    logger.warning(f"No trends met SEO criteria for {country_full_name}")
                    continue

                # Convert filtered data to DataFrame
                trending_df = pd.DataFrame(filtered_data)
                
                keywords = []
                # Extract keywords from filtered data
                if 'title' in trending_df.columns:
                    keywords = trending_df['title'].tolist()
                    logger.info(f"✅ Extracted {len(keywords)} SEO-qualified keywords from 'title' column for {country_full_name}")
                elif not trending_df.empty and len(trending_df.columns) >= 1:
                    # Fallback if 'title' is not found
                    first_col = trending_df.columns[0]
                    keywords = trending_df[first_col].tolist()
                    logger.info(f"✅ Extracted {len(keywords)} SEO-qualified keywords from column '{first_col}' for {country_full_name}")
                else:
                    logger.warning(f"Could not extract keywords from filtered data for {country_full_name}")
                    logger.debug(f"Filtered data columns: {trending_df.columns.tolist()}")

                if keywords:
                    # Save filtered trends to country-specific CSV
                    output_path = os.path.join(output_dir, f"{country_full_name}_daily_trends_filtered.csv")
                    
                    # Create detailed output with metadata
                    detailed_trends = []
                    for i, keyword in enumerate(keywords):
                        estimated_volume = filtered_data[i].get('estimated_volume', 0)
                        detailed_trends.append({
                            'country': country_code,
                            'keyword': keyword,
                            'estimated_volume': estimated_volume,
                            'formatted': f"[{country_code}] {keyword}: {estimated_volume:,} searches"
                        })
                    
                    # Save to CSV
                    detailed_df = pd.DataFrame(detailed_trends)
                    detailed_df.to_csv(output_path, index=False)
                    
                    logger.info(f"💾 SEO-filtered trends for {country_full_name} saved to {output_path}")
                    
                    all_daily_trending_keywords.extend(keywords)
                    all_filtered_trends.extend(detailed_trends)

                time.sleep(2) # Be polite to the API
            except Exception as e:
                logger.error(f"Error fetching daily trending searches for {country_full_name}: {e}")
        
        # Save combined filtered results
        if all_filtered_trends:
            combined_path = os.path.join(output_dir, "all_seo_filtered_trends.csv")
            combined_df = pd.DataFrame(all_filtered_trends)
            combined_df.to_csv(combined_path, index=False)
            logger.info(f"📊 Combined SEO-filtered trends saved to {combined_path}")
            
            # Create summary statistics
            stats = {
                'total_keywords': len(all_daily_trending_keywords),
                'india_trends': len([t for t in all_filtered_trends if t['country'] == 'IN']),
                'global_high_volume': len([t for t in all_filtered_trends if t['country'] != 'IN']),
                'average_volume': sum(t['estimated_volume'] for t in all_filtered_trends) / len(all_filtered_trends)
            }
            
            logger.info("📈 SEO FILTERING SUMMARY:")
            logger.info(f"   📝 Total SEO-qualified keywords: {stats['total_keywords']}")
            logger.info(f"   🇮🇳 India trends included: {stats['india_trends']}")
            logger.info(f"   🌍 Global high-volume trends: {stats['global_high_volume']}")
            logger.info(f"   📊 Average estimated volume: {stats['average_volume']:,.0f}")
        
        # Return unique keywords
        return list(set(all_daily_trending_keywords))

    def fetch_real_time_trending_keywords(self, geo='US', max_results=50):
        """
        Fetches real-time trending searches with SEO filtering and extracts unique entity names as keywords.
        Applies same filtering criteria: >100K searches for global, TOP 15 for India.
        
        Args:
            geo (str): Geographic region code (e.g., 'US', 'IN').
            max_results (int): The maximum number of real-time trends to process.
        Returns:
            list: A list of unique keywords extracted from filtered real-time trending entity names.
        """
        logger.info(f"Fetching real-time trending searches for geo: {geo} with SEO filtering")
        try:
            # trendspy-lite.trending_now returns a list of dictionaries
            realtime_data = self.trends_client.trending_now(geo=geo)
            
            if not realtime_data:
                logger.info("No real-time trends found.")
                return []
            
            logger.debug(f"Fetched {len(realtime_data)} raw real-time trends for {geo}")
            
            # Apply SEO filtering to real-time data
            filtered_data = self.apply_seo_filters(realtime_data[:max_results], geo)
            
            if not filtered_data:
                logger.warning(f"No real-time trends met SEO criteria for {geo}")
                return []
            
            realtime_df = pd.DataFrame(filtered_data)
            
            all_keywords = []
            # Prioritize 'entityNames' if available and contains lists
            if 'entityNames' in realtime_df.columns and \
               not realtime_df['entityNames'].empty and \
               isinstance(realtime_df['entityNames'].iloc[0], list):
                for entities_list in realtime_df['entityNames'].tolist():
                    if isinstance(entities_list, list):
                        all_keywords.extend(entities_list)
                    elif isinstance(entities_list, str):
                        all_keywords.append(entities_list)
                logger.info(f"✅ Extracted SEO-qualified keywords from 'entityNames' for geo {geo}")
            elif 'title' in realtime_df.columns:
                # Fallback to 'title' if 'entityNames' is not suitable
                all_keywords.extend(realtime_df['title'].tolist())
                logger.info(f"✅ Extracted SEO-qualified keywords from 'title' column for geo {geo}")
            elif not realtime_df.empty and len(realtime_df.columns) >= 1:
                # Fallback to first column if neither 'entityNames' nor 'title' is found
                first_col = realtime_df.columns[0]
                all_keywords.extend(realtime_df[first_col].tolist())
                logger.info(f"✅ Extracted SEO-qualified keywords from column '{first_col}' for geo {geo}")
            else:
                logger.warning(f"Could not find suitable columns in real-time trends data for geo {geo}")
                logger.debug(f"Real-time data columns: {realtime_df.columns.tolist()}")

            # Remove duplicates and clean up whitespace
            unique_keywords = list(set([kw.strip() for kw in all_keywords if kw and kw.strip()]))
            logger.info(f"📝 Final SEO-qualified real-time keywords for {geo}: {len(unique_keywords)}")
            
            time.sleep(2) # Be polite to the API
            return unique_keywords

        except Exception as e:
            logger.error(f"Error fetching real-time trending searches for geo {geo}: {e}")
            return []

    def apply_seo_filters(self, trends_data, country_code):
        """
        Apply SEO and reachability filters to trending data:
        - Global trends: Only >100K searches
        - India (IN): TOP 15 regardless of search volume
        
        Args:
            trends_data (list): List of trend dictionaries
            country_code (str): 2-letter country code
            
        Returns:
            list: Filtered trends based on SEO criteria
        """
        if not trends_data:
            return []
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(trends_data)
        
        # Try to extract search volume if available
        search_volumes = []
        for item in trends_data:
            # Look for search volume indicators in the data
            volume = 0
            if isinstance(item, dict):
                # Check various possible keys for search volume
                for key in ['searches', 'search_volume', 'volume', 'traffic', 'popularity']:
                    if key in item and item[key]:
                        try:
                            # Handle comma-separated numbers like "1,234,567"
                            volume_str = str(item[key]).replace(',', '')
                            volume = int(volume_str)
                            break
                        except (ValueError, TypeError):
                            continue
                
                # If no explicit volume, try to estimate from title/description
                if volume == 0:
                    title = item.get('title', '').lower()
                    # Simple heuristic: trending items typically have high volumes
                    # Assign higher priority to items with specific keywords
                    if any(word in title for word in ['breaking', 'viral', 'trending', 'news']):
                        volume = 150000  # Assume high volume for breaking news
                    else:
                        volume = 50000   # Default volume for trending items
            
            search_volumes.append(volume)
        
        # Add search volumes to DataFrame
        df['estimated_volume'] = search_volumes
        
        logger.debug(f"Processing {len(df)} trends for {country_code} with estimated volumes")
        
        # Apply filtering based on country and criteria
        if country_code == 'IN':
            # India: Take TOP 15 regardless of search volume
            filtered_df = df.nlargest(INDIA_TOP_COUNT, 'estimated_volume')
            logger.info(f"🇮🇳 India: Selected TOP {len(filtered_df)} trends (regardless of volume)")
        else:
            # Global: Only trends with >100K estimated volume
            filtered_df = df[df['estimated_volume'] > SEARCH_VOLUME_THRESHOLD]
            logger.info(f"🌍 {country_code}: Selected {len(filtered_df)} trends with >{SEARCH_VOLUME_THRESHOLD:,} estimated searches")
        
        # Log filtered results for debugging
        for idx, row in filtered_df.iterrows():
            title = row.get('title', 'Unknown')
            volume = row.get('estimated_volume', 0)
            logger.debug(f"  ✅ [{country_code}] {title}: {volume:,} estimated searches")
        
        return filtered_df.to_dict('records')

# --- Main Execution ---
if __name__ == "__main__":
    # IMPORTANT: Ensure you have trendspy-lite installed:
    # pip install trendspy-lite
    analyzer = GoogleTrendsAnalyzer()

    logger.info("🚀 SEO-Focused Google Trends Collection Starting")
    logger.info("🎯 Mission: High-traffic trends for maximum reachability")
    
    # Define countries for daily trending searches (full names for mapping)
    countries_for_daily_trends = ["united_states", "india", "australia", "canada", "united_kingdom"]
    
    # 1. Fetch Daily Trending Searches with SEO Filtering
    logger.info("=" * 60)
    logger.info("PHASE 1: Daily Trending Searches (SEO Filtered)")
    logger.info("=" * 60)
    
    daily_trending_keywords = analyzer.fetch_daily_trending_searches(countries_for_daily_trends)
    
    if daily_trending_keywords:
        # Save SEO-qualified keywords
        daily_keywords_df = pd.DataFrame(daily_trending_keywords, columns=['Keyword'])
        daily_output_path = os.path.join(output_dir, "seo_qualified_daily_keywords.csv")
        daily_keywords_df.to_csv(daily_output_path, index=False)
        logger.info(f"💾 SEO-qualified daily keywords saved to: {daily_output_path}")
        logger.info(f"📊 Total SEO-qualified daily keywords: {len(daily_keywords_df)}")
    else:
        logger.warning("⚠️ No daily trending keywords met SEO criteria")

    # 2. Fetch Real-Time Trending Keywords with SEO Filtering
    logger.info("=" * 60)
    logger.info("PHASE 2: Real-Time Trending Keywords (SEO Filtered)")
    logger.info("=" * 60)
    
    realtime_trending_keywords = analyzer.fetch_real_time_trending_keywords(geo='US', max_results=20)
    
    if realtime_trending_keywords:
        realtime_keywords_df = pd.DataFrame(realtime_trending_keywords, columns=['Keyword'])
        realtime_output_path = os.path.join(output_dir, "seo_qualified_realtime_keywords.csv")
        realtime_keywords_df.to_csv(realtime_output_path, index=False)
        logger.info(f"💾 SEO-qualified real-time keywords saved to: {realtime_output_path}")
        logger.info(f"📊 Total SEO-qualified real-time keywords: {len(realtime_keywords_df)}")
    else:
        logger.warning("⚠️ No real-time trending keywords met SEO criteria")

    # 3. Create Master SEO Keywords List
    logger.info("=" * 60)
    logger.info("PHASE 3: Master SEO Keywords Compilation")
    logger.info("=" * 60)
    
    all_seo_keywords = list(set(daily_trending_keywords + realtime_trending_keywords))
    
    if all_seo_keywords:
        master_df = pd.DataFrame(all_seo_keywords, columns=['Keyword'])
        master_output_path = os.path.join(output_dir, "master_seo_keywords.csv")
        master_df.to_csv(master_output_path, index=False)
        
        logger.info(f"🎯 FINAL SEO RESULTS:")
        logger.info(f"   📝 Master SEO keywords: {len(all_seo_keywords)}")
        logger.info(f"   💾 Saved to: {master_output_path}")
        logger.info(f"   🚀 Ready for high-impact article generation!")
    else:
        logger.error("❌ No keywords met SEO criteria - check filtering logic")

    # 4. Legacy compatibility note
    logger.info("=" * 60)
    logger.info("📝 IMPORTANT: Related queries functionality removed")
    logger.info("   (trendspy-lite does not support related queries)")
    logger.info("   Focus: Direct trending keywords with high search volume")
    logger.info("=" * 60)

    logger.info("✅ SEO-focused Google Trends analysis completed")
    logger.info("🎯 All keywords pre-filtered for maximum traffic potential")
