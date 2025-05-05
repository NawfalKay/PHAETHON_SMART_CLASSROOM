import streamlit as st
from PIL import Image
import os
import pandas as pd
import time
import datetime
import requests

# === KONFIGURASI UBIDOTS ===
TOKEN = "BBUS-ZYMsrjRHYXbLRigG1JqWtRBmjhpLls"
DEVICE_LABEL = "phaethon"
BASE_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/"

def get_latest_value(variable):
    url = f"{BASE_URL}{DEVICE_LABEL}/{variable}/lv"
    headers = {"X-Auth-Token": TOKEN}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return float(response.text)
        else:
            return None
    except:
        return None

# === KONFIGURASI APLIKASI ===
LOG_FILE = "absensi_log.txt"
PHOTO_DIR = "absensi_foto"

st.set_page_config(page_title="Rekap Absensi Wajah", layout="wide")
st.title("MONITORING KONDISI KELAS & SISTEM ABSENSI OTOMATIS")
st.markdown("---")

# === FUNGSI MEMBACA DATA SENSOR DARI UBIDOTS ===
def get_sensor_data():
    temperature = get_latest_value("temperature")
    humidity = get_latest_value("humidity")
    noise = get_latest_value("sound")
    if None in [temperature, humidity, noise]:
        st.error("Gagal mengambil data dari Ubidots.")
        return None
    return {
        "temperature": temperature,
        "humidity": humidity,
        "noise_level": noise
    }

# === FUNGSI KONDISI KELAS ===
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

# === MEMUAT DATA ABSENSI DARI FILE ===
def load_absensi_data():
    data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        timestamp, name = line.split(", ")
                        # Ubah format nama file sesuai dengan nama_tanggal_waktu
                        photo_filename = f"{name.replace(' ', '')}{timestamp.replace(' ', '_').replace(':', '-')}.jpg"
                        photo_path = os.path.join(PHOTO_DIR, photo_filename)
                        data.append({
                            "name": name,
                            "timestamp": timestamp,
                            "photo_path": photo_path if os.path.exists(photo_path) else None
                        })
                    except ValueError:
                        continue
    return data

# === FUNGSI RESET DATA ABSENSI DAN LOG ===
def reset_absensi():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    if os.path.exists(PHOTO_DIR):
        for filename in os.listdir(PHOTO_DIR):
            if filename.endswith(".jpg"):
                os.remove(os.path.join(PHOTO_DIR, filename))

# === HALAMAN NAVIGASI ===
page = st.sidebar.selectbox("Pilih Halaman", ["Dashboard Sensor", "Data Absensi", "Log Absensi"])

# === DASHBOARD SENSOR ===
if page == "Dashboard Sensor":
    sensor_data = get_sensor_data()

    if sensor_data:
        st.markdown("### Monitoring Sensor")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown('<h4 style="text-align: center; color: #1E90FF;">KELEMBAPAN</h4>', unsafe_allow_html=True)
        with col2:
            st.markdown('<h4 style="text-align: center; color: #FF6347;">SUHU</h4>', unsafe_allow_html=True)
        with col3:
            st.markdown('<h4 style="text-align: center; color: #32CD32;">KEBISINGAN</h4>', unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f'<h2 style="text-align: center; color: #1E90FF;">{sensor_data["humidity"]}%</h2>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<h2 style="text-align: center; color: #FF6347;">{sensor_data["temperature"]}°C</h2>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<h2 style="text-align: center; color: #32CD32;">{sensor_data["noise_level"]} dB</h2>', unsafe_allow_html=True)

        classroom_condition = get_classroom_condition(sensor_data['temperature'], sensor_data['humidity'], sensor_data['noise_level'])
        st.markdown(f'<h5 style="text-align: center; color: #444;">{classroom_condition}</h5>', unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Grafik Suhu, Kelembapan, dan Kebisingan")

        if "temperature_data" not in st.session_state:
            st.session_state.temperature_data = []
        if "humidity_data" not in st.session_state:
            st.session_state.humidity_data = []
        if "noise_data" not in st.session_state:
            st.session_state.noise_data = []

        # Simpan 10 data terakhir
        st.session_state.temperature_data.append(sensor_data['temperature'])
        st.session_state.humidity_data.append(sensor_data['humidity'])
        st.session_state.noise_data.append(sensor_data['noise_level'])

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

    time.sleep(2)
    st.rerun()

# === DATA ABSENSI ===
if page == "Data Absensi":
    st.markdown("### Data Absensi")
    
    # Tambahkan tombol untuk memulai atau menghentikan auto-refresh
    auto_refresh = st.checkbox("Aktifkan Auto-Refresh", value=True)

    absensi_data = load_absensi_data()

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔁 Reset Absensi"):
            reset_absensi()
            st.success("Data absensi dan foto berhasil direset.")
            time.sleep(2)
            st.rerun()

    if absensi_data:
        for entry in reversed(absensi_data):
            with st.container():
                cols = st.columns([1, 2])
                with cols[0]:
                    photo_path = entry["photo_path"]
                    if entry["photo_path"] and os.path.exists(photo_path):
                        img = Image.open(entry["photo_path"])
                        st.image(img, width=200)
                    else:
                        st.warning(f"📸 Foto tidak ditemukan di path: {photo_path}")
                with cols[1]:
                    st.markdown(f"### 👤 {entry['name']}")
                    st.markdown(f"🕒 {entry['timestamp']}")
                    st.markdown("---")
    else:
        st.info("Belum ada data absensi.")

    # Tambahkan fitur auto-refresh
    if auto_refresh:
        time.sleep(2)
        st.rerun()


# === LOG ABSENSI ===
if page == "Log Absensi":
    st.markdown("### Log Absensi")

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🧹 Reset Log"):
            reset_absensi()
            st.success("Log absensi berhasil dihapus.")
            time.sleep(2)
            st.rerun()

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = f.readlines()

        if logs:
            st.table([{"Waktu": log.split(", ")[0], "Nama": log.split(", ")[1].strip()} for log in logs])
        else:
            st.info("Belum ada log absensi.")
    else:
        st.error(f"File log absensi '{LOG_FILE}' tidak ditemukan.")