import network
import urequests
import time
from machine import Pin, ADC, I2C
from dht import DHT11
from ssd1306 import SSD1306_I2C

# === Konfigurasi WiFi ===
SSID = "PEXIST106_9"  # Ganti dengan SSID WiFi Anda
PASSWORD = "imanilmuamal"  # Ganti dengan password WiFi Anda

# === Konfigurasi Ubidots ===
UBIDOTS_TOKEN = "BBUS-ZYMsrjRHYXbLRigG1JqWtRBmjhpLls"  # Ganti dengan Ubidots Token Anda
UBIDOTS_DEVICE_LABEL = "phaethon"
UBIDOTS_URL = "https://industrial.api.ubidots.com/api/v1.6/devices/"

# Variabel yang akan dikirim
UBIDOTS_VARIABLE_TEMP = "temperature"
UBIDOTS_VARIABLE_HUM = "humidity"
UBIDOTS_VARIABLE_SOUND = "noise_level"

# === Sensor dan OLED ===
dht_sensor = DHT11(Pin(15))  # Sensor DHT11 di Pin 15
sound_sensor = ADC(Pin(34))  # Sensor suara KY-038 di Pin 34
sound_sensor.atten(ADC.ATTN_11DB)  # Atur sensitivitas ADC
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  # I2C untuk OLED
oled = SSD1306_I2C(128, 64, i2c, addr=0x3C)  # OLED SSD1306 dengan alamat 0x3C

# === Fungsi untuk Menghubungkan ke WiFi ===
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print("Connecting to WiFi...")
    oled.fill(0)
    oled.text("Connecting to WiFi...", 0, 0)
    oled.show()
    
    while not wlan.isconnected():
        time.sleep(1)
        print(".")
    
    print("WiFi Connected!")
    oled.fill(0)
    oled.text("WiFi Connected!", 0, 0)
    oled.show()
    time.sleep(1)

# === Fungsi untuk Mengirim Data ke Ubidots ===
def send_to_ubidots(temperature, humidity, noise_level):
    url = f"{UBIDOTS_URL}{UBIDOTS_DEVICE_LABEL}/"
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": UBIDOTS_TOKEN
    }
    payload = {
        UBIDOTS_VARIABLE_TEMP: temperature,
        UBIDOTS_VARIABLE_HUM: humidity,
        UBIDOTS_VARIABLE_SOUND: noise_level
    }
    
    try:
        print("Sending data to Ubidots...")
        print(f"Payload: {payload}")
        response = urequests.post(url, json=payload, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Text: {response.text}")
        response.close()
    except Exception as e:
        print(f"Error sending data to Ubidots: {e}")

# === Proses Utama ===
connect_to_wifi()  # Hubungkan ke WiFi

while True:
    try:
        # Baca data dari sensor DHT11
        dht_sensor.measure()
        temperature = dht_sensor.temperature()
        humidity = dht_sensor.humidity()
        
        # Baca data dari sensor suara KY-038
        noise_level = sound_sensor.read()
        
        # Log nilai sensor ke Serial Monitor
        print(f"Temperature: {temperature}°C, Humidity: {humidity}%, Noise Level: {noise_level}")
        
        # Tampilkan data di OLED
        oled.fill(0)
        oled.text(f"Temp: {temperature} C", 0, 0)
        oled.text(f"Hum: {humidity} %", 0, 10)
        oled.text(f"Sound: {noise_level}", 0, 20)
        oled.show()
        
        # Kirim data ke Ubidots
        send_to_ubidots(temperature, humidity, noise_level)
        
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(5)  # Delay 5 detik sebelum membaca ulang data