#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <SoftwareSerial.h>
#include <PMS.h>

#define SEALEVELPRESSURE_HPA (1013.25)

// BME680
Adafruit_BME680 bme;

// PMS5003
SoftwareSerial pmsSerial(10, 11);
PMS pms(pmsSerial);
PMS::DATA data;

void setup() {
  Serial.begin(9600);
  pmsSerial.begin(9600);

  if (!bme.begin()) {
    Serial.println("BME680 not found");
    while (1);
  }

  bme.setGasHeater(320, 150);
  Serial.println("BME680 + PMS5003 started");
}

void loop() {

  // ---- BME680 ----
  if (bme.performReading()) {
    Serial.print("Temp: ");
    Serial.print(bme.temperature);
    Serial.print(" C | ");

    Serial.print("Humidity: ");
    Serial.print(bme.humidity);
    Serial.print(" % | ");

    Serial.print("Gas: ");
    Serial.print(bme.gas_resistance / 1000);
    Serial.print(" KOhms | ");
  }

  // ---- PMS5003 ----
  if (pms.read(data)) {
    Serial.print("PM2.5: ");
    Serial.print(data.PM_AE_UG_2_5);
    Serial.print(" ug/m3 | ");

    Serial.print("PM10: ");
    Serial.println(data.PM_AE_UG_10_0);
  }

  Serial.println("--------------------------------");
  delay(3000);
}
