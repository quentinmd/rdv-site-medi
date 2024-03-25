from flask import Flask, render_template, request, jsonify
import sqlite3
import qrcode
import random
import string
from datetime import datetime

app = Flask(__name__)

# Fonction pour établir une connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

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

if __name__ == '__main__':
    app.run(debug=True)
