# geo_helper.py — Handles location coordinates using Google Maps API
import os
import requests
from dotenv import load_dotenv

# Load keys
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_lat_lon(address: str):
    """
    Get latitude and longitude for a given address using Google Maps API.

    Parameters:
        address (str): The property address or location text.
    
    Returns:
        (lat, lon): Tuple of (latitude, longitude) as floats, or (None, None) if not found.
    """
    if not GOOGLE_KEY:
        print("⚠️ GOOGLE_MAPS_API_KEY missing in .env")
        return None, None

    if not address or not isinstance(address, str):
        return None, None

    try:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_KEY}"
        resp = requests.get(url)
        data = resp.json()

        if data.get("status") == "OK" and len(data["results"]) > 0:
            loc = data["results"][0]["geometry"]["location"]
            return loc["lat"], loc["lng"]
        else:
            print(f"⚠️ Geocoding failed for: {address}")
            return None, None
    except Exception as e:
        print(f"⚠️ Error in geocoding: {e}")
        return None, None
