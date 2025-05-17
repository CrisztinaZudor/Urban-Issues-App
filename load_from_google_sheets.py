import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from datetime import datetime

def load_reports_from_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key("1kf7im4WWNZJkPzR3p8NOatwTYBc5mSxuCCnEqISp-Tk").sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def update_status_in_google_sheets(timestamp, location, new_status):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1kf7im4WWNZJkPzR3p8NOatwTYBc5mSxuCCnEqISp-Tk").sheet1

    records = sheet.get_all_records()

    for i, row in enumerate(records):
        row_timestamp = row.get("timestamp", "")
        row_location = row.get("location", "")
        
        # Match by both timestamp and location
        if str(row_timestamp).strip() == str(timestamp).strip() and str(row_location).strip() == str(location).strip():
            cell_row = i + 2  # +2 because get_all_records skips the header row
            status_col_index = list(records[0].keys()).index("status") + 1
            sheet.update_cell(cell_row, status_col_index, new_status)
            return True

    return False
