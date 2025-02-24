from flask import Flask, request, jsonify, render_template
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta, timezone
import pytz

app = Flask(__name__)

# Povezivanje na InfluxDB
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "yyIUJ7Qr2QS9eJ3VS2jIuQ3vxctm_E4JaAIwnAocdZFeeUmQ_B0L_NRVvEcFnhjCeC_n_J3HNT-QBNDpNXGIDA=="
INFLUX_ORG = "nbp"
INFLUX_BUCKET = "weatherstation"

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
query_api = client.query_api()
delete_api = client.delete_api()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data', methods=['GET'])
def get_data():
    # Get the date from the request arguments
    date_str = request.args.get('date', datetime.now(pytz.timezone('Europe/Belgrade')).strftime('%Y-%m-%d'))

    # Parse the date string into a datetime object
    belgrade_tz = pytz.timezone('Europe/Belgrade')
    current_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=belgrade_tz)

    # Calculate the previous day's date
    previous_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')

    # Postavi vremenske granice za dati datum
    start_time = f"{previous_date}T23:00:00Z"  # 23:00 previous day in UTC
    end_time = f"{date_str}T22:59:59Z"        # 22:59 current day in UTC

    # Upit za InfluxDB
    query = f"""
    from(bucket: "{INFLUX_BUCKET}")
        |> range(start: {start_time}, stop: {end_time})
        |> filter(fn: (r) => r["_measurement"] == "weather_measurements")
        |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
    """

    tables = query_api.query(query)

    # Convert UTC time to 'Europe/Belgrade' timezone
    data = [{"time": r.get_time().replace(tzinfo=timezone.utc).astimezone(belgrade_tz).strftime('%Y-%m-%d %H:%M:%S'),
             "temperature": r["temperature"],
             "humidity": r["humidity"],
             "air_quality": r["air_quality"]} for table in tables for r in table.records]

    return jsonify(data)


@app.route('/delete', methods=['POST'])
def delete_data():
    # Get the date from the request
    date_str = request.json.get('date')
    if not date_str:
        return jsonify({"error": "Date parameter is required"}), 400

    # Parse the date string into a datetime object
    belgrade_tz = pytz.timezone('Europe/Belgrade')
    current_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=belgrade_tz)

    # Calculate the previous day's date
    previous_date = (current_date - timedelta(days=1)).strftime('%Y-%m-%d')

    # Define the time range for deletion
    start_time = f"{previous_date}T23:00:00Z"  # 23:00 previous day in UTC
    end_time = f"{date_str}T22:59:59Z"        # 22:59 current day in UTC

    # Delete data from InfluxDB
    delete_api.delete(start_time, end_time, f'_measurement="weather_measurements"', bucket=INFLUX_BUCKET, org=INFLUX_ORG)

    return jsonify({"message": f"Data for {date_str} deleted successfully"})


if __name__ == '__main__':
    app.run(debug=True)