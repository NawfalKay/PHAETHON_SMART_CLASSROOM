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
                        continue  # Lewati baris error
    return data

# Ambil data sensor dari Flask API
def get_sensor_data():
    try:
        response = requests.get("http://192.168.0.103:5000/data")  # ganti sesuai URL Flask kamu
        if response.status_code == 200:
            return response.json()  # pastikan API Flask mengembalikan JSON {'temperature':..., 'humidity':..., 'noise_level':...}
        else:
            st.error("Gagal mengambil data sensor dari server.")
            return None
    except Exception as e:
        st.error(f"Terjadi kesalahan koneksi ke server Flask: {e}")
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
    # Menampilkan data sensor yang baru di-refresh
    sensor_data = get_sensor_data()  # Ini memastikan data sensor baru diperoleh setiap kali

    if sensor_data:
        st.markdown("### Monitoring Sensor")

        # Baris judul
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown('<h4 style="text-align: center; color: #1E90FF;">KELEMBAPAN</h4>', unsafe_allow_html=True)
        with col2:
            st.markdown('<h4 style="text-align: center; color: #FF6347;">SUHU</h4>', unsafe_allow_html=True)
        with col3:
            st.markdown('<h4 style="text-align: center; color: #32CD32;">KEBISINGAN</h4>', unsafe_allow_html=True)

        # Baris nilai
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f'<h2 style="text-align: center; color: #1E90FF;">{sensor_data["humidity"]}%</h2>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<h2 style="text-align: center; color: #FF6347;">{sensor_data["temperature"]}°C</h2>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<h2 style="text-align: center; color: #32CD32;">{sensor_data["noise_level"]} dB</h2>', unsafe_allow_html=True)

        # Kesimpulan kondisi kelas
        classroom_condition = get_classroom_condition(sensor_data['temperature'], sensor_data['humidity'], sensor_data['noise_level'])
        st.markdown(f'<h5 style="text-align: center; color: #444;">{classroom_condition}</h5>', unsafe_allow_html=True)

        # Garis pembatas & grafik
        st.markdown("---")
        st.subheader("Grafik Suhu dan Kelembapan")

        if "temperature_data" not in st.session_state:
            st.session_state.temperature_data = []
        if "humidity_data" not in st.session_state:
            st.session_state.humidity_data = []

        st.session_state.temperature_data.append(sensor_data['temperature'])
        st.session_state.humidity_data.append(sensor_data['humidity'])
        st.session_state.temperature_data = st.session_state.temperature_data[-100:]
        st.session_state.humidity_data = st.session_state.humidity_data[-100:]

        df = pd.DataFrame({
            "Suhu (°C)": st.session_state.temperature_data,
            "Kelembapan (%)": st.session_state.humidity_data
        })
        st.line_chart(df)

        st.markdown(""" 
        - **Suhu (°C)**: Mengukur suhu ruangan secara real-time.
        - **Kelembapan (%)**: Mengukur tingkat kelembapan udara di sekitar.
        """)

    # Melakukan rerun otomatis setiap 5 detik untuk memperbarui data sensor
    time.sleep(2)
    st.rerun()  # Re-render tampilan halaman Dashboard Sensor

# Halaman Absensi
if page == "Data Absensi":
    # Tombol reset data
    if st.button("🔴 Reset Data Absensi"):
        # Kosongkan file log
        if os.path.exists(LOG_FILE):
            open(LOG_FILE, "w").close()

        # Hapus semua foto absensi
        if os.path.exists(PHOTO_DIR):
            for file in os.listdir(PHOTO_DIR):
                file_path = os.path.join(PHOTO_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

        st.success("✅ Semua data absensi telah dihapus.")
        
        # Menunggu 3 detik sebelum rerun otomatis
        time.sleep(3)
        st.rerun()  # Re-render tampilan

    # Tampilkan daftar absensi dari file
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
