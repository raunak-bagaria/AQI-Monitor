# Intelligent Indoor Air Quality Monitor

## Overview
This project implements an intelligent indoor air quality monitoring system that continuously tracks various environmental parameters using an ESP32 microcontroller and a set of sensors. The system collects data on temperature, humidity, gas concentration, and dust levels, calculates an Air Quality Index (AQI), and presents this information through a dashboard with actionable recommendations.

## Features
- Real-time monitoring of indoor environmental conditions
- Air Quality Index (AQI) calculation based on EPA-like standards
- Personalized recommendations based on current air quality
- Historical data visualization through interactive charts
- Automatic data collection and storage
- Web-based dashboard for easy access from any device on the local network

## Hardware Components
- ESP32 DevKitV1 microcontroller
- DHT11 Temperature and Humidity sensor
- MQ135 Air Quality sensor
- GP2Y1010AU0F Dust sensor
- 150Ω resistor (for GP2Y1010AU0F)
- 220μF capacitor (for GP2Y1010AU0F)
- Breadboard
- Jumper wires

## Software Architecture
The system consists of two main components:
1. **Arduino firmware (sketch.ino)**: Runs on the ESP32, collects data from sensors, and sends JSON-formatted data to the server
2. **Flask web application**: Receives data from ESP32, stores it persistently in a CSV file, and provides a web interface for visualization and analysis

## Setup and Installation

### Hardware Setup
1. Connect the sensors to the ESP32 according to the connections specified in the project
   - DHT11: Data pin connected to GPIO pin specified in sketch.ino
   - MQ135: Analog output connected to analog pin specified in sketch.ino
   - GP2Y1010AU0F: Follow the connection diagram with the 150Ω resistor and 220μF capacitor
2. Refer to [`ConnectionsGuide.md`](ConnectionsGuide.md) in the project directory for component connections
3. Double-check all connections before powering the system to avoid damage to sensors or microcontroller

### ESP32 Firmware Installation
1. Open the `sketch.ino` file in the Arduino IDE
2. Install required Arduino libraries:
   - WiFi (built-in with ESP32 board support)
   - HTTPClient (built-in with ESP32 board support)
   - DHT sensor library by Adafruit
   - ArduinoJson by Benoit Blanchon
3. Select ESP32 board in the Arduino IDE
4. Compile and upload the sketch to your ESP32

### Flask Web Application Setup
1. Ensure you have Python 3.12+ installed
2. Clone the repository or download the project files
3. Navigate to the project directory:
```bash
cd /path/to/AQI-Monitor
```

4. Create a virtual environment:
```bash
python3 -m venv venv
```

5. Activate the virtual environment:
   - On Linux/macOS:
   ```bash
   source venv/bin/activate
   ```
   - On Windows:
   ```bash
   venv\Scripts\activate
   ```

6. Install the required dependencies:
```bash
pip install -r requirements.txt
```

7. Run the Flask application:
```bash
python3 app.py
```

## Usage
1. Ensure the ESP32 is powered on and running the uploaded sketch
2. Make sure the ESP32 is sending data to the correct serial port
3. Start the Flask application as described above
4. Open a web browser and navigate to:
   - `http://127.0.0.1:5000` if accessing locally
   - `http://<your-computer-ip>:5000` if accessing from another device on the network

## Air Quality Index (AQI) Calculation

The system calculates an Indoor Air Quality Index based on sensor readings:

### Gas Concentration (MQ135 Sensor)
| Gas PPM Range | AQI Value | Category |
|---------------|-----------|----------|
| 400-500 | 0-50 | Good |
| 500-700 | 51-100 | Moderate |
| 700-800 | 101-150 | Unhealthy for Sensitive Groups |
| 800-900 | 151-200 | Unhealthy |
| 900-1000 | 201-300 | Very Unhealthy |
| >1000 | 301+ | Hazardous |

### Dust Density (GP2Y1010AU0F Sensor)
| Dust Density (µg/m³) | AQI Value | Category |
|----------------------|-----------|----------|
| 0-12 | 0-50 | Good |
| 12.1-35.4 | 51-100 | Moderate |
| 35.5-55.4 | 101-150 | Unhealthy for Sensitive Groups |
| 55.5-150.4 | 151-200 | Unhealthy |
| 150.5-250.4 | 201-300 | Very Unhealthy |
| 250.5-500.4 | 301-500 | Hazardous |

### Supporting Measurements
- **Humidity**: Categorized as Too Dry (<30%), Optimal (30-50%), Acceptable (50-60%), or Too Humid (>60%)
- **Temperature**: Categorized as Too Cold (<18°C), Comfortable (18-24°C), or Too Warm (>24°C)

The overall AQI is determined by the highest individual pollutant index value. Based on this value and supporting measurements, the system provides specific recommendations to improve air quality.

## Web Dashboard
The dashboard displays:
- Overall Air Quality Index with color-coded indicator
- Custom recommendations based on current air quality and environmental conditions
- Current temperature, humidity, gas concentration, and dust density readings
- Historical graphs of all parameters over time
- The data refreshes automatically every 60 seconds

## Data Analysis
The system correlates air quality with:
- Temperature and humidity conditions
- Time of day patterns
- Historical trends

## Future Improvements
- Calibration of MQ135 and dust sensors for more accurate readings
- Adding support for multiple monitoring stations
- Implementing user-configurable alerts when air quality deteriorates
- Mobile application for remote monitoring