# loader_mysql.py
import os, json
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv() or None)
from sqlalchemy import create_engine, text
from datetime import datetime
import pandas as pd

DATABASE_URL = os.getenv("DATABASE_URL")
if isinstance(DATABASE_URL, str):
    DATABASE_URL = DATABASE_URL.strip() or None
if not DATABASE_URL:
    raise ValueError("Please set DATABASE_URL in .env")

engine = create_engine(DATABASE_URL, future=True)

def create_table_if_not_exists():
    create_sql = """
    CREATE TABLE IF NOT EXISTS properties (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(500),
        price_raw VARCHAR(200),
        price_inr FLOAT,
        location VARCHAR(255),
        details TEXT,
        url VARCHAR(1000) NOT NULL UNIQUE,
        image_url VARCHAR(1000),
        latitude DOUBLE,
        longitude DOUBLE,
        ai_features JSON,
        scraped_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    );
    """
    with engine.begin() as conn:
        conn.exec_driver_sql(create_sql)

def upsert_property(rec: dict):
    insert_sql = text("""
    INSERT INTO properties (title, price_raw, price_inr, location, details, url, image_url, latitude, longitude, ai_features, scraped_at)
    VALUES (:title, :price_raw, :price_inr, :location, :details, :url, :image_url, :latitude, :longitude, :ai_features, :scraped_at)
    ON DUPLICATE KEY UPDATE
      title = VALUES(title),
      price_raw = VALUES(price_raw),
      price_inr = VALUES(price_inr),
      location = VALUES(location),
      details = VALUES(details),
      image_url = VALUES(image_url),
      latitude = VALUES(latitude),
      longitude = VALUES(longitude),
      ai_features = VALUES(ai_features),
      scraped_at = VALUES(scraped_at),
      updated_at = CURRENT_TIMESTAMP;
    """)
    if isinstance(rec.get("ai_features"), (dict, list)):
        rec["ai_features"] = json.dumps(rec["ai_features"], ensure_ascii=False)
    with engine.begin() as conn:
        conn.execute(insert_sql, **rec)

def load_properties_df(df: pd.DataFrame):
    if df is None or df.empty:
        print("No records to load.")
        return
    create_table_if_not_exists()
    count = 0
    for _, r in df.iterrows():
        rec = {
            "title": r.get("title"),
            "price_raw": r.get("price_raw"),
            "price_inr": float(r.get("price_inr")) if r.get("price_inr") is not None else None,
            "location": r.get("location"),
            "details": r.get("details"),
            "url": r.get("url"),
            "image_url": r.get("image_url"),
            "latitude": float(r.get("latitude")) if r.get("latitude") is not None else None,
            "longitude": float(r.get("longitude")) if r.get("longitude") is not None else None,
            "ai_features": r.get("ai_features"),
            "scraped_at": r.get("scraped_at")
        }
        try:
            upsert_property(rec)
            count += 1
        except Exception as e:
            print("Error inserting row:", e)
    print(f"Inserted/updated {count} properties into MySQL.")
