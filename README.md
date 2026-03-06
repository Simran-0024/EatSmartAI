# EatSmart AI 

An AI-based Indian Food Classification and Health Monitoring System.

## Features
- Food image classification using MobileNetV2 (Transfer Learning)
- 12 Indian food categories recognized
- User authentication (Login/Signup)
- Health profile management (Blood Glucose & Cholesterol)
- Calorie estimation per dish
- Personalized dietary recommendations (Safe/Limited/Avoid)

## Tech Stack
- **Backend:** Flask (Python)
- **ML Model:** TensorFlow, Keras, MobileNetV2
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript

## Food Classes
Bhatura, Biryani, Butter Chicken, Chole Bhature, Dal Makhni, Gulab Jamun, Idli, Jalebi, Pav Bhaji, Poha, Samosa, Vada Pav

## Setup
```bash
pip install -r requirements.txt
python app.py
```

## Usage
1. Signup and enter health details
2. Upload food image
3. Get dish prediction with calories and health suggestion

## Model Download
Download the trained model from Google Drive and place it in the project folder:
[Download food_model_v3]https://drive.google.com/drive/folders/1Vt2Jf1KLZrizqdYdI0dN9UiYGuUYj1DI?usp=sharing