# streamlit_app.py
import streamlit as st
import pandas as pd
import io
from PIL import Image
import pydeck as pdk
import os

# ==========================================================
#  APP SETUP
# ==========================================================
st.set_page_config(page_title="🏡 DataMorph AI Dashboard", layout="wide", page_icon="🏠")
st.title("🏡 DataMorph AI — Property Manager (CSV Version)")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
CSV_PATH = "data/properties.csv"

# ==========================================================
#  DATA LOADING
# ==========================================================
@st.cache_data
def load_data():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame(columns=[
            "id","title","price_raw","price_inr","location","details",
            "url","image_url","latitude","longitude"
        ])
    return df

def save_data(df):
    df.to_csv(CSV_PATH, index=False)

df = load_data()

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
            new_id = int(df["id"].max() + 1) if not df.empty else 1
            new_row = {
                "id": new_id,
                "title": title,
                "price_raw": price_raw,
                "price_inr": price_inr,
                "location": location,
                "details": details,
                "url": url,
                "image_url": image_url,
                "latitude": latitude,
                "longitude": longitude,
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df)
            st.success("✅ Property added!")
            st.cache_data.clear()

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
            new_lat = st.number_input("Latitude", -90.0, 90.0, row["latitude"])
            new_lon = st.number_input("Longitude", -180.0, 180.0, row["longitude"])
            new_image_url = st.text_input("Image URL", row["image_url"])
            update_btn = st.form_submit_button("💾 Update Property")

            if update_btn:
                df.loc[df["id"] == edit_id, :] = [
                    edit_id, new_title, new_price_raw, new_price_inr, new_location,
                    new_details, new_url, new_image_url, new_lat, new_lon
                ]
                save_data(df)
                st.success(f"✅ Property {edit_id} updated!")
                st.cache_data.clear()
    elif edit_id > 0:
        st.warning("No such property ID found.")

# -------- Delete property --------
with st.sidebar.expander("🗑 Delete Property", expanded=False):
    del_id = st.number_input("Enter Property ID to Delete", min_value=0, key="del_id")
    if st.button("Delete Property"):
        df = df[df["id"] != del_id]
        save_data(df)
        st.warning(f"Deleted property {del_id}")
        st.cache_data.clear()

# ==========================================================
#  MAIN PAGE CONTENT
# ==========================================================
st.subheader(f"🏠 Available Properties — {len(df)} total")

left, right = st.columns([1.2, 1])

with left:
    st.dataframe(df[["id","title","price_raw","location","price_inr"]], use_container_width=True)
    sel_id = st.number_input("🔍 View Property ID", min_value=0)
    if sel_id in df["id"].values:
        row = df[df["id"] == sel_id].iloc[0]
        st.markdown(f"### {row['title']}")
        st.write(f"💰 {row['price_raw']} — ₹{row['price_inr']:,}")
        st.write(f"📍 {row['location']}")
        st.write(f"📝 {row['details']}")
        if row["image_url"]:
            st.image(row["image_url"], caption=row["title"], use_container_width=True)
        if row["latitude"] and row["longitude"]:
            st.map(pd.DataFrame([[row["latitude"], row["longitude"]]], columns=["lat","lon"]))

with right:
    st.markdown("### 🖼 Gallery")
    gallery = df.dropna(subset=["image_url"], how="all")
    if not gallery.empty:
        cols = st.columns(3)
        for i, (_, g) in enumerate(gallery.head(9).iterrows()):
            with cols[i % 3]:
                st.image(g["image_url"], use_container_width=True)
    else:
        st.info("No images yet.")

# ==========================================================
#  MAP VISUALIZATION (COLORED)
# ==========================================================
if not df.empty and "latitude" in df.columns:
    st.subheader("🌎 Interactive Price Map")
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_color="[255*(price_inr/df.price_inr.max()), 100, 150, 180]",
        get_radius=80,
    )
    st.pydeck_chart(
        pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v10",
            initial_view_state=pdk.ViewState(
                latitude=df["latitude"].mean(),
                longitude=df["longitude"].mean(),
                zoom=10,
                pitch=0,
            ),
            layers=[layer],
        )
    )
