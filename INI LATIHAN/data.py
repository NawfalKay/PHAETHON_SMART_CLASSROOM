import time
import random
import requests

# Token dan label perangkat Ubidots Anda
TOKEN = "BBUS-ZYMsrjRHYXbLRigG1JqWtRBmjhpLls"
DEVICE_LABEL = "phaethon"
BASE_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/"

# Fungsi untuk mengirim data ke Ubidots
def send_data(temp, humidity, sound):
    url = f"{BASE_URL}{DEVICE_LABEL}"
    payload = {
        "temperature": temp,
        "humidity": humidity,
        "sound": sound
    }
    headers = {
        "X-Auth-Token": TOKEN,
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(f"Sent: {payload} | Status: {response.status_code}")

# Kirim data setiap 1 detik selama 2 detik
while True:
    temp = round(random.uniform(20.0, 35.0), 2)
    humidity = round(random.uniform(30.0, 80.0), 2)
    sound = round(random.uniform(40.0, 90.0), 2)
    send_data(temp, humidity, sound)
    time.sleep(1)  # Kirim setiap 1 detik
