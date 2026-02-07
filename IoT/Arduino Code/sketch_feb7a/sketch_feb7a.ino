#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>

#define SEALEVELPRESSURE_HPA (1013.25)

Adafruit_BME680 bme;  // I2C

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("BME680 test starting...");

  if (!bme.begin()) {
    Serial.println("❌ Could not find BME680 sensor!");
    while (1);
  }

  // Sensor configuration
  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150); // 320°C for 150 ms

  Serial.println("✅ BME680 initialized successfully");
}

void loop() {
  if (!bme.performReading()) {
    Serial.println("Failed to perform reading");
    return;
  }

  Serial.print("Temperature = ");
  Serial.print(bme.temperature);
  Serial.println(" °C");

  Serial.print("Humidity = ");
  Serial.print(bme.humidity);
  Serial.println(" %");

  Serial.print("Pressure = ");
  Serial.print(bme.pressure / 100.0);
  Serial.println(" hPa");

  Serial.print("Gas Resistance = ");
  Serial.print(bme.gas_resistance / 1000.0);
  Serial.println(" KOhms");

  Serial.println("-----------------------");
  delay(2000);
}
