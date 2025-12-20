
import streamlit as st
import pandas as pd
from ai_scraper import scrape_properties

st.set_page_config(page_title="🏡 DataMorph AI", layout="wide")
st.title("🏡 DataMorph AI — Adaptive Real-Estate Dashboard")

# --------------------------------------------------
# Initialize state
# --------------------------------------------------
if "properties" not in st.session_state:
    st.session_state["properties"] = pd.DataFrame(columns=[
        "Title", "Price", "Location", "Bedrooms", "Bathrooms",
        "Area_sqft", "Latitude", "Longitude", "Image_URL", "URL"
    ])

# --------------------------------------------------
# Sidebar CRUD
# --------------------------------------------------
st.sidebar.header("📋 Manage Properties")
action = st.sidebar.selectbox("Action", ["None", "Add", "Edit", "Delete"])

if action == "Add":
    with st.sidebar.form("add"):
        title = st.text_input("Title")
        price = st.text_input("Price")
        location = st.text_input("Location")
        img = st.text_input("Image URL")
        submit = st.form_submit_button("➕ Add")

        if submit:
            st.session_state["properties"] = pd.concat([
                st.session_state["properties"],
                pd.DataFrame([{
                    "Title": title,
                    "Price": price,
                    "Location": location,
                    "Image_URL": img
                }])
            ], ignore_index=True)

elif action == "Delete" and not st.session_state["properties"].empty:
    t = st.sidebar.selectbox(
        "Select",
        st.session_state["properties"]["Title"].fillna("").tolist()
    )
    if st.sidebar.button("🗑 Delete"):
        st.session_state["properties"] = st.session_state["properties"][
            st.session_state["properties"]["Title"] != t
        ]

# --------------------------------------------------
# Scraper Inputs
# --------------------------------------------------
url = st.text_input("Paste Property URL")
upload = st.file_uploader("Or upload HTML file", ["html"])

if st.button("🚀 Scrape"):
    if url:
        df = scrape_properties(url)
    elif upload:
        html = upload.read().decode("utf-8", errors="ignore")
        df = scrape_properties(html, is_html=True)
    else:
        df = pd.DataFrame()

    st.session_state["properties"] = pd.concat(
        [st.session_state["properties"], df],
        ignore_index=True
    )

df = st.session_state["properties"]

# --------------------------------------------------
# Table
# --------------------------------------------------
st.subheader("📋 Properties")
st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# Image Gallery
# --------------------------------------------------
st.subheader("🏠 Property Gallery")

if not df.empty:
    cols = st.columns(3)
    i = 0
    for _, r in df.iterrows():
        img = r.get("Image_URL", "")
        if isinstance(img, str) and img.startswith("http"):
            with cols[i % 3]:
                st.image(img, caption=r.get("Title",""), use_column_width=True)
            i += 1

# --------------------------------------------------
# Map View
# --------------------------------------------------
st.subheader("🗺️ Map View")

if not df.empty and {"Latitude","Longitude"}.issubset(df.columns):
    st.map(df.rename(columns={
        "Latitude":"latitude",
        "Longitude":"longitude"
    })[["latitude","longitude"]])
