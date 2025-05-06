import serial
from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime
import json
import os
from dotenv import load_dotenv

load_dotenv()

from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB connection settings
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

# Serial port settings
SERIAL_PORT = "COM3"  # Replace with your Arduino's serial port
BAUD_RATE = 9600

# Create InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Open serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

def write_to_influxdb(temperature, humidity, pressure):
    """Write data to InfluxDB."""
    point = Point("weather_measurements") \
        .tag("location", "Nis") \
        .field("temperature", temperature) \
        .field("humidity", humidity) \
        .field("pressure", pressure) \
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
                pressure = data["pressure"]

                print(f"Temperature: {temperature} °C, Humidity: {humidity} %, Pressure: {pressure}hBar")

                # Write data to InfluxDB
                write_to_influxdb(temperature, humidity, pressure)
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