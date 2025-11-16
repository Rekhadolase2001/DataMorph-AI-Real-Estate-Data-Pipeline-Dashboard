🏡 Datamorph AI — Real-Estate Data Ingestion & Analytics Pipeline

A cloud-deployable data engineering pipeline that extracts, cleans, enriches, and visualizes property listings from multiple real-estate platforms (MagicBricks, 99acres, Housing.com).

🚀 Features
✔ Smart Adaptive Scraper

Local PC: Selenium + BeautifulSoup + Ollama (LLM-assisted parsing)

Cloud (Streamlit/Render): Requests + API parsing (no Selenium/browser)

✔ ETL Workflow

Extract property HTML

Parse and normalize fields (title, price, bedrooms, area, location, URL, image)

Clean inconsistent values

Geocode addresses using Google Maps API

Handle duplicates and missing values

✔ Interactive Streamlit Dashboard

Property table view

Gallery view (with real listing images)

Map visualization (lat/lon)

Add/Edit/Delete in-memory entries

Upload HTML or scrape via URL

🧱 Tech Stack

Python, BeautifulSoup, Requests, Selenium, undetected-chromedriver,
Google Maps API, Pandas, Streamlit, PyDeck, Ollama LLM (local only)

📁 Project Structure
datamorph_ai/
│── ai_scraper.py          # Adaptive multi-site scraper (local/cloud)
│── streamlit_app.py       # Analytics dashboard UI
│── example_html/          # Sample HTML files (MagicBricks/99acres/Housing)
│── assets/                # Sample images for showcase/testing
│── requirements.txt
│── README.md
│── .env

🚀 How It Works

1️⃣ Paste a real-estate listing URL OR upload saved HTML
2️⃣ The scraper loads it (Selenium locally, Requests on cloud)
3️⃣ Data is parsed → cleaned → normalized
4️⃣ Missing coordinates are geocoded with Google Maps API
5️⃣ Results appear in dashboard:

Table

Image gallery

Map view

🌩 Deployment

Streamlit Cloud (works: Requests-only mode)

Render.com (recommended — full Selenium mode supported with Docker)

Local machine (full mode with Selenium + Ollama)

🎯 Why This Project Is Great for Data Engineering

Real-world ETL pipeline

Handles unstructured → structured data transformation

Environment-aware scraping architecture

Works with APIs, geospatial data, cloud deployments

Demonstrates automation, pipelines, and data quality validation

Includes dashboard for showcasing insights