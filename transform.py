<<<<<<< HEAD
# transform.py
import re
import pandas as pd
from datetime import datetime
from ai_parse import parse_with_openai  # optional, keep as-is
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Geocoder (OpenStreetMap Nominatim) – polite usage via rate limiter
geolocator = Nominatim(user_agent="datamorph-ai-geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=2, error_wait_seconds=2)

# Simple in-memory cache
_geocode_cache = {}

def parse_price_in_inr(price_raw):
    if not price_raw:
        return None
    s = str(price_raw).lower().replace(",", "").replace(" ", "")
    # crore
    m = re.search(r"([0-9]*\.?[0-9]+)\s*(cr|crore)", price_raw, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1e7
    # lakh / lac
    m = re.search(r"([0-9]*\.?[0-9]+)\s*(lakh|lac|lacs|l)", price_raw, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1e5
    # plain number
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", s)
    if m:
        try:
            return float(m.group(1))
        except:
            return None
    return None

def try_geocode_location(location_text):
    """Return (lat, lon) or (None, None). Uses simple cache to avoid repeated calls."""
    if not location_text:
        return None, None
    key = location_text.strip().lower()
    if key in _geocode_cache:
        return _geocode_cache[key]
    try:
        loc = geocode(location_text)
        if loc:
            coords = (loc.latitude, loc.longitude)
        else:
            coords = (None, None)
    except Exception as e:
        print("Geocode error:", e)
        coords = (None, None)
    _geocode_cache[key] = coords
    return coords

def transform_properties(df):
    if df is None or df.empty:
        return df
    df = df.copy()
    # price numeric
    if "price_raw" in df.columns:
        df["price_inr"] = df["price_raw"].apply(parse_price_in_inr)
    else:
        df["price_inr"] = None

    df["scraped_at"] = pd.to_datetime(datetime.utcnow())
    df["ai_features"] = None
    # new columns
    df["latitude"] = None
    df["longitude"] = None

    for i, row in df.iterrows():
        # optional AI parsing from title+details
        text = (row.get("title") or "") + ". " + (row.get("details") or "")
        try:
            parsed = parse_with_openai(text)
        except Exception:
            parsed = None
        df.at[i, "ai_features"] = parsed

        # geocode location -> lat/lon
        loc_text = row.get("location") or ""
        lat, lon = try_geocode_location(loc_text)
        df.at[i, "latitude"] = lat
        df.at[i, "longitude"] = lon

    keep = ["title", "price_raw", "price_inr", "location", "details", "url", "image_url", "ai_features", "latitude", "longitude", "scraped_at"]
    existing = [c for c in keep if c in df.columns]
    return df[existing]
=======
# transform.py
import re
import pandas as pd
from datetime import datetime
from ai_parse import parse_with_openai  # optional, keep as-is
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Geocoder (OpenStreetMap Nominatim) – polite usage via rate limiter
geolocator = Nominatim(user_agent="datamorph-ai-geocoder")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1, max_retries=2, error_wait_seconds=2)

# Simple in-memory cache
_geocode_cache = {}

def parse_price_in_inr(price_raw):
    if not price_raw:
        return None
    s = str(price_raw).lower().replace(",", "").replace(" ", "")
    # crore
    m = re.search(r"([0-9]*\.?[0-9]+)\s*(cr|crore)", price_raw, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1e7
    # lakh / lac
    m = re.search(r"([0-9]*\.?[0-9]+)\s*(lakh|lac|lacs|l)", price_raw, re.IGNORECASE)
    if m:
        return float(m.group(1)) * 1e5
    # plain number
    m = re.search(r"([0-9]+(?:\.[0-9]+)?)", s)
    if m:
        try:
            return float(m.group(1))
        except:
            return None
    return None

def try_geocode_location(location_text):
    """Return (lat, lon) or (None, None). Uses simple cache to avoid repeated calls."""
    if not location_text:
        return None, None
    key = location_text.strip().lower()
    if key in _geocode_cache:
        return _geocode_cache[key]
    try:
        loc = geocode(location_text)
        if loc:
            coords = (loc.latitude, loc.longitude)
        else:
            coords = (None, None)
    except Exception as e:
        print("Geocode error:", e)
        coords = (None, None)
    _geocode_cache[key] = coords
    return coords

def transform_properties(df):
    if df is None or df.empty:
        return df
    df = df.copy()
    # price numeric
    if "price_raw" in df.columns:
        df["price_inr"] = df["price_raw"].apply(parse_price_in_inr)
    else:
        df["price_inr"] = None

    df["scraped_at"] = pd.to_datetime(datetime.utcnow())
    df["ai_features"] = None
    # new columns
    df["latitude"] = None
    df["longitude"] = None

    for i, row in df.iterrows():
        # optional AI parsing from title+details
        text = (row.get("title") or "") + ". " + (row.get("details") or "")
        try:
            parsed = parse_with_openai(text)
        except Exception:
            parsed = None
        df.at[i, "ai_features"] = parsed

        # geocode location -> lat/lon
        loc_text = row.get("location") or ""
        lat, lon = try_geocode_location(loc_text)
        df.at[i, "latitude"] = lat
        df.at[i, "longitude"] = lon

    keep = ["title", "price_raw", "price_inr", "location", "details", "url", "image_url", "ai_features", "latitude", "longitude", "scraped_at"]
    existing = [c for c in keep if c in df.columns]
    return df[existing]
>>>>>>> d243cc566e41a5b7d6dc490e4bc6bcce2c288314
