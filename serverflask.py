from flask import Flask, request, jsonify

app = Flask(__name__)

# Menggunakan dictionary untuk menyimpan data sementara
sensor_data = []

@app.route('/', methods=['GET'])
def home():
    return "Server sudah berjalan"

@app.route('/save', methods=['POST'])
def save_data():
    try:
        # Mengambil data yang dikirimkan dalam format JSON
        data = request.get_json()
        print("Received data:", data)

        # Mendapatkan nilai suhu, kelembaban, dan jarak
        suhu = data.get("suhu")
        kelembaban = data.get("kelembaban")
        jarak = data.get("jarak")

        # Cek jika ada data yang tidak ada
        if suhu is None or kelembaban is None or jarak is None:
            return jsonify({"error": "suhu, kelembaban, dan jarak are required."}), 400

        # Membuat record data sensor
        record = {"suhu": suhu, "kelembaban": kelembaban, "jarak": jarak}
        
        # Menyimpan data ke dalam list sensor_data
        sensor_data.append(record)

        return jsonify({"message": "Data saved successfully."}), 201
    
    except Exception as error:
        print("Error:", error)
        return jsonify({"error": str(error)}), 500

@app.route('/data', methods=['GET'])
def get_data():
    """Endpoint untuk mendapatkan semua data sensor yang tersimpan"""
    return jsonify(sensor_data), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

