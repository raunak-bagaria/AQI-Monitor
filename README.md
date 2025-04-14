# Intelligent Indoor Air Quality Monitor

## Overview
This project implements an intelligent indoor air quality monitoring system that continuously tracks various environmental parameters using an ESP32 microcontroller and a set of sensors. The system collects data on temperature, humidity, air quality, and dust levels, and presents this information through a web-based dashboard.

## Features
- Real-time monitoring of indoor environmental conditions
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
2. **Flask web application**: Receives data from ESP32, stores it in memory, and provides a web interface for visualization

## Setup and Installation

### Hardware Setup
1. Connect the sensors to the ESP32 according to the connections specified in the project
   - DHT11: Data pin connected to GPIO pin specified in sketch.ino
   - MQ135: Analog output connected to analog pin specified in sketch.ino
   - GP2Y1010AU0F: Follow the connection diagram with the 150Ω resistor and 220μF capacitor

### ESP32 Firmware Installation
1. Open the `sketch.ino` file in the Arduino IDE
2. Install required Arduino libraries:
   - DHT sensor library
   - ArduinoJson
   - Any other libraries referenced in the sketch
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
python3 -m venv aqi
```

5. Activate the virtual environment:
   - On Linux/macOS:
   ```bash
   source aqi/bin/activate
   ```
   - On Windows:
   ```bash
   aqi\Scripts\activate
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

## Web Dashboard
The dashboard displays:
- Current temperature, humidity, air quality raw value, and dust level raw value
- Historical graphs of all parameters over time
- The data refreshes automatically every 60 seconds

## Data Analysis
The system correlates air quality with:
- Temperature and humidity conditions
- Time of day patterns
- Historical trends

## Troubleshooting
- If no data appears on the dashboard, check that the ESP32 is properly connected and sending data
- Verify that the correct serial port is configured in the Flask application
- Check the console for any error messages from the Flask application
- If you encounter dependency issues, ensure you're using the correct Python version and that all requirements are installed

## Future Improvements
- Calibration of MQ135 and dust sensors for more accurate readings
- Adding support for multiple monitoring stations
- Implementing user-configurable alerts when air quality deteriorates
- Mobile application for remote monitoring