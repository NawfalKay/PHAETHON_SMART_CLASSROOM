import streamlit as st
import requests

# Token dan label perangkat Ubidots Anda
TOKEN = "BBUS-ZYMsrjRHYXbLRigG1JqWtRBmjhpLls"
DEVICE_LABEL = "phaethon"
BASE_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/"

# Fungsi untuk mengambil 1 data terbaru dari variabel tertentu
def get_latest_value(variable):
    url = f"{BASE_URL}{DEVICE_LABEL}/{variable}/lv"
    headers = {
        "X-Auth-Token": TOKEN
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return float(response.text)
        else:
            return None
    except:
        return None

# Judul Aplikasi
st.title("Live Sensor Monitor dari Ubidots")

# Ambil dan tampilkan data terbaru
temperature = get_latest_value("temperature")
humidity = get_latest_value("humidity")
sound = get_latest_value("sound")

st.subheader("Data Terbaru dari Ubidots")

col1, col2, col3 = st.columns(3)

with col1:
    if temperature is not None:
        st.metric("Temperature (°C)", f"{temperature:.2f}")
    else:
        st.error("Gagal ambil temperature")

with col2:
    if humidity is not None:
        st.metric("Humidity (%)", f"{humidity:.2f}")
    else:
        st.error("Gagal ambil humidity")

with col3:
    if sound is not None:
        st.metric("Sound (dB)", f"{sound:.2f}")
    else:
        st.error("Gagal ambil sound")
