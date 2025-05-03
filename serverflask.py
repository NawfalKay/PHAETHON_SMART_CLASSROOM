from flask import Flask, jsonify
import random
import time

app = Flask(__name__)

@app.route('/data')
def get_sensor_data():
    # Data dummy acak
    temperature = round(random.uniform(20.0, 30.0), 2)  # Suhu dalam °C antara 20 dan 30
    humidity = round(random.uniform(40.0, 60.0), 2)     # Kelembapan dalam % antara 40 dan 60
    noise_level = random.randint(30, 80)  # Kebisingan dalam dB antara 30 dan 80

    return jsonify({
        'temperature': temperature,
        'humidity': humidity,
        'noise_level': noise_level
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
