import os
import pickle
import time
import random
import cv2
import face_recognition
import pygame
import numpy as np
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# File untuk menyimpan kredensial
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pkl'

# ID folder di Google Drive tempat foto akan disimpan
DRIVE_FOLDER_ID = 'your-folder-id'

# Inisialisasi pygame
pygame.init()
window_size = (640, 480)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Face Recognition Absensi")

# Direktori untuk menyimpan foto absensi
ATTENDANCE_DIR = "absensi_foto"
if not os.path.exists(ATTENDANCE_DIR):
    os.makedirs(ATTENDANCE_DIR)

# Fungsi untuk autentikasi dan mendapatkan layanan Google Drive
def authenticate_google_drive():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/drive.file'])
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('drive', 'v3', credentials=creds)
    return service

# Fungsi untuk meng-upload foto ke Google Drive
def upload_to_drive(file_path):
    service = authenticate_google_drive()
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype='image/jpeg')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File uploaded: {file.get('id')}")
    return file.get('id')

# Fungsi untuk log absensi
def log_attendance(name, file_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp}, {name}, {file_path}\n"
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
        print(f"📝 Log absensi tercatat: {log_entry.strip()}")
    except Exception as e:
        print(f"❌ Gagal mencatat log absensi: {e}")

# Inisialisasi ESP32-CAM dan Face Recognition
ESP32_CAM_URL = 0
cap = cv2.VideoCapture(ESP32_CAM_URL)

if not cap.isOpened():
    print("❌ Gagal mengakses stream ESP32-CAM.")
    exit()

# Daftar wajah yang dikenal dan file pickle untuk encoding wajah
ENCODINGS_FILE = "encodings.pkl"
known_face_encodings = []
known_face_names = []

# Muat encoding wajah dari file pickle
def load_known_faces():
    global known_face_encodings, known_face_names
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
            known_face_encodings = data["encodings"]
            known_face_names = data["names"]
            print(f"✅ Encoding wajah berhasil dimuat dari '{ENCODINGS_FILE}'")
    except FileNotFoundError:
        print(f"❌ File encoding '{ENCODINGS_FILE}' tidak ditemukan. Pastikan file ini ada.")
        exit()
    except Exception as e:
        print(f"❌ Gagal memuat encoding wajah: {e}")
        exit()

# Memuat wajah yang dikenal
load_known_faces()

running = True
clock = pygame.time.Clock()

while running:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame untuk performa
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Deteksi wajah dan encoding
    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        name = "Unknown"

        if face_distances[best_match_index] < 0.4:  # Toleransi lebih ketat
            name = known_face_names[best_match_index]

            # Jika belum diabsen, tambahkan ke log dan simpan foto
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            photo_filename = f"{ATTENDANCE_DIR}/{name}_{timestamp}.jpg"
            cv2.imwrite(photo_filename, frame)

            # Upload foto ke Google Drive dan log absensi
            file_id = upload_to_drive(photo_filename)
            log_attendance(name, file_id)

    # Convert frame ke format pygame (RGB → Surface)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = np.fliplr(frame_rgb)  # Mirror frame
    frame_rgb = np.rot90(frame_rgb)   # Rotate 90 derajat
    frame_surface = pygame.surfarray.make_surface(frame_rgb)
    screen.blit(frame_surface, (0, 0))
    pygame.display.update()

    # Cek event quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    clock.tick(30)  # Batasi ke 30 FPS

cap.release()
pygame.quit()
