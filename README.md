# 🌍 Aerolytics

> Real-time Air Quality Index (AQI) and Environmental Monitoring System

Aerolytics is a comprehensive IoT solution for monitoring air quality and environmental conditions. It combines Arduino-based sensors with a modern web interface to provide real-time insights into particulate matter (PM), temperature, humidity, and air quality index calculations.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-19.2.0-61dafb.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688.svg)

---

## 📋 Table of Contents

- [Features](#-features)
- [System Architecture](#-system-architecture)
- [Hardware Requirements](#-hardware-requirements)
- [Software Stack](#-software-stack)
- [Installation](#-installation)
  - [1. Database Setup](#1-database-setup)
  - [2. Arduino Setup](#2-arduino-setup)
  - [3. Backend Setup](#3-backend-setup)
  - [4. Frontend Setup](#4-frontend-setup)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [AQI Calculation](#-aqi-calculation)
- [Future Enhancements](#-future-enhancements)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

- **Real-time Monitoring**: Live tracking of air quality metrics with 5-second refresh intervals
- **Multi-Sensor Integration**: Combines BME680 (temperature, humidity, gas) and PMS5003 (particulate matter) sensors
- **AQI Calculation**: EPA-standard Air Quality Index calculation for PM2.5 and PM10
- **Color-Coded Interface**: Intuitive visual representation of air quality levels
- **Historical Data Storage**: PostgreSQL database for long-term data analysis
- **RESTful API**: FastAPI backend for efficient data handling
- **Responsive Dashboard**: Modern React-based web interface
- **Serial Communication**: Automatic data transmission from Arduino to API

---

## 🏗️ System Architecture

```
┌─────────────────┐
│  Arduino Uno    │
│  + BME680       │  Serial    ┌──────────────────┐
│  + PMS5003      │ ────────> │ serial_to_api.py │
└─────────────────┘   (USB)    └──────────────────┘
                                         │ HTTP POST
                                         ▼
                               ┌──────────────────┐
                               │   FastAPI        │
                               │   Backend        │
                               │   (Port 8000)    │
                               └──────────────────┘
                                         │
                                         ▼
                               ┌──────────────────┐
                               │   PostgreSQL     │
                               │   Database       │
                               └──────────────────┘
                                         │ HTTP GET
                                         ▼
                               ┌──────────────────┐
                               │   React          │
                               │   Frontend       │
                               │   (Port 5173)    │
                               └──────────────────┘
```

---

## 🔧 Hardware Requirements

| Component | Model | Purpose |
|-----------|-------|---------|
| **Microcontroller** | Arduino Uno | Main controller |
| **Environmental Sensor** | BME680 | Temperature, humidity, pressure, gas resistance |
| **Particulate Sensor** | PMS5003 | PM1.0, PM2.5, PM10 measurements |
| **Connection** | USB Cable | Serial communication |
| **Optional** | Breadboard & Jumper Wires | Prototyping |

### Wiring Diagram

**BME680 (I2C):**
- VCC → 3.3V
- GND → GND
- SDA → A4
- SCL → A5

**PMS5003 (Serial):**
- VCC → 5V
- GND → GND
- TX → Pin 10 (Arduino RX)
- RX → Pin 11 (Arduino TX)

---

## 💻 Software Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Modern, fast web framework
- **psycopg2** - PostgreSQL adapter
- **python-dotenv** - Environment variable management
- **pyserial** - Serial communication
- **requests** - HTTP client library

### Frontend
- **React 19.2.0** - UI framework
- **Vite** - Build tool and dev server
- **Axios** - HTTP client (via api.js)

### Database
- **PostgreSQL** - Relational database

### Hardware
- **Arduino IDE** - For uploading sketches
- **Adafruit BME680 Library**
- **PMS Library** - For PMS5003 sensor

---

## 🚀 Installation

### Prerequisites
- Arduino IDE installed
- Python 3.8+ installed
- Node.js and npm installed
- PostgreSQL installed and running

### 1. Database Setup

Create a PostgreSQL database and table:

```sql
CREATE DATABASE aerolytics;

\c aerolytics

CREATE TABLE air_quality_readings (
    id SERIAL PRIMARY KEY,
    pm1 FLOAT NOT NULL,
    pm25 FLOAT NOT NULL,
    pm10 FLOAT NOT NULL,
    aqi INT NOT NULL,
    aqi_category VARCHAR(50) NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    gas_resistance FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 2. Arduino Setup

1. Open Arduino IDE
2. Install required libraries:
   - **Adafruit BME680** (via Library Manager)
   - **PMS Library** by Mariusz Kacki (via Library Manager)
   - **Adafruit Unified Sensor** (dependency)

3. Open `IoT/Arduino Code/sketch_feb7c/sketch_feb7c.ino`
4. Connect your Arduino Uno via USB
5. Select the correct board and port:
   - Tools → Board → Arduino Uno
   - Tools → Port → (Select your COM port)
6. Upload the sketch

### 3. Backend Setup

```bash
# Navigate to backend directory
cd IoT/backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn psycopg2-binary python-dotenv pyserial requests

# Create .env file
echo DATABASE_URL=postgresql://username:password@localhost/aerolytics > .env

# Start the FastAPI server
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd IoT/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The dashboard will be available at `http://localhost:5173`

---

## 🎯 Usage

### Starting the System

1. **Start PostgreSQL** (if not running)
   ```bash
   # Windows
   pg_ctl start
   # Or use pgAdmin
   ```

2. **Start Backend API**
   ```bash
   cd IoT/backend
   uvicorn main:app --reload
   ```

3. **Start Serial Bridge**
   ```bash
   cd IoT/backend
   python serial_to_api.py
   ```
   > **Note**: Update `SERIAL_PORT` in `serial_to_api.py` to match your Arduino's COM port

4. **Start Frontend**
   ```bash
   cd IoT/frontend
   npm run dev
   ```

5. **Access Dashboard**
   - Open browser to `http://localhost:5173`
   - Data will auto-refresh every 5 seconds

### Monitoring Data

The dashboard displays:
- **AQI Banner**: Current air quality index with color-coded status
- **PM Metrics**: PM1.0, PM2.5, PM10 particulate matter levels
- **Environmental Metrics**: Temperature, humidity, gas resistance
- **Reference Guide**: EPA AQI standards and health implications
- **Last Updated**: Timestamp of latest reading

---

## 📁 Project Structure

```
Aerolytics/
│
├── README.md
│
└── IoT/
    ├── Arduino Code/
    │   ├── sketch_feb7a/          # BME680 basic test
    │   │   └── sketch_feb7a.ino
    │   ├── sketch_feb7b/          # BME680 + PMS5003 basic
    │   │   └── sketch_feb7b.ino
    │   └── sketch_feb7c/          # Full AQI implementation ⭐
    │       └── sketch_feb7c.ino
    │
    ├── backend/
    │   ├── main.py                # FastAPI server
    │   ├── serial_to_api.py       # Serial-to-API bridge
    │   └── .env                   # Database credentials (create this)
    │
    └── frontend/
        ├── package.json
        ├── vite.config.js
        ├── index.html
        │
        └── src/
            ├── App.jsx            # Main app component
            ├── main.jsx           # Entry point
            │
            ├── components/
            │   └── Dashboard.jsx  # Main dashboard component
            │
            ├── services/
            │   └── api.js         # API service
            │
            └── styles/
                └── Dashboard.css  # Dashboard styling
```

---

## 🔌 API Endpoints

### `POST /insert`

Insert new sensor reading into database.

**Request Body:**
```json
{
  "pm1": 15.2,
  "pm25": 23.5,
  "pm10": 35.8,
  "aqi": 78,
  "aqi_category": "Moderate",
  "temperature": 24.5,
  "humidity": 55.3,
  "gas": 125.7
}
```

**Response:**
```json
{
  "status": "success"
}
```

### `GET /latest`

Retrieve the most recent sensor reading.

**Response:**
```json
{
  "pm1": 15.2,
  "pm25": 23.5,
  "pm10": 35.8,
  "aqi": 78,
  "aqi_category": "Moderate",
  "temperature": 24.5,
  "humidity": 55.3,
  "gas": 125.7,
  "created_at": "2026-02-07T12:34:56.789Z"
}
```

---

## 📊 AQI Calculation

The system uses EPA's Air Quality Index formula:

### PM2.5 Breakpoints
| PM2.5 (µg/m³) | AQI Range | Category |
|---------------|-----------|----------|
| 0.0 - 12.0 | 0-50 | Good |
| 12.1 - 35.4 | 51-100 | Moderate |
| 35.5 - 55.4 | 101-150 | Unhealthy for Sensitive Groups |
| 55.5 - 150.4 | 151-200 | Unhealthy |
| 150.5 - 250.4 | 201-300 | Very Unhealthy |
| 250.5 - 500.0 | 301-500 | Hazardous |

### PM10 Breakpoints
| PM10 (µg/m³) | AQI Range | Category |
|--------------|-----------|----------|
| 0 - 54 | 0-50 | Good |
| 55 - 154 | 51-100 | Moderate |
| 155 - 254 | 101-150 | Unhealthy for Sensitive Groups |
| 255 - 354 | 151-200 | Unhealthy |
| 355 - 424 | 201-300 | Very Unhealthy |
| 425 - 600 | 301-500 | Hazardous |

**Final AQI** = max(AQI_PM2.5, AQI_PM10)

---

## 🚧 Future Enhancements

- [ ] **ML-based AQI Prediction**: Forecast air quality trends
- [ ] **Historical Data Visualization**: Charts and graphs using Chart.js or D3.js
- [ ] **Alert System**: Notifications when AQI exceeds thresholds
- [ ] **Mobile App**: React Native companion app
- [ ] **Multi-location Support**: Track multiple sensor installations
- [ ] **Export Data**: CSV/Excel export functionality
- [ ] **Weather Integration**: Correlate AQI with weather data
- [ ] **User Authentication**: Personalized dashboards

---

## 🛠️ Troubleshooting

### Arduino Not Connecting
- Check USB cable and driver installation
- Verify correct COM port in Device Manager
- Update `SERIAL_PORT` in `serial_to_api.py`

### BME680 Not Found
- Check I2C wiring (SDA/SCL)
- Try I2C scanner sketch to verify address
- Ensure 3.3V power (not 5V)

### PMS5003 Not Reading
- Allow 30-second warm-up period
- Check serial wiring (TX→10, RX→11)
- Verify 5V power supply

### Database Connection Error
- Ensure PostgreSQL is running
- Verify DATABASE_URL in `.env`
- Check database credentials

### Frontend Not Loading Data
- Verify backend is running on port 8000
- Check CORS settings in `main.py`
- Open browser console for error messages

### Serial Data Not Parsing
- Check regex pattern in `serial_to_api.py`
- Verify Arduino output format matches expected pattern
- Increase baud rate if data corruption occurs

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is open-source and available under the MIT License.

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team

---

## 🙏 Acknowledgments

- **Adafruit** - For excellent sensor libraries
- **EPA** - For AQI calculation standards
- **FastAPI** - For the amazing Python web framework
- **React** - For the powerful UI library

---

<div align="center">
  <p>Made with ❤️ for a cleaner, healthier environment</p>
  <p><strong>Monitor Air Quality. Make Informed Decisions.</strong></p>
</div>
