from flask import Flask, request, jsonify, render_template
from cassandra.cluster import Cluster
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta, timezone

app = Flask(__name__)

# Povezivanje na Cassandra
cluster = Cluster(['127.0.0.1'])
session = cluster.connect()
session.set_keyspace('weather_data')

# Povezivanje na InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "yyIUJ7Qr2QS9eJ3VS2jIuQ3vxctm_E4JaAIwnAocdZFeeUmQ_B0L_NRVvEcFnhjCeC_n_J3HNT-QBNDpNXGIDA=="
INFLUX_ORG = "nbp"
INFLUX_BUCKET = "weatherstation"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data', methods=['GET'])
def get_data():
    date = request.args.get('date', datetime.now(timezone.utc).strftime('%Y-%m-%d'))

    if date == datetime.now(timezone.utc).strftime('%Y-%m-%d'):
        # Izračunaj početak tekućeg dana (00:00) u UTC vremenu
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        # Upit prema InfluxDB za podatke od početka dana do sada
        query = f"""
        from(bucket: "{INFLUX_BUCKET}")
            |> range(start: {start_of_day.isoformat()})
            |> filter(fn: (r) => r["_measurement"] == "weather_measurements")
            |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
        """

        tables = query_api.query(query)
        data = [{"time": r.get_time(), "temperature": r["temperature"], "humidity": r["humidity"],
                 "air_quality": r["air_quality"]} for table in tables for r in table.records]

    else:
        # Dohvati podatke iz Cassandre za prethodne dane
        rows = session.execute(
            "SELECT * FROM weather_archive WHERE location = 'Nis' AND timestamp >= %s AND timestamp < %s",
            (date + " 00:00:00", date + " 23:59:59"))
        data = [{"time": row.timestamp, "temperature": row.temperature, "humidity": row.humidity,
                 "air_quality": row.air_quality} for row in rows]

    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
