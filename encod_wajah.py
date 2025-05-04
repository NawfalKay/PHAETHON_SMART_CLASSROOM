import face_recognition
import pickle
import os

# Path ke file encodings yang ada
ENCODINGS_FILE = "encodings.pkl"

# Load encoding yang sudah ada
def load_known_faces():
    """Memuat encoding wajah yang sudah ada dari file pickle."""
    try:
        with open(ENCODINGS_FILE, "rb") as f:
            data = pickle.load(f)
            return data["encodings"], data["names"]
    except FileNotFoundError:
        print(f"❌ File encoding '{ENCODINGS_FILE}' tidak ditemukan. File baru akan dibuat.")
        return [], []
    except Exception as e:
        print(f"❌ Gagal memuat encoding wajah: {e}")
        exit()

# Menyimpan encoding wajah yang sudah diperbarui
def save_known_faces(encodings, names):
    """Menyimpan encoding wajah yang sudah diperbarui ke file pickle."""
    data = {"encodings": encodings, "names": names}
    with open(ENCODINGS_FILE, "wb") as f:
        pickle.dump(data, f)
    print("✅ File encoding berhasil disimpan.")

# Fungsi untuk menambahkan wajah baru
def add_new_face(image_path, name):
    """Menambahkan wajah baru ke dalam encoding dan menyimpannya."""
    # Load gambar
    image = face_recognition.load_image_file(image_path)
    
    # Dapatkan encoding wajah dari gambar
    encodings = face_recognition.face_encodings(image)
    
    if len(encodings) > 0:
        new_encoding = encodings[0]
        # Memuat encoding yang sudah ada
        known_face_encodings, known_face_names = load_known_faces()

        # Tampilkan jumlah wajah sebelum penambahan
        print(f"Jumlah wajah sebelum penambahan: {len(known_face_encodings)}")

        # Tambahkan encoding baru ke dalam list yang ada
        known_face_encodings.append(new_encoding)
        known_face_names.append(name)

        # Simpan kembali ke file pickle
        save_known_faces(known_face_encodings, known_face_names)

        # Tampilkan jumlah wajah setelah penambahan
        print(f"Jumlah wajah setelah penambahan: {len(known_face_encodings)}")
    else:
        print("❌ Tidak ada wajah yang terdeteksi dalam gambar.")

# Fungsi untuk menampilkan jumlah wajah dan nama yang ada
def show_existing_faces():
    """Menampilkan jumlah dan nama wajah yang ada dalam encoding."""
    known_face_encodings, known_face_names = load_known_faces()

    if len(known_face_encodings) == 0:
        print("❌ Tidak ada data wajah yang tersimpan.")
    else:
        print(f"Jumlah wajah yang tersimpan: {len(known_face_encodings)}")
        print("Nama-nama wajah yang tersimpan:")
        for name in known_face_names:
            print(f"- {name}")

# Fungsi utama untuk menjalankan program
def main():
    # Menambahkan wajah baru (bisa di-comment jika tidak menambah wajah baru)
    image_path = ""  # Ganti dengan path gambar wajah
    name = ""  # Ganti dengan nama yang sesuai
    add_new_face(image_path, name)

    # Menampilkan jumlah dan nama-nama wajah yang ada
    show_existing_faces()

# Menjalankan fungsi utama
if __name__ == "__main__":
    main()
