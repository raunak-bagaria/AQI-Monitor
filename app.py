from flask import Flask, request, jsonify, render_template
from datetime import datetime
import csv
import os
import json
from aqi_calculator import calculate_overall_aqi  # Import our AQI calculator

app = Flask(__name__)

# Define CSV file path and fieldnames - renamed fields and added raw_dust_value
CSV_FILE = 'sensor_data.csv'
FIELDNAMES = ['timestamp', 'temperature', 'humidity', 'gas_ppm', 'dust_density', 'raw_dust_value']

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
                    
                    # Handle renamed fields for backward compatibility
                    if 'gas_ppm' in row:
                        row['gas_ppm'] = float(row['gas_ppm']) if row.get('gas_ppm') else None
                    elif 'air_quality_raw' in row:
                        row['gas_ppm'] = float(row['air_quality_raw']) if row.get('air_quality_raw') else None
                        row.pop('air_quality_raw', None)
                    
                    if 'dust_density' in row:
                        row['dust_density'] = float(row['dust_density']) if row.get('dust_density') else None
                    elif 'dust_raw' in row:
                        row['dust_density'] = float(row['dust_raw']) if row.get('dust_raw') else None
                        row.pop('dust_raw', None)
                    
                    # Handle the new raw_dust_value field
                    if 'raw_dust_value' in row:
                        row['raw_dust_value'] = int(row['raw_dust_value']) if row.get('raw_dust_value') else None
                    
                    # Calculate AQI for each data point
                    row['aqi'] = calculate_overall_aqi(row)
                    
                    data_history.append(row)
                except (ValueError, TypeError) as e:
                    print(f"Skipping row due to conversion error: {row}, Error: {e}")
                    continue

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
        # Get the raw request data for debugging
        raw_data = request.data.decode('utf-8')
        print(f"Raw request data: {raw_data}")
        
        # Parse the JSON data
        data = request.get_json()
        
        if not data:
            print("Error: No JSON data received or invalid JSON format")
            return jsonify({"status": "error", "message": "No JSON data received or invalid format"}), 400

        # Add timestamp
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Map old field names to new ones if needed
        if 'air_quality_raw' in data and 'gas_ppm' not in data:
            data['gas_ppm'] = data.pop('air_quality_raw')
        
        if 'dust_raw' in data and 'dust_density' not in data:
            data['dust_density'] = data.pop('dust_raw')
            
        # Print detailed data for debugging
        print(f"Parsed data: {json.dumps(data, indent=2)}")
        
        # Basic validation (check if expected keys exist)
        required_keys = ['temperature', 'humidity', 'gas_ppm', 'dust_density']
        # Note: raw_dust_value is optional for backward compatibility
        
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            error_msg = f"Missing required keys: {', '.join(missing_keys)}"
            print(f"Error: {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 400

        # Check for null or invalid values
        invalid_values = []
        for key in required_keys:
            if data[key] is None:
                invalid_values.append(f"{key} is null")
            elif isinstance(data[key], (int, float)) and (data[key] < -1000 or data[key] > 10000):
                # Basic range check to catch obvious errors
                invalid_values.append(f"{key} has suspicious value: {data[key]}")
        
        if invalid_values:
            error_msg = f"Invalid values detected: {', '.join(invalid_values)}"
            print(f"Error: {error_msg}")
            return jsonify({"status": "error", "message": error_msg}), 400

        print(f"Received data (validated): {data}")  # Log received data to console

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

        return jsonify({
            "status": "success", 
            "message": "Data received and saved",
            "received_data": data  # Echo back the data for debugging
        }), 200
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Run on all available network interfaces (0.0.0.0)
    # Make sure port 5000 is open in your firewall if accessing from another device
    app.run(host='0.0.0.0', port=5000, debug=True)
