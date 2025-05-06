from influxdb_client import InfluxDBClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

# InfluxDB connection settings
INFLUX_URL = os.getenv("INFLUX_URL")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
INFLUX_ORG = os.getenv("INFLUX_ORG")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")

# Create InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
delete_api = client.delete_api()

# Get the current time in ISO 8601 format
now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

start = "1970-01-01T00:00:00Z"
stop = "2026-01-01T00:00:00Z"
# Delete all data from the bucket by specifying a time range (since the beginning of time to now)
delete_api.delete(start, stop, '_measurement="weather_measurements"', bucket=INFLUX_BUCKET, org=INFLUX_ORG)

print("All data deleted from InfluxDB.")
