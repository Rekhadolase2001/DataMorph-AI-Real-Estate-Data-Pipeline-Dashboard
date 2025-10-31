# streamlit_app.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os, io
from PIL import Image
import pydeck as pdk

# --- Load env and connect to MySQL ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# --- Streamlit setup ---
st.set_page_config(page_title="🏡 DataMorph AI Dashboard", layout="wide", page_icon="🏠")
st.title("🏡 DataMorph AI — Property Manager")

# --- Load data ---
@st.cache_data
def load_data():
    query = """
    SELECT id,title,price_raw,price_inr,location,details,url,
           image_url,image_data,image_mime,latitude,longitude
    FROM properties ORDER BY scraped_at DESC;
    """
    return pd.read_sql(query, engine)

def refresh_data():
    st.cache_data.clear()
    return load_data()

df = load_data()

# --- Helper to render image ---
def render_image(row):
    if row["image_data"] is not None:
        img = Image.open(io.BytesIO(row["image_data"]))
        st.image(img, caption=row["title"], use_container_width=True)
    elif row["image_url"]:
        st.image(row["image_url"], caption=row["title"], use_container_width=True)

# ==========================================================
#  SIDEBAR CONTROLS
# ==========================================================

st.sidebar.header("📋 Manage Properties")

# -------- Add new property --------
with st.sidebar.expander("➕ Add New Property", expanded=False):
    with st.form("add_form"):
        title = st.text_input("Title")
        price_raw = st.text_input("Price (₹ 80 Lac etc)")
        price_inr = st.number_input("Price in INR", 0.0)
        location = st.text_input("Location")
        details = st.text_area("Details")
        url = st.text_input("URL")
        image_upload = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        image_url = st.text_input("Image URL (optional)")
        latitude = st.number_input("Latitude", -90.0, 90.0, 0.0)
        longitude = st.number_input("Longitude", -180.0, 180.0, 0.0)
        submit_add = st.form_submit_button("✅ Add Property")

        if submit_add:
            image_data, mime = None, None
            if image_upload:
                image_data = image_upload.read()
                mime = image_upload.type
            with engine.begin() as conn:
                conn.execute(text("""
                    INSERT INTO properties 
                    (title,price_raw,price_inr,location,details,url,image_url,
                     image_data,image_mime,latitude,longitude,scraped_at)
                    VALUES (:t,:pr,:pi,:l,:d,:u,:iu,:id,:im,:lat,:lon,NOW())
                """), {
                    "t": title, "pr": price_raw, "pi": price_inr,
                    "l": location, "d": details, "u": url,
                    "iu": image_url, "id": image_data, "im": mime,
                    "lat": latitude, "lon": longitude
                })
            st.success("✅ Property added!")
            df = refresh_data()

# -------- Edit existing property --------
with st.sidebar.expander("✏️ Edit Property", expanded=False):
    edit_id = st.number_input("Enter Property ID to Edit", min_value=0)
    if edit_id > 0 and edit_id in df["id"].values:
        row = df[df["id"] == edit_id].iloc[0]
        with st.form("edit_form"):
            new_title = st.text_input("Title", row["title"])
            new_price_raw = st.text_input("Price Raw", row["price_raw"])
            new_price_inr = st.number_input("Price INR", value=row["price_inr"])
            new_location = st.text_input("Location", row["location"])
            new_details = st.text_area("Details", row["details"])
            new_url = st.text_input("URL", row["url"])
            new_lat = st.number_input("Latitude", -90.0, 90.0, row["latitude"] if row["latitude"] else 0.0)
            new_lon = st.number_input("Longitude", -180.0, 180.0, row["longitude"] if row["longitude"] else 0.0)
            new_image = st.file_uploader("Replace Image (optional)", type=["jpg","jpeg","png"])
            update_btn = st.form_submit_button("💾 Update Property")

            if update_btn:
                image_data, mime = row["image_data"], row["image_mime"]
                if new_image:
                    image_data = new_image.read()
                    mime = new_image.type
                with engine.begin() as conn:
                    conn.execute(text("""
                        UPDATE properties SET
                        title=:t, price_raw=:pr, price_inr=:pi, location=:l, details=:d,
                        url=:u, latitude=:lat, longitude=:lon, image_data=:id, image_mime=:im
                        WHERE id=:idn
                    """), {
                        "t": new_title, "pr": new_price_raw, "pi": new_price_inr,
                        "l": new_location, "d": new_details, "u": new_url,
                        "lat": new_lat, "lon": new_lon,
                        "id": image_data, "im": mime, "idn": edit_id
                    })
                st.success(f"✅ Property {edit_id} updated!")
                df = refresh_data()
    elif edit_id > 0:
        st.warning("No such property ID found.")

# -------- Delete property --------
with st.sidebar.expander("🗑 Delete Property", expanded=False):
    del_id = st.number_input("Enter Property ID to Delete", min_value=0, key="del_id")
    if st.button("Delete Property"):
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM properties WHERE id=:i"), {"i": del_id})
        st.warning(f"Deleted property {del_id}")
        df = refresh_data()

# ==========================================================
#  MAIN PAGE CONTENT
# ==========================================================

st.subheader(f"🏠 Available Properties — {len(df)} total")

# Left: Table + Details
left, right = st.columns([1.2, 1])

with left:
    st.dataframe(df[["id","title","price_raw","location","price_inr"]], use_container_width=True)
    sel_id = st.number_input("🔍 View Property ID", min_value=0)
    if sel_id in df["id"].values:
        row = df[df["id"] == sel_id].iloc[0]
        st.markdown(f"### {row['title']}")
        st.write(f"💰 {row['price_raw']} — {row['price_inr']:,} INR")
        st.write(f"📍 {row['location']}")
        st.write(f"📝 {row['details']}")
        render_image(row)
        if row["latitude"] and row["longitude"]:
            st.map(pd.DataFrame([[row["latitude"], row["longitude"]]], columns=["lat","lon"]))

with right:
    st.markdown("### 🖼 Gallery")
    gallery = df.dropna(subset=["image_data","image_url"], how="all")
    if not gallery.empty:
        cols = st.columns(3)
        for i, (_, g) in enumerate(gallery.head(9).iterrows()):
            with cols[i % 3]:
                if g["image_data"]:
                    st.image(Image.open(io.BytesIO(g["image_data"])), use_container_width=True)
                elif g["image_url"]:
                    st.image(g["image_url"], use_container_width=True)
    else:
        st.info("No images yet.")

