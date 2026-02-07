import serial
import requests
import re

SERIAL_PORT = "COM5"   # change if needed
BAUD_RATE = 9600
API_URL = "http://127.0.0.1:8000/insert"

ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

pattern = re.compile(
    r"PM1.0:\s([\d.]+)\s\|\sPM2.5:\s([\d.]+)\s\|\sPM10:\s([\d.]+)\s\|\sAQI:\s(\d+)\s\(([^)]+)\)\s\|\sTemp:\s([\d.]+)\sC\s\|\sHumidity:\s([\d.]+)\s%\s\|\sGas:\s([\d.]+)"
)

print("Listening to Arduino...")

while True:
    line = ser.readline().decode(errors="ignore").strip()
    match = pattern.search(line)

    if match:
        data = {
            "pm1": float(match.group(1)),
            "pm25": float(match.group(2)),
            "pm10": float(match.group(3)),
            "aqi": int(match.group(4)),
            "aqi_category": match.group(5),
            "temperature": float(match.group(6)),
            "humidity": float(match.group(7)),
            "gas": float(match.group(8)),
        }

        r = requests.post(API_URL, json=data)
        print("Inserted:", data)
