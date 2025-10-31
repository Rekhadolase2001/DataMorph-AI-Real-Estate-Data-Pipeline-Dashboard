# etl.py
"""
DataMorph AI ETL runner.
Orchestrates: scraper.scrape_search_page -> transform.transform_properties -> loader_mysql.load_properties_df
Usage:
    python etl.py
"""

from scraper import scrape_search_page
from transform import transform_properties
from loader_mysql import load_properties_df
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def run_etl_for_url(url, max_items=50):
    logging.info("Starting ETL for URL: %s", url)
    try:
        raw = scrape_search_page(url, max_items=max_items)
        logging.info("Raw rows scraped: %d", len(raw))
    except Exception as e:
        logging.exception("Error during scraping: %s", e)
        return

    try:
        clean = transform_properties(raw)
        logging.info("Transformed rows: %d", len(clean) if clean is not None else 0)
    except Exception as e:
        logging.exception("Error during transform: %s", e)
        return

    try:
        load_properties_df(clean)
        logging.info("Loaded rows into DB.")
    except Exception as e:
        logging.exception("Error during DB load: %s", e)
        return

if __name__ == "__main__":
    # You can add multiple search pages here if you want to collect more cities.
    SEARCH_PAGES = [
        # Example: Bangalore sale listings (change to any MagicBricks search page you want)
        "https://www.magicbricks.com/property-for-sale-in-bangalore-pppfs",
        # You can add more pages later:
        # "https://www.magicbricks.com/property-for-sale-in-mumbai-pppfs",
    ]

    # How many items to fetch per page (tweak for demo; larger value -> more scraping)
    MAX_ITEMS_PER_PAGE = 40

    started = datetime.utcnow()
    logging.info("ETL run started at %s UTC", started.isoformat())
    for url in SEARCH_PAGES:
        run_etl_for_url(url, max_items=MAX_ITEMS_PER_PAGE)
    finished = datetime.utcnow()
    logging.info("ETL run finished at %s UTC (elapsed: %s)", finished.isoformat(), finished - started)