---
title: DataMorph AI
emoji: 🏡
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: "1.38.0"
app_file: streamlit_app.py
pinned: false
---

# 🏡 DataMorph AI — Adaptive Real-Estate Data Pipeline

DataMorph AI is an **end-to-end AI-assisted web scraping and analytics platform**
that extracts, cleans, enriches, and visualizes real-estate listings from
multiple property portals such as **MagicBricks, 99acres, and Housing.com**.

The system is **environment-aware** and automatically adapts to:
- 🖥️ **Local PC (Selenium + Browser)**
- ☁️ **Cloud Platforms (Hugging Face / Streamlit Cloud)**

---

## 🚀 Key Features

### 🔹 Adaptive Web Scraping
- **Local PC** → Selenium + Undetected Chrome (handles JS-heavy pages)
- **Cloud** → Requests + BeautifulSoup (safe & deployable)
- Optional **LLM-assisted parsing** (Ollama – local only)

### 🔹 Real-World ETL Pipeline
1. **Extract** raw HTML (URL or uploaded file)
2. **Transform** unstructured HTML → structured tabular data
3. **Enrich** with latitude/longitude (auto-read from HTML or geocoding)
4. **Load** into interactive dashboard (in-memory)

### 🔹 Smart Geocoding
- Reads **lat/lon directly from HTML** if present
- Falls back to **Google Maps API**
- Optional OpenStreetMap fallback

### 🔹 Interactive Streamlit Dashboard
- Property table view
- Image gallery (real listing images)
- Map visualization
- Add / Edit / Delete properties in-memory
- Upload saved HTML files
- Paste live URLs

---

## 🧱 Tech Stack

**Languages & Core**
- Python, Pandas, Requests, BeautifulSoup

**Web Scraping**
- Selenium, undetected-chromedriver (local)
- Requests (cloud-safe)

**AI / Parsing**
- Ollama (local LLM parsing – optional)

**Visualization**
- Streamlit, PyDeck, Maps

**APIs**
- Google Maps Geocoding API

**Deployment**
- Hugging Face Spaces
- Streamlit Cloud
- Local PC
-Deployment link:https://huggingface.co/spaces/rekhadolase2001/datamorph-ai-app
---

## 📁 Project Deployment:
https://huggingface.co/spaces/rekhadolase2001/datamorph-ai-app

