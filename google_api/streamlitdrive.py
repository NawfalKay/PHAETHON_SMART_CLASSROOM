import streamlit as st
from PIL import Image
import pandas as pd
import requests
import os
import io
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# === KONFIGURASI ===
LOG_FILE = "absensi_log.txt"
FOLDER_ID = "1YZHW5hY0o_DpLKR1FyUSVImwnDzlcUsj"
PHOTO_DIR = "absensi_gdrive"

# === AUTENTIKASI GOOGLE DRIVE ===
def authenticate_google_drive():
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Wajib: file client_secrets.json harus ada
    return GoogleDrive(gauth)

# === AMBIL DATA DARI GOOGLE DRIVE ===
def fetch_drive_photos(drive):
    if not os.path.exists(PHOTO_DIR):
        os.makedirs(PHOTO_DIR)

    file_list = drive.ListFile({
        'q': f"'{FOLDER_ID}' in parents and trashed=false"
    }).GetList()

    photos = []
    for file in file_list:
        if file['mimeType'].startswith('image/'):
            file_id = file['id']
            file_title = file['title']
            download_url = f"https://drive.google.com/uc?id={file_id}"
            photo_path = os.path.join(PHOTO_DIR, file_title)

            if not os.path.exists(photo_path):
                response = requests.get(download_url)
                if response.status_code == 200:
                    with open(photo_path, 'wb') as f:
                        f.write(response.content)
            photos.append((file_title, photo_path))
    return photos

# === BACA LOG ABSENSI ===
def load_absensi_data():
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        timestamp, name = line.split(", ")
                        prefix = f"{name}_{timestamp.replace(':', '-').replace(' ', '_')}"
                        data.append({"name": name, "timestamp": timestamp, "photo_prefix": prefix})
                    except ValueError:
                        continue
    return data

# === TAMPILKAN FOTO DARI GDRIVE ===
def get_photo_path_for_entry(entry, photo_files):
    for filename, path in photo_files:
        if filename.startswith(entry['photo_prefix']):
            return path
    return None

# === STREAMLIT APP ===
st.set_page_config(page_title="Absensi Otomatis GDrive", layout="wide")
st.title("📷 Rekap Absensi dari Google Drive")
st.markdown("---")

col1, col2 = st.columns([1,1])
with col1:
    reset = st.button("🔴 Reset Data Absensi")
with col2:
    refresh = st.button("🔁 Refresh Foto GDrive")

# Reset data lokal (log dan folder foto)
if reset:
    if os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()
    if os.path.exists(PHOTO_DIR):
        for file in os.listdir(PHOTO_DIR):
            os.remove(os.path.join(PHOTO_DIR, file))
    st.success("✅ Data absensi berhasil direset.")
    st.rerun()

# Autentikasi & ambil foto dari Google Drive
if 'photos' not in st.session_state or refresh:
    try:
        st.info("🔐 Autentikasi ke Google Drive dan mengambil gambar...")
        drive = authenticate_google_drive()
        st.session_state.photos = fetch_drive_photos(drive)
        st.success("✅ Foto berhasil diambil dari Google Drive.")
    except Exception as e:
        st.error(f"❌ Gagal autentikasi/ambil foto: {e}")
        st.stop()

# Tampilkan data absensi
absensi_data = load_absensi_data()
if absensi_data:
    for entry in reversed(absensi_data):
        with st.container():
            cols = st.columns([1, 2])
            with cols[0]:
                photo_path = get_photo_path_for_entry(entry, st.session_state.photos)
                if photo_path and os.path.exists(photo_path):
                    st.image(photo_path, width=200)
                else:
                    st.warning("📸 Foto tidak ditemukan.")
            with cols[1]:
                st.markdown(f"### 👤 {entry['name']}")
                st.markdown(f"🕒 {entry['timestamp']}")
                st.markdown("---")
else:
    st.info("Belum ada data absensi.")
