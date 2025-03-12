import serial
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime
import json

from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB connection settings
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "qJ0X5lH8RtqB-IWyPzaEDDqGGdc3xQ8M4HcinZRqqdOV-UnoRa6nQYwoYWRz_9jRGY5UBlIt1eLSVzuBi-52XA=="
INFLUX_ORG = "nbp"
INFLUX_BUCKET = "weatherstation"

# Serial port settings
SERIAL_PORT = "COM3"  # Replace with your Arduino's serial port
BAUD_RATE = 9600

# Create InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Open serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

def write_to_influxdb(temperature, humidity, air_quality):
    """Write data to InfluxDB."""
    point = Point("weather_measurements") \
        .tag("location", "Nis") \
        .field("temperature", temperature) \
        .field("humidity", humidity) \
        .field("air_quality", air_quality) \
        .time(datetime.utcnow(), WritePrecision.NS)
    write_api.write(INFLUX_BUCKET, INFLUX_ORG, point)

def main():
    """Read data from Serial and write to InfluxDB."""
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode("utf-8").strip()
            print(line)
            try:
                data = json.loads(line)
                temperature = data["temperature"]
                humidity = data["humidity"]
                air_quality = data["air_quality"]

                print(f"Temperature: {temperature} °C, Humidity: {humidity} %, AQ: {air_quality}")

                # Write data to InfluxDB
                write_to_influxdb(temperature, humidity, air_quality)
            except json.JSONDecodeError:
                print("Invalid JSON data received")
            except KeyError:
                print("Missing key in JSON data")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program stopped")
    finally:
        ser.close()
        client.close()