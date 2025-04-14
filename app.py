from flask import Flask, request, jsonify, render_template
from datetime import datetime
import csv
import os

app = Flask(__name__)

# Define CSV file path and fieldnames
CSV_FILE = 'sensor_data.csv'
FIELDNAMES = ['timestamp', 'temperature', 'humidity', 'air_quality_raw', 'dust_raw']

@app.route('/')
def index():
    """Serve the dashboard page."""
    data_history = []
    try:
        # Read data from CSV file
        with open(CSV_FILE, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            # Convert relevant fields back to numbers for the chart
            for row in reader:
                try:
                    row['temperature'] = float(row['temperature']) if row.get('temperature') else None
                    row['humidity'] = float(row['humidity']) if row.get('humidity') else None
                    row['air_quality_raw'] = int(row['air_quality_raw']) if row.get('air_quality_raw') else None
                    row['dust_raw'] = int(row['dust_raw']) if row.get('dust_raw') else None
                    data_history.append(row)
                except (ValueError, TypeError) as e:
                    print(f"Skipping row due to conversion error: {row}, Error: {e}") # Handle potential errors during conversion
                    continue # Skip rows with bad data

    except FileNotFoundError:
        print(f"CSV file '{CSV_FILE}' not found. Will be created on first data POST.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")

    # Pass the data read from CSV (or empty list) to the template
    return render_template('index.html', data_history=data_history)

@app.route('/data', methods=['POST'])
def receive_data():
    """Receive sensor data from ESP32 and append to CSV."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400

        # Add timestamp
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Basic validation (check if expected keys exist)
        required_keys = ['temperature', 'humidity', 'air_quality_raw', 'dust_raw']
        if not all(key in data for key in required_keys):
             return jsonify({"status": "error", "message": "Missing data keys"}), 400

        print(f"Received data: {data}") # Log received data to console

        # Append data to CSV
        file_exists = os.path.isfile(CSV_FILE)
        try:
            with open(CSV_FILE, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
                # Write header only if file is new or empty
                if not file_exists or os.path.getsize(CSV_FILE) == 0:
                    writer.writeheader()
                # Ensure data dictionary only contains keys defined in FIELDNAMES
                filtered_data = {k: data.get(k) for k in FIELDNAMES}
                writer.writerow(filtered_data)
        except IOError as e:
             print(f"Error writing to CSV file: {e}")
             return jsonify({"status": "error", "message": "Could not write to CSV file"}), 500

        return jsonify({"status": "success", "message": "Data received and saved"}), 200
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Run on all available network interfaces (0.0.0.0)
    # Make sure port 5000 is open in your firewall if accessing from another device
    app.run(host='0.0.0.0', port=5000, debug=True)
