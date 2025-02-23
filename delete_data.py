from influxdb_client import InfluxDBClient
from datetime import datetime

# InfluxDB connection settings
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "yyIUJ7Qr2QS9eJ3VS2jIuQ3vxctm_E4JaAIwnAocdZFeeUmQ_B0L_NRVvEcFnhjCeC_n_J3HNT-QBNDpNXGIDA=="
INFLUX_ORG = "nbp"
INFLUX_BUCKET = "weatherstation"

# Create InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
delete_api = client.delete_api()

# Get the current time in ISO 8601 format
now = datetime.utcnow().isoformat() + "Z"  # This is the current time in UTC
start = "1970-01-01T00:00:00Z"
stop = "2026-01-01T00:00:00Z"
# Delete all data from the bucket by specifying a time range (since the beginning of time to now)
delete_api.delete(start, stop, '_measurement="weather_measurements"', bucket=INFLUX_BUCKET, org=INFLUX_ORG)

print("All data deleted from InfluxDB.")
