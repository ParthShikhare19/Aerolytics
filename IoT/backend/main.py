from fastapi import FastAPI
import psycopg2
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB connection
conn = psycopg2.connect(DATABASE_URL)

@app.post("/insert")
def insert_data(data: dict):
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO air_quality_readings
        (pm1, pm25, pm10, aqi, aqi_category, temperature, humidity, gas_resistance)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["pm1"],
        data["pm25"],
        data["pm10"],
        data["aqi"],
        data["aqi_category"],
        data["temperature"],
        data["humidity"],
        data["gas"]
    ))

    conn.commit()
    cur.close()

    return {"status": "success"}

@app.get("/latest")
def get_latest_data():
    cur = conn.cursor()
    cur.execute("""
        SELECT
            pm1, pm25, pm10,
            aqi, aqi_category,
            temperature, humidity, gas_resistance,
            created_at
        FROM air_quality_readings
        ORDER BY created_at DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()

    if row is None:
        return {"message": "No data available"}

    return {
        "pm1": row[0],
        "pm25": row[1],
        "pm10": row[2],
        "aqi": row[3],
        "aqi_category": row[4],
        "temperature": row[5],
        "humidity": row[6],
        "gas": row[7],
        "created_at": row[8]
    }
