import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st

def save_to_google_sheets(report):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1kf7im4WWNZJkPzR3p8NOatwTYBc5mSxuCCnEqISp-Tk").sheet1

    row = [
        report["timestamp"],
        report["cracks"], report["fallen_trees"], report["graffiti"],
        report["illegal_parking"], report["open_manhole"], report["overflowing_trashbin"],
        report["pothole"], report["stray"], report["trash"], report["roadkills"], report["flood"],
        report["broken_urban_furniture"], report["wild_animals"], report["dangerous_buildings"],
        report["location"], report["description"], report["status"]
    ]

    sheet.append_row(row)
