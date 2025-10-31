# scraper.py
"""
MagicBricks static scraper (requests + BeautifulSoup).
Extracts: title, price_raw, location, details, url, image_url
"""

import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; DataMorphAI/1.0)"}
BASE_URL = "https://www.magicbricks.com"

def fetch(url, wait=1.0):
    time.sleep(wait)
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def try_select_text(card, selectors):
    for sel in selectors:
        el = card.select_one(sel)
        if el:
            t = el.get_text(separator=" ", strip=True)
            if t:
                return t
    return None

def parse_listing_card(card):
    """Extract fields including image URL."""
    title = try_select_text(card, ["h2 > a", ".mb-srp__card__title a", ".srpTuple__tupleTitle a"])
    price_raw = try_select_text(card, [".mb-srp__card__price", ".srpTuple__tuplePrice", ".price"])
    location = try_select_text(card, [".mb-srp__card__locality", ".srpTuple__tupleLocality", ".localityText"])
    details = try_select_text(card, [".mb-srp__card__desc", ".propAttr", ".propDetails"])

    # IMAGE extraction
    image_url = None
    img = card.select_one("img")
    if img:
        # common attributes: src, data-src, data-lazy
        image_url = img.get("src") or img.get("data-src") or img.get("data-lazy") or None
        if image_url and image_url.startswith("/"):
            image_url = urljoin(BASE_URL, image_url)

    # link extraction (common patterns)
    link_tag = card.select_one("a[href*='/property-details'], a[href*='/property-for-sale'], a[href*='/property-rent']")
    url = urljoin(BASE_URL, link_tag["href"]) if link_tag and link_tag.get("href") else None

    return {
        "title": title,
        "price_raw": price_raw,
        "location": location,
        "details": details,
        "url": url,
        "image_url": image_url
    }

def find_cards(soup):
    cards = soup.select(".mb-srp__card, .srpTuple, .list-card, .srp-listing")
    if not cards:
        cards = soup.select("li.clearfix, article")
    return cards

def scrape_search_page(url, max_items=50):
    print(f"Scraping: {url}")
    html = fetch(url)
    soup = BeautifulSoup(html, "lxml")
    cards = find_cards(soup)
    rows = []
    for c in cards:
        rec = parse_listing_card(c)
        if rec.get("title") or rec.get("url"):
            rows.append(rec)
        if len(rows) >= max_items:
            break
    df = pd.DataFrame(rows)
    print(f"Scraped {len(df)} listings")
    return df

if __name__ == "__main__":
    test = "https://www.magicbricks.com/property-for-sale-in-bangalore-pppfs"
    df = scrape_search_page(test, max_items=8)
    print(df.head())