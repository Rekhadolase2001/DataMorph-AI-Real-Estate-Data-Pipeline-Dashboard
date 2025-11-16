# ai_scraper.py
"""
Multi-site AI scraper helper (MagicBricks / 99acres / Housing.com)
Auto-switch:
- Local PC → Selenium + Ollama + BS4
- Streamlit Cloud → Requests + BS4 (no Selenium, no Ollama)
"""

import os
import time
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import subprocess
import undetected_chromedriver as uc

load_dotenv()

# ----------------------------------------------------------
# Detect Streamlit Cloud
# ----------------------------------------------------------
ON_CLOUD = os.environ.get("STREAMLIT_RUNTIME", "") != ""

# ----------------------------------------------------------
# Environment toggles
# ----------------------------------------------------------
GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
USE_SELENIUM_ENV = os.getenv("USE_SELENIUM", "false").lower() == "true"

# ----------------------------------------------------------
# Optional Selenium
# ----------------------------------------------------------
def _try_import_selenium():
    if ON_CLOUD:
        return None
    try:
        import undetected_chromedriver as uc
        return {"type": "uc", "uc": uc}
    except:
        pass
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        return {
            "type": "selenium",
            "webdriver": webdriver,
            "Service": Service,
            "Options": Options,
            "ChromeDriverManager": ChromeDriverManager,
        }
    except:
        return None

# ----------------------------------------------------------
# Google Maps Geocoding
# ----------------------------------------------------------
def get_lat_lon(address):
    if not GOOGLE_KEY or not address:
        return None, None
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address, "key": GOOGLE_KEY},
            timeout=8,
        )
        j = resp.json()
        if j.get("results"):
            loc = j["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
    except:
        return None, None
    return None, None

# ----------------------------------------------------------
# Ollama Parser (LOCAL ONLY)
# ----------------------------------------------------------
def _ollama_extract(html, model="tinyllama"):
    if ON_CLOUD:
        return None  # Streamlit Cloud → skip
    try:
        prompt = (
            "Extract property listings from this HTML. "
            "Return ONLY JSON list of objects. Keys: "
            "Title, Price, Location, Bedrooms, Bathrooms, Area_sqft, "
            "Latitude, Longitude, Image_URL, URL.\n\n"
        )
        snippet = html[:6000]
        cmd = ["ollama", "run", model, prompt + snippet]
        out = subprocess.check_output(cmd, text=True, timeout=25)

        start = out.find("[")
        if start == -1:
            return None

        data = json.loads(out[start:])
        return data if isinstance(data, list) else None
    except:
        return None

# ----------------------------------------------------------
# BeautifulSoup Fallback
# ----------------------------------------------------------
def _bs4_parse(html):
    soup = BeautifulSoup(html, "html.parser")
    properties = []

    cards = soup.select("div.mb-srp__card, div.listingCard, article.card, div.srpTuple, div.card")
    if not cards:
        cards = soup.find_all("div")

    for card in cards:
        try:
            title = card.find(["h1", "h2", "h3"])
            price = card.select_one(".price, .mb-srp__card__price--amount")
            location = card.select_one(".locName, .location, .mb-srp__card__location")
            img = card.find("img")
            a = card.find("a", href=True)

            properties.append({
                "Title": title.get_text(strip=True) if title else "",
                "Price": price.get_text(strip=True) if price else "",
                "Location": location.get_text(strip=True) if location else "",
                "Bedrooms": "",
                "Bathrooms": "",
                "Area_sqft": "",
                "Latitude": None,
                "Longitude": None,
                "Image_URL": img["src"] if img else "",
                "URL": a["href"] if a else "",
            })
        except:
            continue

    return properties

# ----------------------------------------------------------
# Main Function
# ----------------------------------------------------------
def scrape_properties(source, is_html=False):
    """
    Auto-adapts to local vs cloud.
    Returns DataFrame with expected columns.
    """

    html = ""

    # ---- Handle HTML upload ----
    if is_html:
        html = source

    # ---- Load from URL ----
    else:
        url = source

        # LOCAL → Try Selenium
        if not ON_CLOUD and USE_SELENIUM_ENV:
            sel = _try_import_selenium()
            if sel:
                try:
                    if sel["type"] == "uc":
                        uc = sel["uc"]
                        driver = uc.Chrome()
                        driver.get(url)
                        time.sleep(3)
                        html = driver.page_source
                        driver.quit()
                    else:
                        options = sel["Options"]()
                        options.add_argument("--headless=new")
                        driver = sel["webdriver"].Chrome(
                            service=sel["Service"](sel["ChromeDriverManager"]().install()),
                            options=options,
                        )
                        driver.get(url)
                        time.sleep(3)
                        html = driver.page_source
                        driver.quit()
                except:
                    html = ""

        # CLOUD or Selenium failed → requests
        if not html:
            try:
                r = requests.get(url, headers={"User-Agent": "Mozilla"}, timeout=10)
                html = r.text
            except:
                html = ""

    # Failure → empty DF
    if not html:
        return pd.DataFrame(columns=[
            "Title", "Price", "Location", "Bedrooms", "Bathrooms",
            "Area_sqft", "Latitude", "Longitude", "Image_URL", "URL"
        ])

    # ---- Local Ollama ----
    data = None
    if not ON_CLOUD:
        data = _ollama_extract(html)

    # ---- BeautifulSoup fallback ----
    if not data:
        data = _bs4_parse(html)

    df = pd.DataFrame(data)

    # Ensure columns exist
    for col in ["Title", "Price", "Location", "Bedrooms", "Bathrooms", "Area_sqft",
                "Latitude", "Longitude", "Image_URL", "URL"]:
        if col not in df.columns:
            df[col] = None

    # Geocode missing
    if GOOGLE_KEY:
        for i in df.index:
            if pd.isna(df.at[i, "Latitude"]) or pd.isna(df.at[i, "Longitude"]):
                lat, lon = get_lat_lon(df.at[i, "Location"])
                df.at[i, "Latitude"] = lat
                df.at[i, "Longitude"] = lon

    return df
