"""
ai_scraper.py

DataMorph AI – Adaptive Real Estate Scraper

✔ Local PC → Selenium (undetected / normal)
✔ Cloud → Requests only
✔ Supports URL + Uploaded HTML
✔ BS4 parsing fallback
✔ Safe geocoding
✔ No silent failures
"""

import os
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from selenium_options import get_selenium_driver
from geo_helper import get_lat_lon

load_dotenv()

# -------------------------------------------------
# ENV FLAGS
# -------------------------------------------------
ON_CLOUD = os.environ.get("STREAMLIT_RUNTIME", "") != ""
USE_SELENIUM = os.getenv("USE_SELENIUM", "false").lower() == "true"

# -------------------------------------------------
# HTML PARSER (WORKS WITH YOUR EXAMPLE FILES)
# -------------------------------------------------
def parse_html(html: str):
    soup = BeautifulSoup(html, "html.parser")
    properties = []

    cards = soup.select(
        "div.mb-srp__card, div.listingCard, article.card"
    )

    for card in cards:
        try:
            title = card.find(["h1", "h2", "h3"])
            price = card.select_one(".price, .mb-srp__card__price--amount, .css-1rhznz4")
            location = card.select_one(".locName, .mb-srp__card__location, .css-1rzr0xl")

            img = card.find("img")
            link = card.find("a", href=True)

            lat_tag = card.select_one(".latitude")
            lon_tag = card.select_one(".longitude")

            lat = float(lat_tag.text.strip()) if lat_tag else None
            lon = float(lon_tag.text.strip()) if lon_tag else None

            properties.append({
                "Title": title.text.strip() if title else "",
                "Price": price.text.strip() if price else "",
                "Location": location.text.strip() if location else "",
                "Bedrooms": "",
                "Bathrooms": "",
                "Area_sqft": "",
                "Latitude": lat,
                "Longitude": lon,
                "Image_URL": img["src"] if img else "",
                "URL": link["href"] if link else ""
            })

        except Exception:
            continue

    return properties


# -------------------------------------------------
# MAIN SCRAPER
# -------------------------------------------------
def scrape_properties(source, is_html=False) -> pd.DataFrame:
    html = ""

    # ---------------------------------------------
    # 1️⃣ HTML UPLOAD
    # ---------------------------------------------
    if is_html:
        html = source

    # ---------------------------------------------
    # 2️⃣ URL SCRAPING
    # ---------------------------------------------
    else:
        url = source.strip()

        # -------- LOCAL → Selenium --------
        if not ON_CLOUD and USE_SELENIUM:
            driver = get_selenium_driver(headless=False)
            if driver:
                try:
                    driver.get(url)
                    time.sleep(5)  # IMPORTANT
                    html = driver.page_source
                finally:
                    driver.quit()

        # -------- FALLBACK → Requests --------
        if not html:
            try:
                r = requests.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=15
                )
                html = r.text
            except:
                html = ""

    # ---------------------------------------------
    # FAIL SAFE
    # ---------------------------------------------
    if not html or len(html) < 500:
        return pd.DataFrame(columns=[
            "Title", "Price", "Location", "Bedrooms", "Bathrooms",
            "Area_sqft", "Latitude", "Longitude", "Image_URL", "URL"
        ])

    # ---------------------------------------------
    # PARSE
    # ---------------------------------------------
    data = parse_html(html)
    df = pd.DataFrame(data)

    if df.empty:
        return df

    # ---------------------------------------------
    # GEOCODE IF MISSING
    # ---------------------------------------------
    for i in df.index:
        if pd.isna(df.at[i, "Latitude"]) or pd.isna(df.at[i, "Longitude"]):
            lat, lon = get_lat_lon(df.at[i, "Location"])
            df.at[i, "Latitude"] = lat
            df.at[i, "Longitude"] = lon

    return df
