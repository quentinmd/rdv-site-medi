from flask import Flask, render_template, request, jsonify
import sqlite3
import qrcode
import random
import string
from datetime import datetime
from pyzbar.pyzbar import decode
import cv2

app = Flask(__name__)

# Fonction pour établir une connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Fonction pour lire le QR code à partir d'une image
def read_qr_code(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        return data
    return None

# Fonction pour vérifier la plage horaire du rendez-vous
def check_appointment_time(access_code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT appointment_time FROM appointments WHERE access_code = ?", (access_code,))
    appointment_time_str = cursor.fetchone()[0]
    appointment_time = datetime.strptime(appointment_time_str, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    conn.close()
    return current_time < appointment_time

# Fonction pour ouvrir la barrière
def open_barrier():
    # Intégrer le code pour ouvrir la barrière ici
    print("La barrière est ouverte.")

# Endpoint pour afficher la page de création de rendez-vous
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint pour créer un rendez-vous
@app.route('/create_appointment', methods=['POST'])
def create_appointment():
    patient_name = request.form['patient_name']
    appointment_time = request.form['appointment_time']
    
    # Générer un code d'accès aléatoire
    access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    # Insertion du rendez-vous dans la base de données
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO appointments (patient_name, appointment_time, access_code) VALUES (?, ?, ?)",
                   (patient_name, appointment_time, access_code))
    conn.commit()
    conn.close()

    # Générer le QR code
    generate_qr_code(access_code)

    return jsonify({'message': 'Appointment created successfully', 'access_code': access_code})

# Générer un QR code pour un code d'accès donné
def generate_qr_code(access_code):
    img = qrcode.make(access_code)
    img.save('static/access_code_qr.png')

# Endpoint pour lire le QR code et ouvrir la barrière
@app.route('/read_qr_code', methods=['POST'])
def read_qr_code_endpoint():
    qr_code_image_path = 'path/to/qr_code_image.png'  # Chemin vers l'image contenant le QR code
    access_code = read_qr_code(qr_code_image_path)
    if access_code:
        if check_appointment_time(access_code):
            open_barrier()
            return jsonify({'message': 'Barrier opened successfully'})
        else:
            return jsonify({'error': 'Invalid appointment time'})
    else:
        return jsonify({'error': 'No QR code detected'})

if __name__ == '__main__':
    app.run(debug=True)