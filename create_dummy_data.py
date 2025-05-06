from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime, timedelta
from dateutil import tz
import random
import math
from dotenv import load_dotenv
import os

from influxdb_client.client.write_api import SYNCHRONOUS

load_dotenv()

# InfluxDB connection settings
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

# Create InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Timezone settings
local_timezone = tz.gettz("Europe/Belgrade")
utc_timezone = tz.gettz("UTC")

# Generate data for the past 7 days (every 10 minutes)
now = datetime.now(local_timezone)
seven_days_ago = datetime(now.year, now.month, now.day, tzinfo=local_timezone) - timedelta(days=7)

# Base values for the outdoor environment
base_temp = 20        # °C
base_humidity = 60    # %
base_pressure = 1013  # hPa

# Realistic data generation based on outdoor patterns
def generate_realistic_data(timestamp, base_temp, base_humidity, base_pressure):
    hour_of_day = timestamp.hour + timestamp.minute / 60

    # Simulate diurnal temperature change
    temp_variation = 10 * math.sin(math.radians(hour_of_day * 15 - 90))
    temperature = round(base_temp + temp_variation + random.uniform(-0.5, 0.5), 1)

    # Simulate daily humidity change
    humidity_variation = 10 * math.cos(math.radians(hour_of_day * 15 - 30))
    humidity = round(base_humidity + humidity_variation + random.uniform(-1, 1), 1)

    # Simulate slow pressure changes (e.g., weather fronts)
    pressure_variation = 5 * math.sin(math.radians((timestamp - seven_days_ago).total_seconds() / 3600 * 5))
    pressure = round(base_pressure + pressure_variation + random.uniform(-0.5, 0.5), 1)

    temperature = max(-20, min(temperature, 50))
    humidity = max(0, min(humidity, 100))
    pressure = max(950, min(pressure, 1050))

    return temperature, humidity, pressure

# Collect data points in batches
points_batch = []
current_time = seven_days_ago

while current_time.date() <= now.date():
    day_start = datetime(current_time.year, current_time.month, current_time.day, tzinfo=local_timezone)

    if current_time.date() == now.date():
        day_end = now
    else:
        day_end = day_start + timedelta(hours=23, minutes=50)

    while day_start <= day_end:
        temperature, humidity, pressure = generate_realistic_data(day_start, base_temp, base_humidity, base_pressure)
        utc_timestamp = day_start.astimezone(utc_timezone)

        point = Point("weather_measurements") \
            .tag("location", "Nis") \
            .field("temperature", temperature) \
            .field("humidity", humidity) \
            .field("pressure", pressure) \
            .time(utc_timestamp, WritePrecision.NS)

        points_batch.append(point)
        day_start += timedelta(minutes=10)

    current_time += timedelta(days=1)

# Write all points in a single request
write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=points_batch)

print("Realistic dummy pressure data for the past 7 days has been written to InfluxDB.")
