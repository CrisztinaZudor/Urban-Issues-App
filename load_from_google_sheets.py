import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd

def load_reports_from_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key("1kf7im4WWNZJkPzR3p8NOatwTYBc5mSxuCCnEqISp-Tk").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)
