#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <SoftwareSerial.h>
#include <PMS.h>

// -------- BME680 --------
Adafruit_BME680 bme;

// -------- PMS5003 --------
SoftwareSerial pmsSerial(10, 11); // RX, TX
PMS pms(pmsSerial);
PMS::DATA data;

unsigned long lastPrint = 0;

// store last PMS values
float pm1 = 0;
float pm25 = 0;
float pm10 = 0;
bool pmsDataAvailable = false;


// -------- AQI FUNCTIONS --------
int calculateAQI(float C, float BP_lo, float BP_hi, int I_lo, int I_hi) {
  return ((I_hi - I_lo) * (C - BP_lo)) / (BP_hi - BP_lo) + I_lo;
}

int aqi_pm25(float pm) {
  if (pm <= 12.0) return calculateAQI(pm, 0.0, 12.0, 0, 50);
  else if (pm <= 35.4) return calculateAQI(pm, 12.1, 35.4, 51, 100);
  else if (pm <= 55.4) return calculateAQI(pm, 35.5, 55.4, 101, 150);
  else if (pm <= 150.4) return calculateAQI(pm, 55.5, 150.4, 151, 200);
  else if (pm <= 250.4) return calculateAQI(pm, 150.5, 250.4, 201, 300);
  else return calculateAQI(pm, 250.5, 500.0, 301, 500);
}

int aqi_pm10(float pm) {
  if (pm <= 54) return calculateAQI(pm, 0, 54, 0, 50);
  else if (pm <= 154) return calculateAQI(pm, 55, 154, 51, 100);
  else if (pm <= 254) return calculateAQI(pm, 155, 254, 101, 150);
  else if (pm <= 354) return calculateAQI(pm, 255, 354, 151, 200);
  else if (pm <= 424) return calculateAQI(pm, 355, 424, 201, 300);
  else return calculateAQI(pm, 425, 600, 301, 500);
}

String airQualityLevel(int aqi) {
  if (aqi <= 50) return "Good";
  else if (aqi <= 100) return "Moderate";
  else if (aqi <= 150) return "Unhealthy (Sensitive)";
  else if (aqi <= 200) return "Unhealthy";
  else if (aqi <= 300) return "Very Unhealthy";
  else return "Hazardous";
}


// -------- SETUP --------
void setup() {

  Serial.begin(9600);

  pmsSerial.begin(9600);

  Serial.println("System started");

  if (!bme.begin(0x76)) {
    Serial.println("Trying BME680 at 0x77...");
    if (!bme.begin(0x77)) {
      Serial.println("BME680 not found");
      while (1);
    }
  }

  bme.setGasHeater(320, 150);

  Serial.println("Warming PMS5003...");
  delay(30000);

  Serial.println("Sensors ready");
}


// -------- LOOP --------
void loop() {

  // Read PMS continuously
  if (pms.read(data)) {
    pm1 = data.PM_AE_UG_1_0;
    pm25 = data.PM_AE_UG_2_5;
    pm10 = data.PM_AE_UG_10_0;
    pmsDataAvailable = true;
  }

  // Print every 5 seconds
  if (millis() - lastPrint > 5000) {

    lastPrint = millis();

    int aqi25 = aqi_pm25(pm25);
    int aqi10 = aqi_pm10(pm10);
    int finalAQI = max(aqi25, aqi10);

    // PMS DATA
    if (pmsDataAvailable) {
      Serial.print("PM1.0: ");
      Serial.print(pm1);

      Serial.print(" | PM2.5: ");
      Serial.print(pm25);

      Serial.print(" | PM10: ");
      Serial.print(pm10);

      Serial.print(" | AQI: ");
      Serial.print(finalAQI);
      Serial.print(" (");
      Serial.print(airQualityLevel(finalAQI));
      Serial.print(") | ");
    }
    else {
      Serial.print("PMS: No data | ");
    }

    // BME680 DATA
    if (bme.performReading()) {

      Serial.print("Temp: ");
      Serial.print(bme.temperature);

      Serial.print(" C | Humidity: ");
      Serial.print(bme.humidity);

      Serial.print(" % | Gas: ");
      Serial.print(bme.gas_resistance / 1000);

      Serial.print(" KOhms");
    }

    Serial.println();
    Serial.println("--------------------------------");
  }
}