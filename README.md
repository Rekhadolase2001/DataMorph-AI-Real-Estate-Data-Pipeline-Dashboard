# 🧠 DataMorph AI — Real Estate Data Engineering Dashboard

A **Streamlit-powered AI Data Engineering project** that scrapes, stores, and visualizes real estate listings (like MagicBricks) with **ETL automation**, **MySQL integration**, and an **interactive dashboard** for insights and property management.

---

## 🚀 Features

✅ **ETL Pipeline** — Extract property data → Transform using Pandas → Load into MySQL
✅ **Interactive Streamlit Dashboard** — Filter, search, view properties with images & coordinates
✅ **Upload & Delete Listings** — Add new listings manually or remove old ones
✅ **Map Visualization** — Shows property locations on an interactive map (Pydeck)
✅ **AI JSON Storage** — Each property’s details are stored with AI metadata (`ai_features`)
✅ **Image Gallery** — View uploaded images for each property
✅ **Fully Deployable** — Ready for Streamlit Cloud or local deployment

---

## 🧩 Project Structure

```
datamorph_ai/
│
├── streamlit_app.py         # Main Streamlit dashboard
├── etl_script.py            # ETL pipeline for scraping & transforming data
├── database.py              # Database connection (SQLAlchemy + MySQL)
├── utils.py                 # Helper functions for map, uploads, etc.
├── .env                     # Environment variables (DB URL, debug settings)
├── requirements.txt         # Dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/datamorph_ai.git
cd datamorph_ai
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate     # On Windows
source venv/bin/activate  # On macOS/Linux
```

### 3️⃣ Install Requirements

```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up `.env`

Copy the following into your `.env` file:

```
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/ai_scraper_db
APP_NAME=DataMorph_AI
DEBUG=True
DEFAULT_LAT=20.5937
DEFAULT_LON=78.9629
IMAGE_UPLOAD_DIR=images/
```

### 5️⃣ Run Locally

```bash
streamlit run streamlit_app.py
```

---

## 🌐 Deployment (Streamlit Cloud)

1. Push your full project (with `.py` and `requirements.txt`) to a **public GitHub repo**.
2. Visit [https://share.streamlit.io](https://share.streamlit.io).
3. Sign in with your GitHub account → select your repo and `streamlit_app.py` as entrypoint.
4. In **Settings → Secrets**, add:

   ```
   DATABASE_URL = "mysql+pymysql://your-db-user:your-db-pass@your-host:3306/ai_scraper_db"
   APP_NAME = "DataMorph_AI"
   ```
5. Click **Deploy** 🎉

---

## 🗺️ Map & Gallery

Each property supports:

* **Latitude/Longitude** for map visualization.
* **Image upload** (stored as binary or via image URL).

Example property:

| Title          | Location | Price    | Latitude | Longitude | Image |
| -------------- | -------- | -------- | -------- | --------- | ----- |
| 2 BHK in Powai | Mumbai   | ₹1.05 Cr | 19.1197  | 72.9052   | ✅     |

---

## 📸 Sample Screenshots

Add your screenshots in a folder called `/screenshots` in your GitHub repo, then update these markdowns:

### 🏠 Dashboard Home

![Dashboard](screenshots/dashboard_home.png)

### 🖼️ Property Details View

![Property Details](screenshots/property_details.png)

### 🌍 Map Visualization

![Map](screenshots/map_view.png)

### 📤 Upload Property Form

![Upload Form](screenshots/upload_form.png)

### 🧹 Delete Property Option

![Delete Property](screenshots/delete_property.png)

---

## 👩‍💻 Tech Stack

* **Frontend:** Streamlit
* **Backend:** Python, Pandas, SQLAlchemy
* **Database:** MySQL
* **Visualization:** Pydeck (Map), Streamlit UI
* **Hosting:** Streamlit Community Cloud

---

## 🧰 Future Enhancements

* Cloud MySQL (AWS RDS / Google Cloud SQL)
* Automated web scraping using Airflow or GitHub Actions
* Power BI / Tableau dashboard integration
* AI-powered property description generator

---

## 💡 Author

**Rekha — Data Engineer | Data Analyst | AI Enthusiast**
📧 [Your Email or LinkedIn]
🌐 [Add your portfolio or GitHub link]

---

### ⭐ Don’t forget to star this repo if you found it useful!

