import streamlit as st
import pandas as pd
import pydeck as pdk
import os
from io import BytesIO
from datetime import datetime
from geopy.geocoders import Nominatim
import time

def show():
    DATA_PATH = "Data/Reports.csv"

    st.title("Harta Problemelor Urbane")

    if not os.path.exists(DATA_PATH):
        st.warning("Nu există rapoarte disponibile.")
        return

    df = pd.read_csv(DATA_PATH)
    # Ensure consistent column casing
    df.columns = [col.strip().capitalize() if col.lower() == "timestamp" else col for col in df.columns]


    def extract_lat_lon(location_str):
        try:
            parts = [p.strip() for p in str(location_str).split(",")]
            if len(parts) == 2:
                return float(parts[0]), float(parts[1])
            return None, None
        except:
            return None, None


    df["Status"] = df["Status"].astype(str).str.strip().str.lower()
    df[["Latitude", "Longitude"]] = df["Location"].apply(lambda loc: pd.Series(extract_lat_lon(loc)))
    df = df.dropna(subset=["Latitude", "Longitude", "Status"])

    #  Formatam Timestamp-ul
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df["Formatted Timestamp"] = df["Timestamp"].dt.strftime("%d %B %Y, %H:%M")

    #  Geocodare inversă pentru locație
    geolocator = Nominatim(user_agent="urban_issues_app")
    address_cache = {}

    def reverse_geocode(lat, lon):
        key = f"{lat},{lon}"
        if key in address_cache:
            return address_cache[key]
        try:
            location = geolocator.reverse((lat, lon), language="ro", timeout=10)
            address = location.address if location else "Locație necunoscută"
        except:
            address = "Locație necunoscută"
        address_cache[key] = address
        time.sleep(1)  # Respectăm limita API-ului Nominatim
        return address

    df["Formatted Location"] = df.apply(lambda row: reverse_geocode(row["Latitude"], row["Longitude"]), axis=1)

    # === Filtrare după statusuri ===
    status_colors = {
        "sesizat": [255, 0, 0],
        "în proces de rezolvare": [255, 255, 0],
        "rezolvat": [0, 255, 0],
    }

    with st.expander("Filtreaza problemele", expanded=False):
        st.markdown("### Alege statusurile pe care vrei să le vezi:")
        col1, col2, col3 = st.columns(3)
        selected_status = []

        with col1:
            if st.checkbox("🟥 Sesizat", value=True, key="sesizat"):
                selected_status.append("sesizat")
        with col2:
            if st.checkbox("🟨 În proces de rezolvare", value=True, key="in_proces"):
                selected_status.append("în proces de rezolvare")
        with col3:
            if st.checkbox("🟩 Rezolvat", value=True, key="rezolvat"):
                selected_status.append("rezolvat")

    filtered_df = df[df["Status"].isin(selected_status)]
    if filtered_df.empty:
        st.info("Nu există rapoarte pentru statusurile selectate.")
        return

    filtered_df["Color"] = filtered_df["Status"].apply(lambda status: status_colors.get(status, [200, 200, 200]))

    view_state = pdk.ViewState(
        latitude=filtered_df["Latitude"].mean(),
        longitude=filtered_df["Longitude"].mean(),
        zoom=12,
        pitch=0,
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position='[Longitude, Latitude]',
        get_radius=120,
        get_fill_color='Color',
        pickable=True,
    )

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v12',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={
            "text": "📍 {Formatted Location}\n🕒 {Formatted Timestamp}\n📝 {Description}\n🔧 {Status}"
        }
    ))
