import streamlit as st
import pandas as pd
import pydeck as pdk
import os
from io import BytesIO
from datetime import datetime
from geopy.geocoders import Nominatim
import time
from reports_db import load_reports


def show():
    st.title("Harta Problemelor Urbane")

    df = load_reports()

    if df.empty:
        st.warning("Nu există rapoarte disponibile.")
        return


    def extract_lat_lon(location_str):
        try:
            parts = [p.strip() for p in str(location_str).split(",")]
            if len(parts) == 2:
                return float(parts[0]), float(parts[1])
            return None, None
        except:
            return None, None


    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df[["Latitude", "Longitude"]] = df["location"].apply(lambda loc: pd.Series(extract_lat_lon(loc)))
    df = df.dropna(subset=["Latitude", "Longitude", "status"])

    #  Formatam Timestamp-ul
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["Formatted timestamp"] = df["timestamp"].dt.strftime("%d %B %Y, %H:%M")

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

    df["Formatted location"] = df.apply(lambda row: reverse_geocode(row["Latitude"], row["Longitude"]), axis=1)

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
            if st.checkbox("🔴 Sesizat", value=True, key="sesizat"):
                selected_status.append("sesizat")
        with col2:
            if st.checkbox("🟡 În proces de rezolvare", value=True, key="in_proces"):
                selected_status.append("în proces de rezolvare")
        with col3:
            if st.checkbox("🟢 Rezolvat", value=True, key="rezolvat"):
                selected_status.append("rezolvat")

    filtered_df = df[df["status"].isin(selected_status)]
    if filtered_df.empty:
        st.info("Nu există rapoarte pentru statusurile selectate.")
        return

    filtered_df["Color"] = filtered_df["status"].apply(lambda status: status_colors.get(status, [200, 200, 200]))

    view_state = pdk.ViewState(
        latitude=46.77199106484599,   # Cluj-Napoca
        longitude=23.618117574725613,
        zoom=10.5,
        pitch=0,
    )

    # Rename BEFORE defining layer
    filtered_df = filtered_df.rename(columns={
        "Formatted timestamp": "formatted_timestamp",
        "Formatted location": "formatted_location"
    })

    # Create layer AFTER renaming
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
        "html": "<b>📍 {formatted_location}</b><br>🕒 {formatted_timestamp}<br>📝 {description}<br>🔧 {status}",
        "style": {
            "backgroundColor": "rgba(30,30,30,0.9)",
            "color": "white",
            "fontSize": "12px",
            "padding": "10px"
        }
    }

    ))
