from cassandra.cluster import Cluster
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta

# Povezivanje na Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()
session.set_keyspace('weather_data')

# Povezivanje na InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "pKq6OVKAfJYN0HJcHqrR4L9ZtKYbw6ZJKqcm7JBeQeEBeBFRVrtHPviup_4Oph_51xeMrwf3hfA3UG7ufd9n7w=="
INFLUX_ORG = "nbp"
INFLUX_BUCKET = "weatherstation"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()

# Dohvatanje podataka iz InfluxDB za jučerašnji dan
yesterday = (datetime.utcnow() - timedelta(days=1))
yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat() + "Z"

query = f"""
from(bucket: "{INFLUX_BUCKET}")
    |> range(start: {yesterday_start}, stop: {yesterday_end})
    |> filter(fn: (r) => r["_measurement"] == "weather_measurements")
    |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
"""

# Ubacivanje podataka u Cassandru i brisanje iz InfluxDB
for table in tables:
    for record in table.records:
        session.execute("""
            INSERT INTO weather_archive (location, timestamp, temperature, humidity, air_quality)
            VALUES (%s, %s, %s, %s, %s)
        """, ("Belgrade", record.get_time(), record["temperature"], record["humidity"], record["air_quality"]))

print("Podaci prebačeni u Cassandru!")
