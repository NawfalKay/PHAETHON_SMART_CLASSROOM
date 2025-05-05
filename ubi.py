import requests
import time
import random

# ---------------- Konfigurasi Ubidots ----------------
UBIDOTS_TOKEN = 'BBUS-ZYMsrjRHYXbLRigG1JqWtRBmjhpLls'
DEVICE_LABEL = 'phaethon'
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}"
HEADERS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

# ---------------- Fungsi Kirim Data ----------------
def kirim_data(temp, hum, sound):
    data = {
        "temperature": temp,
        "humidity": hum,
        "sound": sound
    }
    try:
        response = requests.post(UBIDOTS_URL, headers=HEADERS, json=data)
        print(f"Kirim: {data} | Status: {response.status_code}")
        response.close()
    except Exception as e:
        print("Gagal mengirim:", e)

# ---------------- Kirim Data Setiap 2 Detik Tanpa Henti ----------------
while True:
    temperature = round(random.uniform(24.0, 32.0), 1)
    humidity = round(random.uniform(40.0, 80.0), 1)
    sound = random.randint(0, 100)

    kirim_data(temperature, humidity, sound)
    time.sleep(2)  # jeda 2 detik antar kiriman
