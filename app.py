import streamlit as st
from PIL import Image
import os
import pandas as pd
import random
import time
import datetime
import requests

# Lokasi file log dan folder foto
LOG_FILE = "absensi_log.txt"
PHOTO_DIR = "absensi_foto"

st.set_page_config(page_title="Rekap Absensi Wajah", layout="wide")
st.title("MONITORING KONDISI KELAS & SISTEM ABSENSI OTOMATIS")
st.markdown("---")

# Fungsi untuk baca log absensi
def load_absensi_data():
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        timestamp, name = line.split(", ")
                        photo_filename = f"{name}_{timestamp.replace(':', '-').replace(' ', '_')}.jpg"
                        photo_path = os.path.join(PHOTO_DIR, photo_filename)
                        data.append({
                            "name": name,
                            "timestamp": timestamp,
                            "photo_path": photo_path if os.path.exists(photo_path) else None
                        })
                    except ValueError:
                        continue
    return data

# Ambil data sensor dari Ubidots
def get_sensor_data_from_ubidots():
    API_KEY = 'BBUS-e5b989efecad340dceef0c67ab5ecc52d04'  # Ganti dengan API Key Ubidots kamu
    DEVICE_ID = 'phaethon'  # Ganti dengan Device ID Ubidots kamu

    # Endpoint untuk mengambil data dari Ubidots
    UBIDOTS_URL = f'https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_ID}/data/'

    headers = {
        'X-Auth-Token': API_KEY
    }

    try:
        response = requests.get(UBIDOTS_URL, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Ambil data sensor dari hasil response
            return data['results']
        else:
            st.error("Gagal mengambil data dari Ubidots.")
            return None
    except Exception as e:
        st.error(f"Terjadi kesalahan koneksi ke Ubidots: {e}")
        return None

def get_classroom_condition(temperature, humidity, noise):
    if temperature < 20:
        temp = "Dingin"
    elif 20 <= temperature < 25:
        temp = "Nyaman"
    elif 25 <= temperature < 30:
        temp = "Hangat"
    else:
        temp = "Panas"

    if humidity < 40:
        hum = "Kering"
    elif 40 <= humidity <= 60:
        hum = "Normal"
    else:
        hum = "Lembap"

    if noise > 60:
        sound = "Bising"
    elif 40 <= noise <= 60:
        sound = "Tidak Berisik"
    else:
        sound = "Tenang"

    return f"Kelas {temp}, {hum}, {sound}"

# Data Absensi
attendance_data = []

def log_attendance(name, status):
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attendance_data.append({"Nama": name, "Tanggal": current_date, "Absen": status})

# Pilih Halaman
page = st.sidebar.selectbox("Pilih Halaman", ["Dashboard Sensor", "Data Absensi"])

# Halaman Sensor
if page == "Dashboard Sensor":
    sensor_data = get_sensor_data_from_ubidots()

    if sensor_data:
        st.markdown("### Monitoring Sensor")

        # Ambil data suhu, kelembapan, dan kebisingan dari Ubidots
        humidity = sensor_data[0].get('value', 0)  # Anggap data kelembapan ada di index 0
        temperature = sensor_data[1].get('value', 0)  # Anggap data suhu ada di index 1
        noise_level = sensor_data[2].get('value', 0)  # Anggap data kebisingan ada di index 2

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown('<h4 style="text-align: center; color: #1E90FF;">KELEMBAPAN</h4>', unsafe_allow_html=True)
        with col2:
            st.markdown('<h4 style="text-align: center; color: #FF6347;">SUHU</h4>', unsafe_allow_html=True)
        with col3:
            st.markdown('<h4 style="text-align: center; color: #32CD32;">KEBISINGAN</h4>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f'<h2 style="text-align: center; color: #1E90FF;">{humidity}%</h2>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<h2 style="text-align: center; color: #FF6347;">{temperature}°C</h2>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<h2 style="text-align: center; color: #32CD32;">{noise_level} dB</h2>', unsafe_allow_html=True)

        classroom_condition = get_classroom_condition(temperature, humidity, noise_level)
        st.markdown(f'<h5 style="text-align: center; color: #444;">{classroom_condition}</h5>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Grafik Suhu, Kelembapan, dan Kebisingan")

        if "temperature_data" not in st.session_state:
            st.session_state.temperature_data = []
        if "humidity_data" not in st.session_state:
            st.session_state.humidity_data = []
        if "noise_data" not in st.session_state:
            st.session_state.noise_data = []

        # Tambahkan data terbaru
        st.session_state.temperature_data.append(temperature)
        st.session_state.humidity_data.append(humidity)
        st.session_state.noise_data.append(noise_level)

        # Hanya simpan 10 data terakhir
        max_data = 10
        st.session_state.temperature_data = st.session_state.temperature_data[-max_data:]
        st.session_state.humidity_data = st.session_state.humidity_data[-max_data:]
        st.session_state.noise_data = st.session_state.noise_data[-max_data:]

        df = pd.DataFrame({
            "Suhu (°C)": st.session_state.temperature_data,
            "Kelembapan (%)": st.session_state.humidity_data,
            "Kebisingan (dB)": st.session_state.noise_data
        })

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.subheader("Grafik Kelembapan")
            st.line_chart(df["Kelembapan (%)"])
        with col2:
            st.subheader("Grafik Suhu")
            st.line_chart(df["Suhu (°C)"])
        with col3:
            st.subheader("Grafik Kebisingan")
            st.line_chart(df["Kebisingan (dB)"])

        st.markdown(""" 
        - **Suhu (°C)**: Mengukur suhu ruangan secara real-time.
        - **Kelembapan (%)**: Mengukur tingkat kelembapan udara di sekitar.
        - **Kebisingan (dB)**: Mengukur tingkat kebisingan di dalam kelas.
        """)

    time.sleep(2)
    st.rerun()

# Halaman Absensi
if page == "Data Absensi":
    if st.button("🔴 Reset Data Absensi"):
        if os.path.exists(LOG_FILE):
            open(LOG_FILE, "w").close()
        if os.path.exists(PHOTO_DIR):
            for file in os.listdir(PHOTO_DIR):
                file_path = os.path.join(PHOTO_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        st.success("✅ Semua data absensi telah dihapus.")
        time.sleep(3)
        st.rerun()

    st.markdown("DATA ABSENSI")
    absensi_data = load_absensi_data()

    if absensi_data:
        for entry in reversed(absensi_data):
            with st.container():
                cols = st.columns([1, 2])
                with cols[0]:
                    if entry["photo_path"]:
                        img = Image.open(entry["photo_path"])
                        st.image(img, width=200)
                    else:
                        st.warning("📸 Foto tidak ditemukan.")
                with cols[1]:
                    st.markdown(f"### 👤 {entry['name']}")
                    st.markdown(f"🕒 {entry['timestamp']}")
                    st.markdown("---")
    else:
        st.info("Belum ada data absensi.")
