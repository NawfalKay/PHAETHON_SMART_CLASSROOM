import requests
import json

# Konfigurasi Ubidots STEM
TOKEN = "BBUS-ZYMsrjRHYXbLRigG1JqWtRBmjhpLls"  # Token Ubidots STEM Anda
DEVICE_LABEL = "phaethon"  # Label perangkat Ubidots Anda
BASE_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/"

# Dummy data absensi
attendance_data = {
    "name": "John Doe",
    "photo_filename": "john_doe_2025-05-04_10-30-00.jpg",
    "timestamp": "2025-05-04 10:30:00"
}

# Endpoint untuk mengirim data ke Ubidots
url = f"{BASE_URL}{DEVICE_LABEL}/values/"

# Header untuk autentikasi
headers = {
    "Content-Type": "application/json",
    "X-Auth-Token": TOKEN
}

# Data yang akan dikirim ke Ubidots
data = {
    "variable1": {
        "value": attendance_data["name"]
    },
    "variable2": {
        "value": attendance_data["photo_filename"]
    },
    "variable3": {
        "value": attendance_data["timestamp"]
    }
}

# Mengirim data ke Ubidots
response = requests.post(url, headers=headers, data=json.dumps(data))

# Memeriksa respons
if response.status_code == 201:
    print("✅ Data berhasil dikirim ke Ubidots!")
else:
    print(f"❌ Gagal mengirim data ke Ubidots: {response.text}")
