# streamlit_app.py 
"""
Streamlit front-end for DataMorph AI (no CSV — in-memory)
- Paste URL or upload saved HTML
- Click Scrape -> shows Available Properties, Gallery, Map
- Sidebar: Add/Edit/Delete in-memory properties
"""

import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import pydeck as pdk

load_dotenv()

st.set_page_config(page_title="🏡 DataMorph AI Dashboard", layout="wide", page_icon="🏠")
st.title("🏡 DataMorph AI — Multi-Site Property Manager")

# ----------------------------------------------------------
# Initialize in-memory store
# ----------------------------------------------------------
if "properties" not in st.session_state:
    st.session_state["properties"] = pd.DataFrame(columns=[
        "Title", "Price", "Location", "Bedrooms", "Bathrooms",
        "Area_sqft", "Latitude", "Longitude", "Image_URL", "URL"
    ])

# ----------------------------------------------------------
# Sidebar: Add / Edit / Delete
# ----------------------------------------------------------
st.sidebar.header("📋 Manage Properties (in-memory)")

action = st.sidebar.selectbox("Action", ["None", "Add", "Edit", "Delete"])

# ---------- ADD ----------
if action == "Add":
    with st.sidebar.form("add_form"):
        title = st.text_input("Title")
        price = st.text_input("Price")
        location = st.text_input("Location")
        beds = st.number_input("Bedrooms", 0, 20, 0)
        baths = st.number_input("Bathrooms", 0, 20, 0)
        area = st.text_input("Area (sqft)")
        lat = st.text_input("Latitude")
        lon = st.text_input("Longitude")
        img = st.text_input("Image URL")
        url = st.text_input("Listing URL")
        submit_add = st.form_submit_button("➕ Add Property")

        if submit_add:
            new_row = {
                "Title": title,
                "Price": price,
                "Location": location,
                "Bedrooms": beds,
                "Bathrooms": baths,
                "Area_sqft": area,
                "Latitude": lat,
                "Longitude": lon,
                "Image_URL": img,
                "URL": url
            }
            st.session_state["properties"] = pd.concat(
                [st.session_state["properties"], pd.DataFrame([new_row])],
                ignore_index=True
            )
            st.sidebar.success("✅ Property added (in memory).")

# ---------- EDIT ----------
elif action == "Edit" and not st.session_state["properties"].empty:
    titles = st.session_state["properties"]["Title"].fillna("").tolist()
    selected = st.sidebar.selectbox("Select property to edit", [""] + titles)

    if selected:
        idx = st.session_state["properties"][st.session_state["properties"]["Title"] == selected].index[0]
        new_price = st.sidebar.text_input("New Price", value=st.session_state["properties"].at[idx, "Price"])

        if st.sidebar.button("💾 Save"):
            st.session_state["properties"].at[idx, "Price"] = new_price
            st.sidebar.success("✅ Updated")

# ---------- DELETE ----------
elif action == "Delete" and not st.session_state["properties"].empty:
    titles = st.session_state["properties"]["Title"].fillna("").tolist()
    to_del = st.sidebar.selectbox("Select property to delete", [""] + titles)

    if to_del and st.sidebar.button("🗑 Delete"):
        st.session_state["properties"] = st.session_state["properties"][
            st.session_state["properties"]["Title"] != to_del
        ]
        st.sidebar.success("✅ Deleted")

# ----------------------------------------------------------
# Scraper Inputs
# ----------------------------------------------------------
st.subheader("🌐 AI Web Scraper — MagicBricks / 99acres / Housing.com")

col1, col2 = st.columns([3, 1])
with col1:
    site_url = st.text_input("Paste a property listing page URL:")
with col2:
    go_btn = st.button("🚀 Scrape (live)")

uploaded_html = st.file_uploader("Or upload a saved HTML file", type=["html", "htm"])

# ----------------------------------------------------------
# Run Scraper (URL)
# ----------------------------------------------------------
if go_btn and site_url.strip():
    with st.spinner("Scraping... this may take a few seconds"):
        from ai_scraper import scrape_properties

        try:
            df_result = scrape_properties(site_url.strip(), is_html=False)

            if df_result.empty:
                st.warning("⚠️ No data found. Try uploading HTML or use different site.")
            else:
                cur = st.session_state["properties"]
                combined = pd.concat([cur, df_result], ignore_index=True)
                combined = combined.drop_duplicates(subset=["Title", "Location"], keep="last")
                st.session_state["properties"] = combined.reset_index(drop=True)

                st.success(f"✅ Extracted {len(df_result)} properties.")
                st.dataframe(df_result)

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ----------------------------------------------------------
# Run Scraper (Uploaded HTML)
# ----------------------------------------------------------
if uploaded_html is not None:
    html_text = uploaded_html.read().decode("utf-8", errors="ignore")
    with st.spinner("Parsing uploaded HTML..."):
        from ai_scraper import scrape_properties

        try:
            df_result = scrape_properties(html_text, is_html=True)

            if df_result.empty:
                st.warning("⚠️ No data found in uploaded HTML.")
            else:
                cur = st.session_state["properties"]
                combined = pd.concat([cur, df_result], ignore_index=True)
                combined = combined.drop_duplicates(subset=["Title", "Location"], keep="last")
                st.session_state["properties"] = combined.reset_index(drop=True)

                st.success(f"✅ Extracted {len[df_result]} properties.")
                st.dataframe(df_result)

        except Exception as e:
            st.error(f"❌ Error parsing HTML: {e}")

# ----------------------------------------------------------
# Available Properties
# ----------------------------------------------------------
df = st.session_state["properties"]
st.subheader(f"🧾 Available Properties — {len(df)} total")

if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No properties yet. Scrape a URL or upload HTML.")

# ----------------------------------------------------------
# Property Gallery
# ----------------------------------------------------------
st.subheader("🏠 Property Gallery")

if not df.empty:
    gallery = df.head(6)
    cols = st.columns(3)

    for i, (_, g) in enumerate(gallery.iterrows()):
        with cols[i % 3]:
            img = g.get("Image_URL", "")
            if isinstance(img, str) and img.startswith("http"):
                st.image(img, caption=f"{g.get('Title','')} — {g.get('Price','')}", use_column_width=True)
            else:
                st.info(f"No image for: {g.get('Title','(no title)')}")

# ----------------------------------------------------------
# Map View
# ----------------------------------------------------------
st.subheader("🗺️ Map View")

if not df.empty:
    df_geo = df.copy()
    df_geo.columns = df_geo.columns.str.lower()

    lat_col = next((c for c in df_geo.columns if "lat" in c), None)
    lon_col = next((c for c in df_geo.columns if "lon" in c), None)

    if lat_col and lon_col:
        df_geo[lat_col] = pd.to_numeric(df_geo[lat_col], errors="coerce")
        df_geo[lon_col] = pd.to_numeric(df_geo[lon_col], errors="coerce")
        df_geo = df_geo.dropna(subset=[lat_col, lon_col])

        if not df_geo.empty:
            st.map(df_geo.rename(columns={lat_col: "latitude", lon_col: "longitude"})[["latitude", "longitude"]])
        else:
            st.warning("No valid coordinates found.")

    else:
        st.warning("Latitude/Longitude columns missing.")
