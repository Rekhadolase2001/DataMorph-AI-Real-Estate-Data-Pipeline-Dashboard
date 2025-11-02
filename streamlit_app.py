# streamlit_app.py
import streamlit as st
import pandas as pd
import os
import pydeck as pdk
from PIL import Image
import io

# ==========================================================
#  APP SETUP
# ==========================================================

st.set_page_config(
    page_title="🏡 DataMorph AI Dashboard",
    layout="wide",
    page_icon="🏠"
)

st.title("🏡 DataMorph AI — Property Manager")


# Ensure data directory exists
os.makedirs("data", exist_ok=True)
CSV_PATH = "data/properties.csv"

# ==========================================================
#  DATA LOADING
# ==========================================================
@st.cache_data
def load_data():
    os.makedirs("data", exist_ok=True)
    CSV_PATH = "data/properties.csv"

    # If CSV exists → load it
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)

    # If CSV missing → create with default sample data
    else:
        sample_data = """id,title,price_raw,price_inr,location,details,url,image_url,latitude,longitude
1,2 BHK Apartment in Whitefield, Bangalore,₹ 75 Lac,7500000,Whitefield, Bangalore,Spacious 2BHK flat, 1200 sqft, semi-furnished, close to IT hub.,https://www.magicbricks.com/propertyDetails/2bhk-Whitefield-101,https://images.unsplash.com/photo-1600607687644-aac4c3eac7f4,12.9698,77.7499
2,3 BHK Villa in Sarjapur Road, Bangalore,₹ 1.2 Cr,12000000,Sarjapur Road, Bangalore,Independent villa with 3 bedrooms, 1800 sqft, private garden.,https://www.magicbricks.com/propertyDetails/3bhk-Sarjapur-102,https://images.unsplash.com/photo-1613490493576-7fde63acd811,12.8608,77.7815
3,1 BHK Apartment in Hinjewadi, Pune,₹ 38 Lac,3800000,Hinjewadi, Pune,Affordable 1BHK near Phase 2 IT Park, 650 sqft.,https://www.magicbricks.com/propertyDetails/1bhk-Hinjewadi-103,https://images.unsplash.com/photo-1560448204-e02f11c3d0e2,18.5974,73.7187
4,Office Space in Cyber City, Gurgaon,₹ 2.5 Cr,25000000,Cyber City, Gurgaon,Fully furnished office, 2500 sqft, near metro station.,https://www.magicbricks.com/propertyDetails/office-Gurgaon-104,https://images.unsplash.com/photo-1600585154340-be6161a56a0c,28.4943,77.0880
5,2 BHK Flat in Powai, Mumbai,₹ 1.05 Cr,10500000,Powai, Mumbai,Lake-view 2BHK apartment, 980 sqft, modern amenities.,https://www.magicbricks.com/propertyDetails/2bhk-Powai-105,https://images.unsplash.com/photo-1580587771525-78b9dba3b914,19.1177,72.9056
"""
        from io import StringIO
        df = pd.read_csv(StringIO(sample_data))
        df.to_csv(CSV_PATH, index=False)
        st.warning("⚠️ No properties.csv found — created sample data automatically.")

    return df


# ==========================================================
#  LOAD INITIAL DATA & SAVE FUNCTION
# ==========================================================
df = load_data()

def save_data(updated_df):
    """Save updated property data to CSV"""
    updated_df.to_csv(CSV_PATH, index=False)


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
    st.dataframe(df[["id", "title", "price_raw", "location", "price_inr"]], use_container_width=True)
    sel_id = st.number_input("🔍 View Property ID", min_value=0)
    if sel_id in df["id"].values:
        row = df[df["id"] == sel_id].iloc[0]
        st.markdown(f"### {row['title']}")
        st.write(f"💰 {row['price_raw']} — ₹{row['price_inr']:,}")
        st.write(f"📍 {row['location']}")
        st.write(f"📝 {row['details']}")
        if row["image_url"]:
            st.image(row["image_url"], caption=row["title"])

        if row["latitude"] and row["longitude"]:
            st.map(pd.DataFrame([[row["latitude"], row["longitude"]]], columns=["lat", "lon"]))

with right:
    # --- Property Gallery Section ---
    st.subheader("🏠 Property Gallery")

gallery = df.copy()

if not gallery.empty:
    cols = st.columns(3)
    for i, (_, g) in enumerate(gallery.head(9).iterrows()):
        with cols[i % 3]:
            img_url = g.get("image_url", "")
            title = g.get("title", "Property")
            location = g.get("location", "")
            price = g.get("price_raw", "")

            # ✅ Check if valid image URL or file
            if img_url and (img_url.startswith("http") or os.path.exists(img_url)):
                try:
                    st.image(img_url, caption=f"{title}\n{location}\n{price}")
                except Exception:
                    st.warning("⚠️ Unable to load image")
            else:
                st.warning("📷 Image not available")

            
else:
    st.info("No property images to show yet.")


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
    os.makedirs("data", exist_ok=True)
    CSV_PATH = "data/properties.csv"

    # If CSV exists → load it
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)

    # If CSV missing → create with default sample data
    else:
        sample_data = """id,title,price_raw,price_inr,location,details,url,image_url,latitude,longitude
1,2 BHK Apartment in Whitefield, Bangalore,₹ 75 Lac,7500000,Whitefield, Bangalore,Spacious 2BHK flat, 1200 sqft, semi-furnished, close to IT hub.,https://www.magicbricks.com/propertyDetails/2bhk-Whitefield-101,https://images.unsplash.com/photo-1600607687644-aac4c3eac7f4,12.9698,77.7499
2,3 BHK Villa in Sarjapur Road, Bangalore,₹ 1.2 Cr,12000000,Sarjapur Road, Bangalore,Independent villa with 3 bedrooms, 1800 sqft, private garden.,https://www.magicbricks.com/propertyDetails/3bhk-Sarjapur-102,https://images.unsplash.com/photo-1613490493576-7fde63acd811,12.8608,77.7815
3,1 BHK Apartment in Hinjewadi, Pune,₹ 38 Lac,3800000,Hinjewadi, Pune,Affordable 1BHK near Phase 2 IT Park, 650 sqft.,https://www.magicbricks.com/propertyDetails/1bhk-Hinjewadi-103,https://images.unsplash.com/photo-1560448204-e02f11c3d0e2,18.5974,73.7187
4,Office Space in Cyber City, Gurgaon,₹ 2.5 Cr,25000000,Cyber City, Gurgaon,Fully furnished office, 2500 sqft, near metro station.,https://www.magicbricks.com/propertyDetails/office-Gurgaon-104,https://images.unsplash.com/photo-1600585154340-be6161a56a0c,28.4943,77.0880
5,2 BHK Flat in Powai, Mumbai,₹ 1.05 Cr,10500000,Powai, Mumbai,Lake-view 2BHK apartment, 980 sqft, modern amenities.,https://www.magicbricks.com/propertyDetails/2bhk-Powai-105,https://images.unsplash.com/photo-1580587771525-78b9dba3b914,19.1177,72.9056
"""
        from io import StringIO
        df = pd.read_csv(StringIO(sample_data))
        df.to_csv(CSV_PATH, index=False)
        st.warning("⚠️ No properties.csv found — created sample data automatically.")

    return df


# ==========================================================
#  LOAD INITIAL DATA & SAVE FUNCTION
# ==========================================================
df = load_data()

def save_data(updated_df):
    """Save updated property data to CSV"""
    updated_df.to_csv(CSV_PATH, index=False)


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
    st.dataframe(df[["id", "title", "price_raw", "location", "price_inr"]], use_container_width=True)
    sel_id = st.number_input("🔍 View Property ID", min_value=0)
    if sel_id in df["id"].values:
        row = df[df["id"] == sel_id].iloc[0]
        st.markdown(f"### {row['title']}")
        st.write(f"💰 {row['price_raw']} — ₹{row['price_inr']:,}")
        st.write(f"📍 {row['location']}")
        st.write(f"📝 {row['details']}")
        if row["image_url"]:
            st.image(row["image_url"], caption=row["title"])

        if row["latitude"] and row["longitude"]:
            st.map(pd.DataFrame([[row["latitude"], row["longitude"]]], columns=["lat", "lon"]))

with right:
    # --- Property Gallery Section ---
    st.subheader("🏠 Property Gallery")

gallery = df.copy()

if not gallery.empty:
    cols = st.columns(3)
    for i, (_, g) in enumerate(gallery.head(9).iterrows()):
        with cols[i % 3]:
            img_url = g.get("image_url", "")
            title = g.get("title", "Property")
            location = g.get("location", "")
            price = g.get("price_raw", "")

            # ✅ Check if valid image URL or file
            if img_url and (img_url.startswith("http") or os.path.exists(img_url)):
                try:
                    st.image(img_url, caption=f"{title}\n{location}\n{price}")
                except Exception:
                    st.warning("⚠️ Unable to load image")
            else:
                st.warning("📷 Image not available")

            
else:
    st.info("No property images to show yet.")

