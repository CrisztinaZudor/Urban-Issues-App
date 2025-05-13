import streamlit as st
import requests
from PIL import Image
import numpy as np
import cv2
import os
import pandas as pd 
import datetime
from fpdf import FPDF
from streamlit_current_location import current_position
import admin_dashboard
import map_view
from geopy.geocoders import OpenCage
from reports_db import insert_report
import sqlite3
from reports_db import init_db
init_db()


# ----------------------------- Custom CSS -----------------------------
st.markdown("""
    <style>
        .block-container {
            padding: 2rem 3rem;
        }

        /* Menu + Contact buttons */
        .stButton>button,
        div[data-testid="stExpander"] > details {
            background-color: #2ecc71 !important;
            color: white !important;
            border: none !important;
            border-radius: 5px !important;
            padding: 0.5rem 1rem !important;
            text-align: center !important;
            transition: background-color 0.3s ease, color 0.3s ease;
            box-shadow: none !important;
        }

        /* Hover effect */
        .stButton>button:hover,
        div[data-testid="stExpander"] > details:hover {
            background-color: #239b56 !important;
            color: #d5f5e3 !important;
        }

        /* Remove arrow and space */
        div[data-testid="stExpander"] summary::marker,
        div[data-testid="stExpander"] summary::before {
            display: none !important;
        }

        div[data-testid="stExpander"] summary {
            list-style: none;
            display: flex;
            justify-content: center;
            align-items: left;
            font-weight: 500;
            font-size: 15px;
            color: white !important;
        }

        /* Hide internal background on open */
        div[data-testid="stExpander"] > details[open] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        /* Contact content spacing */
        div[data-testid="stExpander"] .stMarkdown {
            padding: 0.5rem 1rem;
        }

        /* File uploader button hover */
        button[kind="secondary"] {
            border: 1px solid #2ecc71 !important;
            color: #2ecc71 !important;
            background: transparent !important;
            transition: all 0.3s ease;
        }

        button[kind="secondary"]:hover {
            background-color: #2ecc71 !important;
            color: white !important;
        }

        .stTextInput>div>input, .stTextArea>div>textarea {
            border-radius: 6px;
        }

        .report-card {
            background-color: #2a2a2a;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------- Configs -----------------------------
MAX_WIDTH, MAX_HEIGHT = 800, 800
TEMP_IMAGE_PATH = "temp_image.jpg"
API_KEY = "FaFuJj3V3gw6uexPjbaW"
PDF_DIR = "generated_pdfs"
ADMIN_PASSWORD = "admin123"
CONFIDENCE_THRESHOLD = 0.5
DB_PATH = "Data/reports.db"
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs("Data", exist_ok=True)

# ----------------------------- DB Setup -----------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            cracks INTEGER,
            fallen_trees INTEGER,
            graffiti INTEGER,
            illegal_parking INTEGER,
            open_manhole INTEGER,
            overflowing_trashbin INTEGER,
            pothole INTEGER,
            stray INTEGER,
            trash INTEGER,
            roadkills INTEGER,
            flood INTEGER,
            broken_urban_furniture INTEGER,
            wild_animals INTEGER,
            dangerous_buildings INTEGER,
            location TEXT,
            description TEXT,
            status TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()

# ----------------------------- Custom CSS -----------------------------
st.markdown("""<style> ... </style>""", unsafe_allow_html=True)  # CSS păstrat neschimbat pentru claritate

# ----------------------------- Sidebar -----------------------------
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("urban_holmes_logo.png", width=160)

    st.markdown("---")
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Sesizeaza o problema"

    for label in ["Sesizeaza o problema", "Harta Problemelor", "Administratie"]:
        if st.button(label, use_container_width=True):
            st.session_state["current_page"] = label

    st.markdown("---")
    with st.expander("Contact"):
        st.markdown("Email: [urban@email.com](mailto:urban@email.com)")

# ----------------------------- Page Routing -----------------------------
if st.session_state["current_page"] == "Sesizeaza o problema":
    st.markdown("<h2 style='margin-top: 0;'>Probleme Urbane</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='font-size:16px; line-height:1.6; margin-bottom:2rem;'>
        Aici poți sesiza rapid problemele din orașul tău! De la coșuri de gunoi pline, până la mașini parcate ilegal.<br><br>
        Faci o poză, sistemul nostru cu inteligență artificială detectează automat problema, iar sesizarea ta ajunge direct la autoritățile locale.<br><br>
        <b>Tu vezi ce alții trec cu vederea!</b>
    </div>
    """, unsafe_allow_html=True)

    location_data = current_position()

    manual_location = st.text_input(
        "Introdu locația manual (opțional):",
        placeholder="Ex: 46.770439, 23.591423 sau Str. Memorandumului, Cluj-Napoca"
    )


    location_str = ""
    geolocator = OpenCage(api_key="79333a6e62e94f6582766d6c508daf8b")

    if manual_location.strip():
        try:
            import unicodedata
            def normalize_text(text):
                return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

            clean_address = normalize_text(manual_location.strip())
            location = geolocator.geocode(clean_address)

            if location:
                location_str = f"{location.latitude}, {location.longitude}"
                st.success(f"Locație geocodificată: {manual_location.strip()} → {location_str}")
            else:
                st.warning("Adresa introdusă nu a putut fi localizată.")
        except Exception as e:
            st.warning(f"Eroare la geocodificare: {str(e)}")

    elif location_data:
        lat = location_data.get("latitude")
        lon = location_data.get("longitude")
        location_str = f"{lat}, {lon}"
        st.success(f"Locație detectată automat: {location_str}")

    else:
        st.warning("Locația nu a putut fi detectată. Te rugăm să introduci una manual.")

    st.markdown("### Încarcă imaginea cu problema identificată")
    uploaded_file = st.file_uploader("Selectează o imagine", type=["jpg", "png", "jpeg", "jfif"])

    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        img.thumbnail((MAX_WIDTH, MAX_HEIGHT))
        img_np = np.array(img)
        img.save(TEMP_IMAGE_PATH)

        st.image(img, caption="Imagine încărcată", use_container_width=True)

        if st.button("Detectează Probleme"):
            with st.spinner("Analizăm imaginea..."):
                def run_model(image_path, model_url):
                    with open(image_path, "rb") as image_file:
                        response = requests.post(f"{model_url}?api_key={API_KEY}",
                                                 files={"file": image_file}, timeout=10)
                        response.raise_for_status()
                        return response.json()

                def draw_predictions(image_np, predictions, color, label_prefix="", conf_thresh=CONFIDENCE_THRESHOLD):
                    count = 0
                    for pred in predictions.get("predictions", []):
                        confidence = pred.get("confidence", 0)
                        if confidence >= conf_thresh:
                            x, y, w, h = int(pred["x"]), int(pred["y"]), int(pred["width"]), int(pred["height"])
                            left, top = x - w // 2, y - h // 2
                            right, bottom = x + w // 2, y + h // 2
                            cv2.rectangle(image_np, (left, top), (right, bottom), color, 2)
                            label = f"{label_prefix}{confidence:.2f}"
                            cv2.putText(image_np, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                            count += 1
                    return image_np, count

                def blur_faces(image_np, predictions):
                    for pred in predictions.get("predictions", []):
                        confidence = pred.get("confidence", 0)
                        if confidence >= CONFIDENCE_THRESHOLD:
                            x, y, w, h = int(pred["x"]), int(pred["y"]), int(pred["width"]), int(pred["height"])
                            shrink_ratio = 0.85
                            new_w, new_h = int(w * shrink_ratio), int(h * shrink_ratio)
                            center_x, center_y = x, y
                            left = max(center_x - new_w // 2, 0)
                            top = max(center_y - new_h // 2, 0)
                            right = min(center_x + new_w // 2, image_np.shape[1])
                            bottom = min(center_y + new_h // 2, image_np.shape[0])
                            face_roi = image_np[top:bottom, left:right]
                            if face_roi.size > 0:
                                blurred = cv2.GaussianBlur(face_roi, (45, 45), 30)
                                image_np[top:bottom, left:right] = blurred
                    return image_np

                MODEL_URL = "https://detect.roboflow.com/urban-issues-detector-yb3km/3"

                predictions = run_model(TEMP_IMAGE_PATH, MODEL_URL)
                result_img = blur_faces(img_np.copy(), predictions)

                CLASS_NAMES = [
                    "cracks", "fallen_trees", "graffiti", "illegal_parking", "open_manhole",
                    "overflowing_trashbin", "pothole", "stray", "trash", "roadkills",
                    "flood", "broken_urban_furniture", "wild_animals", "dangerous_buildings"
                ]


                detected_counts = {}
                result_img = img_np.copy()

                for class_name in CLASS_NAMES:
                    class_preds = {
                        "predictions": [p for p in predictions.get("predictions", []) if p["class"] == class_name]
                    }
                    result_img, count = draw_predictions(result_img, class_preds, (0, 255, 0), f"{class_name.replace('_', ' ').title()}: ")
                    if count > 0:
                        detected_counts[class_name] = count


                st.session_state.update({
                    "detection_done": True,
                    "result_img": result_img,
                    "detected_counts": detected_counts
                })


    if st.session_state.get("detection_done", False):
        PROBLEM_LABELS = {
            "cracks": "Crăpături în asfalt",
            "fallen_trees": "Copaci căzuți",
            "graffiti": "Graffiti",
            "illegal_parking": "Parcare ilegală",
            "open_manhole": "Capace de canal lipsă",
            "overflowing_trashbin": "Coșuri de gunoi pline",
            "pothole": "Gropi în asfalt",
            "stray": "Animale fără stăpân",
            "trash": "Gunoi aruncat",
            "roadkills": "Animale moarte",
            "flood": "Inundații",
            "broken_urban_furniture": "Mobilier urban stricat",
            "wild_animals": "Animale sălbatice",
            "dangerous_buildings": "Clădiri periculoase"
        }

        lines = [f"- {PROBLEM_LABELS.get(cls, cls)}: {cnt}" for cls, cnt in st.session_state["detected_counts"].items()]
        st.image(st.session_state["result_img"], caption="\n".join(lines), use_container_width=True)


        description = st.text_area("Detalii suplimentare", placeholder="Ex: 3 mașini parcate ilegal în fața blocului.")
        if st.button("Trimite Raport"):
            CLASS_NAMES = [
                "cracks", "fallen_trees", "graffiti", "illegal_parking", "open_manhole",
                "overflowing_trashbin", "pothole", "stray", "trash", "roadkills",
                "flood", "broken_urban_furniture", "wild_animals", "dangerous_buildings"
            ]

            timestamp = datetime.datetime.now().isoformat()
            report = {
                "Timestamp": timestamp,
                "Location": location_str,
                "Description": description,
                "Status": "sesizat"
            }

            # Add detected counts to the report
            for cls in CLASS_NAMES:
                report[cls] = st.session_state["detected_counts"].get(cls, 0)

            save_report(report)  # ✅ store in SQLite
            st.success("Raport trimis cu succes!")


            def generate_pdf_report(image_np, report_data):
                from fpdf import FPDF
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                image_path = f"{PDF_DIR}/image_{timestamp}.jpg"
                pdf_output_path = f"{PDF_DIR}/Report_{timestamp}.pdf"
                Image.fromarray(image_np).save(image_path)

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
                    "open_manhole": "Capace de canal lipsă",
                    "overflowing_trashbin": "Coșuri de gunoi pline",
                    "pothole": "Gropi în asfalt",
                    "stray": "Animale fără stăpân",
                    "trash": "Gunoi aruncat",
                    "roadkills": "Animale moarte pe șosea",
                    "flood": "Inundații",
                    "broken_urban_furniture": "Mobilier urban stricat",
                    "wild_animals": "Animale sălbatice",
                    "dangerous_buildings": "Clădiri periculoase"
                }
                

                pdf = FPDF()
                pdf.add_page()
                pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
                pdf.set_font("DejaVu", size=12)


                # Title
                pdf.set_font("DejaVu", size=16)

                pdf.cell(200, 10, txt="Raport - Probleme Urbane", ln=True, align="C")
                pdf.ln(10)

                # General Info
                pdf.set_font("DejaVu", size=12)
                pdf.cell(200, 10, txt=f"Data și ora: {report_data['Timestamp']}", ln=True)
                pdf.cell(200, 10, txt=f"Locație: {report_data['Location']}", ln=True)
                pdf.cell(200, 10, txt=f"Status: {report_data['Status']}", ln=True)
                pdf.ln(5)

                # Description
                pdf.multi_cell(0, 10, txt=f"Descriere: {report_data['Description'] or '—'}")
                pdf.ln(5)

                # Detected Problems
                pdf.set_font("DejaVu", size=14)
                pdf.cell(200, 10, txt="Probleme detectate:", ln=True)
                pdf.set_font("DejaVu", size=12)

                has_detections = False
                for cls in CLASS_NAMES:
                    count = report_data.get(cls, 0)
                    if count and int(count) > 0:
                        label = PROBLEM_LABELS.get(cls, cls.replace("_", " ").title())
                        pdf.cell(200, 10, txt=f"- {label}: {count}", ln=True)
                        has_detections = True

                if not has_detections:
                    pdf.cell(200, 10, txt="Nicio problemă detectată.", ln=True)

                # Image
                pdf.ln(5)
                pdf.image(image_path, x=10, y=None, w=180)

                pdf.output(pdf_output_path)
                return pdf_output_path


            pdf_path = generate_pdf_report(st.session_state["result_img"], report)
            st.success(f"PDF generat: {pdf_path}")

            with open(pdf_path, "rb") as f:
                st.download_button("Descarcă PDF", f, file_name=os.path.basename(pdf_path))

            st.session_state["detection_done"] = False
            if os.path.exists(TEMP_IMAGE_PATH):
                os.remove(TEMP_IMAGE_PATH)

elif st.session_state["current_page"] == "Harta Problemelor":
    map_view.show()

elif st.session_state["current_page"] == "Administratie":
        admin_dashboard.show()
