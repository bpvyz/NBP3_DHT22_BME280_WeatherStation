from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime, timedelta
import random

from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB connection settings
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "yyIUJ7Qr2QS9eJ3VS2jIuQ3vxctm_E4JaAIwnAocdZFeeUmQ_B0L_NRVvEcFnhjCeC_n_J3HNT-QBNDpNXGIDA=="
INFLUX_ORG = "nbp"
INFLUX_BUCKET = "weatherstation"

# Create InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Generate data for every hour from 00:00 to the current hour
now = datetime.utcnow()
start_of_day = datetime(now.year, now.month, now.day)  # 00:00 of the current day
hours = int((now - start_of_day).total_seconds() // 3600)  # Total number of hours passed today

base_temp = 20  # Starting temperature in Celsius
base_humidity = 60  # Starting humidity in %
base_air_quality = 50  # Base air quality index

# Function to generate dummy data
def generate_dummy_data(timestamp):
    temp = base_temp + round(random.uniform(-1, 1), 1)  # Small random variation
    humidity = base_humidity + round(random.uniform(-2, 2), 1)  # Small random variation
    air_quality = base_air_quality + round(random.uniform(-5, 5), 1)  # Small random variation
    return temp, humidity, air_quality

# Write dummy data for each hour from 00:00 to the current hour
for hour in range(hours + 1):
    timestamp = start_of_day + timedelta(hours=hour)
    temperature, humidity, air_quality = generate_dummy_data(timestamp)

    # Create a point and write to InfluxDB
    point = Point("weather_measurements") \
        .tag("location", "Nis") \
        .field("temperature", temperature) \
        .field("humidity", humidity) \
        .field("air_quality", air_quality) \
        .time(timestamp, WritePrecision.NS)

    write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)

print(f"Dummy data for today has been written to InfluxDB (from 00:00 to {now.strftime('%H:%M')}).")
