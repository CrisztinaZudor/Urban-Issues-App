from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import io

def upload_pdf_to_drive(file_path, filename):
    scope = ['https://www.googleapis.com/auth/drive.file']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)

    drive_service = build('drive', 'v3', credentials=creds)

    with open(file_path, 'rb') as f:
        file_metadata = {'name': filename, 'mimeType': 'application/pdf'}
        media = MediaIoBaseUpload(f, mimetype='application/pdf')
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return file.get('id')  # returnează ID-ul fișierului
