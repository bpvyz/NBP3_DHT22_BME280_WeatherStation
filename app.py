from flask import Flask, request, jsonify, render_template, Response
from influxdb_client import InfluxDBClient
from datetime import datetime, timedelta, timezone
import pytz
import time
import json

app = Flask(__name__)

# InfluxDB connection settings
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "qJ0X5lH8RtqB-IWyPzaEDDqGGdc3xQ8M4HcinZRqqdOV-UnoRa6nQYwoYWRz_9jRGY5UBlIt1eLSVzuBi-52XA=="
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

    # Set time boundaries for the given date
    start_time = f"{previous_date}T23:00:00Z"  # 23:00 previous day in UTC
    end_time = f"{date_str}T22:59:59Z"        # 22:59 current day in UTC

    # Query InfluxDB
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


@app.route('/stream')
def stream():
    def event_stream():
        belgrade_tz = pytz.timezone('Europe/Belgrade')
        while True:
            try:
                # Query the latest data from InfluxDB
                query = f'''
                from(bucket: "{INFLUX_BUCKET}")
                    |> range(start: -1m)  // Get data from the last 1 minute
                    |> filter(fn: (r) => r["_measurement"] == "weather_measurements")
                    |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
                '''

                tables = query_api.query(query)
                data = [{"time": r.get_time().replace(tzinfo=timezone.utc).astimezone(belgrade_tz).strftime('%Y-%m-%d %H:%M:%S'),
                         "temperature": r["temperature"],
                         "humidity": r["humidity"],
                         "air_quality": r["air_quality"]} for table in tables for r in table.records]

                if data:
                    yield f"data: {json.dumps(data)}\n\n"  # Send data as SSE
            except Exception as e:
                print(f"Error querying InfluxDB: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"  # Send error as SSE

            time.sleep(30)  # Wait 10 seconds before the next update

    return Response(event_stream(), mimetype="text/event-stream")


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


@app.route('/delete-all', methods=['POST'])
def delete_all_data():
    try:
        # Define a time range that covers all data (e.g., from the beginning of time to now)
        start_time = "1970-01-01T00:00:00Z"  # Start from the Unix epoch
        end_time = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')  # Current time in UTC

        # Delete all data in the bucket
        delete_api.delete(start_time, end_time, '_measurement="weather_measurements"', bucket=INFLUX_BUCKET, org=INFLUX_ORG)

        return jsonify({"message": "All data deleted successfully"})
    except Exception as e:
        return jsonify({"error": f"Failed to delete all data: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True)