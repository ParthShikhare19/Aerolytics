# 🌍 Aerolytics

**Real-time Air Quality Monitoring & Prediction System**

Monitor air quality with IoT sensors and predict AQI using machine learning. Combines Arduino hardware, real-time dashboards, and ML-powered predictions.

---

## 🚀 What's Inside

### **IoT System** 
Real-time air quality monitoring with Arduino sensors → FastAPI backend → React dashboard

### **ML System**
Linear Regression model to predict AQI from environmental parameters

---

## 📦 Quick Start

### **IoT Setup**

**Hardware Needed:**
- Arduino Uno + BME680 (temp/humidity/gas) + PMS5003 (PM sensor)

**Steps:**
```bash
# 1. Upload Arduino code
# Upload IoT/Arduino Code/sketch_feb7a/sketch_feb7a.ino to Arduino

# 2. Start Backend (requires PostgreSQL)
cd IoT/backend
pip install fastapi uvicorn psycopg2-binary python-dotenv
uvicorn main:app --reload

# 3. Start Serial Bridge
python serial_to_api.py

# 4. Start Frontend
cd IoT/frontend
npm install
npm run dev
```

**Access:** `http://localhost:5173`

---

### **ML Setup**

**Train Model:**
```bash
cd ML
pip install pandas scikit-learn flask
python train_model.py  # Creates model.pkl
```

**Run Prediction App:**
```bash
python app.py  # Runs on http://localhost:5000
```

Input: PM1.0, PM2.5, PM10, Temperature, Humidity, Gas Resistance  
Output: Predicted AQI

---

## 📊 How It Works

**IoT Flow:**  
Arduino Sensors → Serial Port → Python Bridge → FastAPI → PostgreSQL → React Dashboard

**ML Flow:**  
Historical Data → Data Cleaning → Linear Regression → Model Prediction

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **IoT Hardware** | Arduino Uno, BME680, PMS5003 |
| **IoT Backend** | FastAPI, PostgreSQL, Python |
| **IoT Frontend** | React, Vite |
| **ML Training** | Scikit-learn, Pandas |
| **ML Serving** | Flask |

---

## 📁 Project Structure

```
Aerolytics/
├── IoT/
│   ├── Arduino Code/     # Sensor sketches (BME680 + PMS5003)
│   ├── backend/          # FastAPI server + serial bridge
│   └── frontend/         # React dashboard
└── ML/
    ├── data/             # Air quality dataset
    ├── train_model.py    # Model training
    ├── data_clean.py     # Data preprocessing
    ├── Accuracy.py       # Model evaluation
    └── app.py            # Flask prediction API
```

---

## ⚙️ Configuration

**IoT Backend `.env`:**
```bash
DATABASE_URL=postgresql://user:pass@localhost/aerolytics
```

**Serial Port (serial_to_api.py):**
```python
SERIAL_PORT = "COM5"  # Change to your Arduino port
```

**Database Setup:**
```sql
CREATE TABLE air_quality_readings (
    id SERIAL PRIMARY KEY,
    pm1 FLOAT, pm25 FLOAT, pm10 FLOAT,
    aqi INT, aqi_category VARCHAR(50),
    temperature FLOAT, humidity FLOAT,
    gas_resistance FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 Features

**IoT:**
- Live sensor readings every 5 seconds
- Color-coded AQI dashboard (Good → Hazardous)
- Historical data storage

**ML:**
- Linear regression model for AQI prediction
- 80%+ accuracy on test data
- Web interface for predictions

---

## 🔍 Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| Arduino not detected | Check COM port in Device Manager |
| Sensors not found | Verify wiring (BME680: I2C, PMS5003: Serial) |
| DB connection error | Ensure PostgreSQL running & check `.env` |
| Frontend blank | Backend must run on port 8000 |

---

**Made for cleaner air monitoring 🌱**
