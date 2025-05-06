#include <dht.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>

#define DHTPIN 2               // Pin where DHT11 is connected
#define SEALEVELPRESSURE_HPA 1013.25

dht DHT;                      // DHT11 object
Adafruit_BME280 bme;          // BME280 object (I2C)

// Setup
void setup() {
  Serial.begin(9600);

  // Initialize BME280
  if (!bme.begin(0x76)) {     // Try 0x76 or 0x77 depending on your module
    Serial.println("Could not find a valid BME280 sensor, check wiring!");
    while (1); // Stop execution if BME280 not found
  }

  Serial.println("DHT11 and BME280 initialized.");
}

// Loop
void loop() {
  // Read DHT11
  int chk = DHT.read11(DHTPIN);
  float temp = DHT.temperature;
  float humidity = DHT.humidity;

  // Read BME280 pressure
  float pressure = bme.readPressure() / 100.0; // Convert to hPa

  // Send as JSON
  send_to_serial(temp, humidity, pressure);

  delay(5000); // 30s delay
}

// JSON Serial Output
void send_to_serial(float temperature, float humidity, float pressure) {
  Serial.print("{\"temperature\":");
  Serial.print(temperature);
  Serial.print(",\"humidity\":");
  Serial.print(humidity);
  Serial.print(",\"pressure\":");
  Serial.print(pressure);
  Serial.println("}");
}
