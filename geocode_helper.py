# geocode_helper.py
import requests
import pandas as pd
import time

def geocode_address(address):
    if not address or pd.isna(address):
        return None, None
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1}
        headers = {"User-Agent": "DataMorphAI/1.0 (contact: you@example.com)"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        return None, None
    return None, None

def add_lat_lon_to_df(df: pd.DataFrame, address_col="Location") -> pd.DataFrame:
    df = df.copy()
    if "Latitude" in df.columns and "Longitude" in df.columns:
        # if present but many missing, fill only missing
        missing_lat = df["Latitude"].isna().sum() if "Latitude" in df else len(df)
        if missing_lat == 0:
            return df
    df["Latitude"] = df.get("Latitude", None)
    df["Longitude"] = df.get("Longitude", None)
    for i, row in df.iterrows():
        if not row.get("Latitude") or not row.get("Longitude"):
            lat, lon = geocode_address(row.get(address_col, ""))
            df.at[i, "Latitude"] = lat
            df.at[i, "Longitude"] = lon
            time.sleep(1)  # respect rate limit
    return df
