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
        Fetches daily trending searches for a list of specified countries using trendspy-lite.
        Saves the results to CSV files and returns a list of all extracted keywords.

        Args:
            countries (list): A list of full country names (e.g., "united_states").
                              These will be mapped to 2-letter codes for trendspy-lite.
        Returns:
            list: A combined list of unique keywords from daily trending searches.
        """
        all_daily_trending_keywords = []
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

                # Convert list of dictionaries to DataFrame
                trending_df = pd.DataFrame(trending_data)
                
                keywords = []
                # Attempt to extract keywords from 'title' column first
                if 'title' in trending_df.columns:
                    keywords = trending_df['title'].tolist()
                    logger.debug(f"Extracted {len(keywords)} keywords from 'title' column for {country_full_name}.")
                elif not trending_df.empty and len(trending_df.columns) == 1:
                    # Fallback if 'title' is not found but there's a single column (e.g., named 0)
                    # This handles cases where the data might just be a list of values
                    logger.warning(f"No 'title' column found for {country_full_name}. Attempting to extract from single column: {trending_df.columns[0]}")
                    keywords = trending_df[trending_df.columns[0]].tolist()
                    logger.debug(f"Extracted {len(keywords)} keywords from column '{trending_df.columns[0]}' for {country_full_name}.")
                else:
                    logger.warning(f"Could not find 'title' or suitable single column in trending data for {country_full_name}. Data structure might have changed.")
                    logger.debug(f"Trending data columns: {trending_df.columns.tolist()}")

                if keywords:
                    output_path = os.path.join(output_dir, f"{country_full_name}_daily_trends.csv")
                    trending_df.to_csv(output_path, index=False)
                    logger.info(f"Daily trends for {country_full_name.replace('_', ' ').title()} saved to {output_path}")
                    all_daily_trending_keywords.extend(keywords)

                time.sleep(2) # Be polite to the API
            except Exception as e:
                logger.error(f"Error fetching daily trending searches for {country_full_name}: {e}")
        
        # Return unique keywords
        return list(set(all_daily_trending_keywords))

    def fetch_real_time_trending_keywords(self, geo='US', max_results=50):
        """
        Fetches real-time trending searches and extracts unique entity names as keywords using trendspy-lite.
        
        Args:
            geo (str): Geographic region code (e.g., 'US', 'IN').
            max_results (int): The maximum number of real-time trends to process.
        Returns:
            list: A list of unique keywords extracted from real-time trending entity names.
        """
        logger.info(f"Fetching real-time trending searches for geo: {geo}")
        try:
            # trendspy-lite.trending_now returns a list of dictionaries
            realtime_data = self.trends_client.trending_now(geo=geo)
            
            if not realtime_data:
                logger.info("No real-time trends found.")
                return []
            
            realtime_df = pd.DataFrame(realtime_data)
            entities_to_process = realtime_df.head(max_results)
            
            all_keywords = []
            # Prioritize 'entityNames' if available and contains lists
            if 'entityNames' in entities_to_process.columns and \
               not entities_to_process['entityNames'].empty and \
               isinstance(entities_to_process['entityNames'].iloc[0], list):
                for entities_list in entities_to_process['entityNames'].tolist():
                    if isinstance(entities_list, list):
                        all_keywords.extend(entities_list)
                    elif isinstance(entities_list, str):
                        all_keywords.append(entities_list)
                logger.debug(f"Extracted keywords from 'entityNames' for geo {geo}.")
            elif 'title' in entities_to_process.columns:
                # Fallback to 'title' if 'entityNames' is not suitable
                logger.info(f"No suitable 'entityNames' found in real-time trends for geo {geo}, falling back to 'title' column.")
                all_keywords.extend(entities_to_process['title'].tolist())
            elif not entities_to_process.empty and len(entities_to_process.columns) == 1:
                # Fallback to single column if neither 'entityNames' nor 'title' is found
                logger.warning(f"Neither 'entityNames' nor 'title' column found in real-time trends for geo {geo}. Attempting to extract from single column: {entities_to_process.columns[0]}")
                all_keywords.extend(entities_to_process[entities_to_process.columns[0]].tolist())
            else:
                logger.warning(f"Could not find 'entityNames', 'title', or suitable single column in real-time trends data for geo {geo}.")
                logger.debug(f"Real-time data columns: {realtime_df.columns.tolist()}")

            # Remove duplicates and clean up whitespace
            unique_keywords = list(set([kw.strip() for kw in all_keywords if kw and kw.strip()]))
            logger.debug(f"Unique real-time keywords extracted ({len(unique_keywords)}): {unique_keywords[:20]}...")
            time.sleep(2) # Be polite to the API
            return unique_keywords

        except Exception as e:
            logger.error(f"Error fetching real-time trending searches for geo {geo}: {e}")
            return []

    # Removed get_related_queries_for_keywords as trendspy-lite does not appear to support it.
    # If this functionality is critical, you might need to explore other libraries or APIs.

# --- Main Execution ---
if __name__ == "__main__":
    # IMPORTANT: Ensure you have trendspy-lite installed:
    # pip install trendspy-lite
    analyzer = GoogleTrendsAnalyzer()

    # Define countries for daily trending searches (full names for mapping)
    countries_for_daily_trends = ["united_states", "india", "australia", "canada", "united_kingdom"]
    
    # 1. Fetch Daily Trending Searches
    daily_trending_keywords = analyzer.fetch_daily_trending_searches(countries_for_daily_trends)
    
    if daily_trending_keywords:
        daily_keywords_df = pd.DataFrame(daily_trending_keywords, columns=['Keyword','relatedKeywordsCount','topic'])
        daily_keywords_df.to_csv(os.path.join(output_dir, "all_unique_daily_trending_keywords.csv"), index=False)
        logger.info(f"Total unique daily trending keywords collected: {len(daily_keywords_df)}")
    else:
        logger.info("No daily trending keywords were collected.")

    # 2. Fetch Real-Time Trending Keywords (e.g., for US)
    # Note: trendspy-lite's trending_now method covers both daily and real-time.
    # We'll use a 2-letter code directly here.
    realtime_trending_keywords = analyzer.fetch_real_time_trending_keywords(geo='US', max_results=20)
    
    if realtime_trending_keywords:
        realtime_keywords_df = pd.DataFrame(realtime_trending_keywords, columns=['Keyword'])
        realtime_keywords_df.to_csv(os.path.join(output_dir, "all_unique_realtime_trending_keywords.csv"), index=False)
        logger.info(f"Total unique real-time trending keywords collected: {len(realtime_keywords_df)}")
    else:
        logger.info("No real-time trending keywords were collected.")

    # 3. Related queries section has been removed as trendspy-lite does not support it.
    logger.info("Related query functionality is not supported by trendspy-lite and has been skipped.")

    logger.info("Google Trends analysis process finished.")
