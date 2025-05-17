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

from datetime import datetime

def format_coords(coord_str):
    try:
        lat, lon = map(float, coord_str.split(","))
        return f"{round(lat, 5)},{round(lon, 5)}"
    except:
        return None

def update_status_in_google_sheets(timestamp, location, new_status):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1kf7im4WWNZJkPzR3p8NOatwTYBc5mSxuCCnEqISp-Tk").sheet1

    records = sheet.get_all_records()

    # Convert timestamp to string format used in Sheets
    if isinstance(timestamp, datetime):
        ts_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    else:
        try:
            ts_obj = datetime.fromisoformat(str(timestamp))
            ts_str = ts_obj.strftime("%Y-%m-%d %H:%M:%S")
        except:
            ts_str = str(timestamp).split(".")[0].replace("T", " ")


    formatted_loc = format_coords(location)

    for i, row in enumerate(records):
        row_ts = str(row.get("timestamp", "")).strip()
        row_loc = format_coords(str(row.get("location", "")).strip())

        if row_ts == ts_str and row_loc == formatted_loc:
            cell_row = i + 2  # header is skipped in get_all_records
            col_names = list(records[0].keys())
            status_col = col_names.index("status") + 1
            sheet.update_cell(cell_row, status_col, new_status)
            return True

    return False
