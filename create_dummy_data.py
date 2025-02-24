from influxdb_client import InfluxDBClient, Point, WritePrecision
from datetime import datetime, timedelta
from dateutil import tz
import random
import math

from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB connection settings
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "yyIUJ7Qr2QS9eJ3VS2jIuQ3vxctm_E4JaAIwnAocdZFeeUmQ_B0L_NRVvEcFnhjCeC_n_J3HNT-QBNDpNXGIDA=="
INFLUX_ORG = "nbp"
INFLUX_BUCKET = "weatherstation"

# Create InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Timezone settings
local_timezone = tz.gettz("Europe/Belgrade")  # Replace with your local timezone
utc_timezone = tz.gettz("UTC")

# Generate data for the past 7 days (every 10 minutes)
now = datetime.now(local_timezone)
seven_days_ago = datetime(now.year, now.month, now.day, tzinfo=local_timezone) - timedelta(days=7)

# Base values for the outdoor environment
base_temp = 20  # Starting temperature in Celsius
base_humidity = 60  # Starting humidity in %
base_air_quality = 75  # Base air quality index

# Realistic data generation based on outdoor patterns
def generate_realistic_data(timestamp, base_temp, base_humidity, base_air_quality):
    hour_of_day = timestamp.hour + timestamp.minute / 60
    temp_variation = 10 * math.sin(math.radians(hour_of_day * 15 - 90))
    temperature = round(base_temp + temp_variation + random.uniform(-0.5, 0.5), 1)

    humidity_variation = 10 * math.cos(math.radians(hour_of_day * 15 - 30))
    humidity = round(base_humidity + humidity_variation + random.uniform(-1, 1), 1)

    air_quality_variation = 5 * math.sin(math.radians(hour_of_day * 20))
    air_quality = round(base_air_quality + air_quality_variation + random.uniform(-1, 1), 1)

    air_quality = max(0, min(air_quality, 300))
    humidity = max(0, min(humidity, 100))
    temperature = max(-20, min(temperature, 50))

    return temperature, humidity, air_quality

# Collect data points in batches
points_batch = []
current_time = seven_days_ago

while current_time.date() <= now.date():
    # Start at 00:00 in the local timezone for the given day
    day_start = datetime(current_time.year, current_time.month, current_time.day, tzinfo=local_timezone)

    # Determine the last timestamp to generate for this day
    if current_time.date() == now.date():
        day_end = now  # For today, only generate until the current time
    else:
        day_end = day_start + timedelta(hours=23, minutes=50)  # For past days, go until 23:50

    # Generate data points from 00:00 to 23:50 in the local timezone
    while day_start <= day_end:
        # Update data using generate_realistic_data
        temperature, humidity, air_quality = generate_realistic_data(day_start, base_temp, base_humidity, base_air_quality)

        # Convert the timestamp to UTC before writing to InfluxDB
        utc_timestamp = day_start.astimezone(utc_timezone)

        # Create a point and add it to the batch
        point = Point("weather_measurements") \
            .tag("location", "Nis") \
            .field("temperature", temperature) \
            .field("humidity", humidity) \
            .field("air_quality", air_quality) \
            .time(utc_timestamp, WritePrecision.NS)

        points_batch.append(point)

        # Move to the next 10-minute interval
        day_start += timedelta(minutes=10)

    # Move to the next day
    current_time += timedelta(days=1)

# Write all points in a single request
write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=points_batch)

print(f"Realistic dummy data for the past 7 days (up to now) has been written to InfluxDB.")