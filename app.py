from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import tensorflow as tf
import numpy as np
from PIL import Image
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'eatsmart_secret_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eatsmart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ✅ User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    blood_glucose = db.Column(db.Float, default=0)
    cholesterol = db.Column(db.Float, default=0)

# ✅ Load Model
model = tf.keras.models.load_model("food_model_v3", compile=False)
infer = model.signatures["serving_default"]
print("✅ Model loaded!")

class_names = [
    "bhatura", "biryani", "butter_chicken", "chole_bhature",
    "dal_makhni", "gulab_jamun", "idli", "jalebi",
    "pav_bhaji", "poha", "samosa", "vada_pav"
]

calories_data = {
    "bhatura": 320,
    "biryani": 190,
    "butter_chicken": 165,
    "chole_bhature": 300,
    "dal_makhni": 135,
    "gulab_jamun": 385,
    "idli": 58,
    "jalebi": 360,
    "pav_bhaji": 180,
    "poha": 130,
    "samosa": 265,
    "vada_pav": 290
}

def get_suggestion(food, blood_glucose, cholesterol):
    high_sugar = ["gulab_jamun", "jalebi"]
    high_cholesterol = ["butter_chicken", "chole_bhature", "bhatura", "samosa", "vada_pav"]
    high_carb = ["bhatura", "chole_bhature", "pav_bhaji", "vada_pav", "jalebi", "gulab_jamun"]

    reasons = []
    suggestion = "✅ Safe to Consume"

    if blood_glucose > 140:
        if food in high_sugar:
            suggestion = "❌ Avoid"
            reasons.append("High sugar — not good for diabetes")
        elif food in high_carb:
            suggestion = "⚠️ Limited"
            reasons.append("High carbs — consume in small quantity")

    if cholesterol > 200:
        if food in high_cholesterol:
            if suggestion == "✅ Safe to Consume":
                suggestion = "⚠️ Limited"
            reasons.append("High fat — not good for cholesterol")
        if cholesterol > 240 and food in high_cholesterol:
            suggestion = "❌ Avoid"
            reasons.append("Very high cholesterol — strictly avoid")

    return suggestion, reasons

def preprocess_image(image):
    image = image.resize((224, 224))
    image = np.array(image, dtype=np.float32) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user and check_password_hash(user.password, data['password']):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid email or password'})
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        existing = User.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'success': False, 'message': 'Email already registered'})
        user = User(
            name=data['name'],
            email=data['email'],
            password=generate_password_hash(data['password'])
        )
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['user_name'] = user.name
        return jsonify({'success': True, 'redirect': '/health-profile'})
    return render_template('signup.html')

@app.route('/health-profile', methods=['GET', 'POST'])
def health_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        user = User.query.get(session['user_id'])
        user.blood_glucose = float(data['blood_glucose'])
        user.cholesterol = float(data['cholesterol'])
        db.session.commit()
        return jsonify({'success': True})
    return render_template('health_profile.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['user_name'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return jsonify({'error': 'Please login first'}), 401
    try:
        file = request.files['image']
        image = Image.open(file).convert('RGB')
        processed_image = preprocess_image(image)
        input_tensor = tf.constant(processed_image)
        result = infer(input_tensor)
        output_key = list(result.keys())[0]
        predictions = result[output_key].numpy()
        predicted_index = np.argmax(predictions[0])
        confidence = float(np.max(predictions[0])) * 100
        food = class_names[predicted_index]

        user = User.query.get(session['user_id'])
        suggestion, reasons = get_suggestion(food, user.blood_glucose, user.cholesterol)

        return jsonify({
            'prediction': food,
            'confidence': round(confidence, 2),
            'calories': calories_data[food],
            'suggestion': suggestion,
            'reasons': reasons
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)