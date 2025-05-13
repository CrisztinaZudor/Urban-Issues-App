import streamlit as st
import pandas as pd
import os
import pydeck as pdk
import datetime
from db_utils import verify_admin, log_action
from io import BytesIO

def show():
    DATA_PATH = "Data/Reports.csv"
    PDF_DIR = "generated_pdfs"

    # --- Autentificare Admin ---
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("Autentificare Administrator")
        username = st.text_input("Utilizator")
        password = st.text_input("Parolă", type="password")
        if st.button("Autentifică-te"):
            if verify_admin(username, password):
                st.session_state["authenticated"] = True
                st.session_state["admin_user"] = username
                log_action(username, "Autentificare reușită")
                st.success("Autentificare reușită.")
                st.rerun()
            else:
                log_action(username, "Autentificare eșuată")
                st.error("Utilizator sau parolă incorecte.")
        return  # oprește afișarea restului până la autentificare

    st.title("Harta Problemelor Urbane")

    if not os.path.exists(DATA_PATH):
        st.warning("Nu există rapoarte salvate încă.")
        return

    df = pd.read_csv(DATA_PATH)
    df.columns = df.columns.str.strip()

    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
        invalid_ts_count = df["Timestamp"].isna().sum()
        if invalid_ts_count > 0:
            st.warning(f"{invalid_ts_count} timestamp(uri) nu au fost parsate corect și vor apărea ca 'Data invalidă'")
        df = df.sort_values("Timestamp", ascending=False)
    else:
        st.warning("Coloana 'Timestamp' nu există în fișier.")


    def extract_lat_lon(location_str):
        try:
            lat_str, lon_str = location_str.split(",")
            return float(lat_str.strip()), float(lon_str.strip())
        except:
            return None, None

    df["Status"] = df["Status"].fillna("sesizat").astype(str).str.strip().str.lower()
    df[["Latitude", "Longitude"]] = df["Location"].apply(lambda loc: pd.Series(extract_lat_lon(loc)))

    search_term = st.text_input("Căutare în locație sau descriere")

    # Filters
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


    # Apply Status Filter
    if selected_status:
        df = df[df["Status"].isin(selected_status)]

    # Apply Text Search
    if search_term:
        df = df[
            df["Location"].str.contains(search_term, case=False, na=False) |
            df["Description"].str.contains(search_term, case=False, na=False)
        ]

    df = df.reset_index(drop=True)

    valid_coords_df = df.dropna(subset=["Latitude", "Longitude"])
    status_colors = {
        "sesizat": [255, 0, 0],
        "în proces de rezolvare": [255, 200, 0],
        "rezolvat": [0, 200, 0],
    }
    valid_coords_df["Color"] = valid_coords_df["Status"].apply(lambda s: status_colors.get(s, [200, 0, 200]))

    if not valid_coords_df.empty:
        st.subheader("Localizare pe hartă")

        view_state = pdk.ViewState(
            latitude=valid_coords_df["Latitude"].mean(),
            longitude=valid_coords_df["Longitude"].mean(),
            zoom=12,
            pitch=0,
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=valid_coords_df,
            get_position='[Longitude, Latitude]',
            get_radius=60,
            get_fill_color='Color',
            pickable=True,
        )

        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v12',
            initial_view_state=view_state,
            layers=[layer],
            tooltip={
                "text": "Locație: {Location}\nDescriere: {Description}\nStatus: {Status}"
            }
        ))
    else:
        st.info("Nu există locații valide pentru afișare.")

    st.subheader(f"Rapoarte găsite: {len(df)}")

    status_options = ["sesizat", "în proces de rezolvare", "rezolvat"]
    bg_colors = {
        "sesizat": "#f8d7da",
        "în proces de rezolvare": "#fff3cd",
        "rezolvat": "#d4edda",
    }
    icon_colors = {
        "sesizat": "#dc3545",
        "în proces de rezolvare": "#ffc107",
        "rezolvat": "#28a745",
    }

    for i, row in df.iterrows():
        status = row["Status"]
        bg_color = bg_colors.get(status, "#e2e3e5")
        icon_color = icon_colors.get(status, "#6c757d")
        
        # Verificăm dacă timestamp-ul este valid
        ts = row.get("Timestamp")
        if isinstance(ts, pd.Timestamp) and not pd.isna(ts):
            timestamp_str = ts.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp_str = "Data invalidă"

        
        latitude = row.get("Latitude")
        longitude = row.get("Longitude")

        google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}" if pd.notna(latitude) and pd.notna(longitude) else None

        with st.container():
            st.markdown(f"""
                <div style='background-color:{bg_color}; padding:15px; border-radius:10px; margin-bottom:10px'>
                    <span style='color:{icon_color}; font-size:20px'>⬤</span>
                    <strong> Raport din {timestamp_str}</strong>
                </div>
            """, unsafe_allow_html=True)

            CLASS_NAMES = [
                "cracks", "fallen_trees", "graffiti", "illegal_parking", "open_manhole",
                "overflowing_trashbin", "pothole", "stray", "trash", "roadkills",
                "flood", "broken_urban_furniture", "wild_animals", "dangerous_buildings"
            ]

            PROBLEM_LABELS = {
                "cracks": "Crăpături în asfalt",
                "fallen_trees": "Copaci căzuți",
                "graffiti": "Graffiti",
                "illegal_parking": "Parcare ilegală",
                "open_manhole": "Capace lipsă",
                "overflowing_trashbin": "Coșuri de gunoi pline",
                "pothole": "Gropi",
                "stray": "Animale fără stăpân",
                "trash": "Gunoi aruncat",
                "roadkills": "Animale moarte pe șosea",
                "flood": "Inundații",
                "broken_urban_furniture": "Mobilier urban stricat",
                "wild_animals": "Animale sălbatice",
                "dangerous_buildings": "Clădiri periculoase"
            }

            show_details = st.toggle("Afișează detalii", key=f"toggle_{i}")


            if show_details:
                details = "<ul>"
                for cls in CLASS_NAMES:
                    count = row.get(cls, 0)
                    if count and int(count) > 0:
                        details += f"<li><strong>{PROBLEM_LABELS[cls]}:</strong> {count}</li>"
                details += f"<li><strong>Descriere:</strong> {row['Description'] or '—'}</li>"
                details += f"<li><strong>Status curent:</strong> {row['Status']}</li>"

                if google_maps_link:
                    details += f"<li><strong>Locație:</strong> <a href='{google_maps_link}' target='_blank'>Vezi pe Google Maps</a></li>"
                else:
                    details += "<li><strong>Locație:</strong> N/A</li>"

                details += "</ul>"
                st.markdown(details, unsafe_allow_html=True)


            current_status = row["Status"] if row["Status"] in status_options else "sesizat"
            new_status = st.selectbox("Actualizează status:", status_options,
                                      index=status_options.index(current_status),
                                          key=f"status_{i}")
            if st.button("Salvează modificarea", key=f"save_{i}") and new_status != row["Status"]:
                df.at[i, "Status"] = new_status
                df.to_csv(DATA_PATH, index=False)
                log_action(st.session_state["admin_user"], f"Actualizat status raport la {new_status} - {row['Timestamp']} - {row['Location']}")
                st.success("Status actualizat.")
                st.rerun()

                # Verificăm dacă timestamp-ul este valid pentru a crea numele fișierului PDF
                pdf_filename = pd.to_datetime(row["Timestamp"]).strftime("%Y-%m-%d_%H-%M-%S") if pd.notna(row["Timestamp"]) else "invalid_date"
                invalid_ts_count = df["Timestamp"].isna().sum()
                if invalid_ts_count > 0:
                    st.warning(f"{invalid_ts_count} timestamp(uri) nu au fost parsate corect și vor apărea ca 'Data invalidă'")

                pdf_path = os.path.join(PDF_DIR, f"Report_{pdf_filename}.pdf")
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button("Descarcă PDF", f, file_name=os.path.basename(pdf_path))
                else:
                    st.info("PDF-ul pentru acest raport nu a fost găsit.")
