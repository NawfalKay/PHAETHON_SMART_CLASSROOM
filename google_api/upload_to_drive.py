import cv2
import face_recognition
import pygame
import numpy as np
import pickle
import os
from datetime import datetime
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# URL streaming ESP32-CAM
ESP32_CAM_URL = 0  # Ganti dengan IP ESP32-CAM Anda

# Inisialisasi pygame
pygame.init()
window_size = (640, 480)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Face Recognition Absensi")

# Daftar wajah yang dikenal
known_face_encodings = []
known_face_names = []

# File pickle untuk menyimpan encoding wajah
ENCODINGS_FILE = "encodings.pkl"

# Direktori untuk menyimpan foto absensi
ATTENDANCE_DIR = "absensi_foto"

# File untuk menyimpan log absensi
LOG_FILE = "absensi_log.txt"

# Folder ID Google Drive
FOLDER_ID = '1YZHW5hY0o_DpLKR1FyUSVImwnDzlcUsj'  # Ganti dengan ID folder Anda

if not os.path.exists(ATTENDANCE_DIR):
    os.makedirs(ATTENDANCE_DIR)

# Menyimpan status absensi sementara
attendance_log = {}

def load_known_faces():
    """Memuat encoding wajah yang dikenal dari file pickle."""
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

def log_attendance(name):
    """Mencatat absensi ke file log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp}, {name}\n"
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
        print(f"📝 Log absensi tercatat: {log_entry.strip()}")
    except Exception as e:
        print(f"❌ Gagal mencatat log absensi: {e}")

def upload_to_drive(frame, name):
    """Upload foto ke Google Drive."""
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # hanya pertama kali untuk login ke Google

    drive = GoogleDrive(gauth)

    # Membuat nama file foto berdasarkan nama dan timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{name}_{timestamp}.jpg"
    
    # Simpan frame sebagai gambar sementara di disk
    temp_file_path = f"temp_{file_name}"
    cv2.imwrite(temp_file_path, frame)

    # Membuat file Google Drive dan mengupload foto
    file_drive = drive.CreateFile({
        'title': file_name,
        'parents': [{'id': FOLDER_ID}]  # Menentukan folder tujuan di Google Drive
    })

    # Mengupload file gambar ke Google Drive
    file_drive.SetContentFile(temp_file_path)
    file_drive.Upload()
    print(f"✅ Foto berhasil di-upload ke Google Drive: {file_drive['title']}")

    # Pastikan file sudah tidak digunakan lagi sebelum dihapus
    try:
        os.remove(temp_file_path)
        print(f"✅ File sementara '{temp_file_path}' berhasil dihapus.")
    except Exception as e:
        print(f"❌ Gagal menghapus file sementara: {e}")

# Muat encoding wajah dari file pickle
load_known_faces()

# Mengakses stream dari ESP32-CAM
cap = cv2.VideoCapture(ESP32_CAM_URL)

if not cap.isOpened():
    print("❌ Gagal mengakses stream ESP32-CAM.")
    exit()

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
            if name not in attendance_log:
                attendance_log[name] = True
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                photo_filename = f"{ATTENDANCE_DIR}/{name}_{timestamp}.jpg"
                cv2.imwrite(photo_filename, frame)
                log_attendance(name)

                # Upload foto ke Google Drive
                upload_to_drive(frame, name)

        # Skala balik koordinat (karena frame dikecilkan)
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Gambar persegi panjang di sekitar wajah
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, f"{name} ({face_distances[best_match_index]:.2f})", (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

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
