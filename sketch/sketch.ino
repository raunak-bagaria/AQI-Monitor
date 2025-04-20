#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

#define DHTPIN 4
#define DHTTYPE DHT11

#define MQ135_PIN 32
#define DUST_ANALOG_PIN 34
#define DUST_LED_PIN 25

DHT dht(DHTPIN, DHTTYPE);

// --- WiFi and Server Configuration ---
const char* ssid = "moto g24 power_7522"; // Replace with your WiFi SSID
const char* password = "Bagaria@2004"; // Replace with your WiFi Password
const char* serverUrl = "http://192.168.152.235:5000/data"; // Replace SERVER_IP with the IP address of the machine running Flask

void setup() {
  Serial.begin(115200);
  delay(1000);

  dht.begin();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  pinMode(DUST_LED_PIN, OUTPUT);
}

float getDustDensity() {
  // GP2Y1010AU0F pulse + read
  digitalWrite(DUST_LED_PIN, LOW);
  delayMicroseconds(280);
  int raw = analogRead(DUST_ANALOG_PIN);
  delayMicroseconds(40);
  digitalWrite(DUST_LED_PIN, HIGH);
  delayMicroseconds(9680);

  // Debug print for raw value
  Serial.print("Raw Dust ADC Value: ");
  Serial.println(raw);

  // Convert the ADC reading to voltage (0-3.3V for ESP32)
  float voltage = raw * (3.3 / 4095.0);  // ESP32 has 12-bit ADC (0-4095)
  
  // Debug print the voltage
  Serial.print("Dust Sensor Voltage: ");
  Serial.print(voltage);
  Serial.println(" V");
  
  // The datasheet indicates that the output voltage vs. dust density is roughly linear
  // with 0V corresponding to 0 µg/m³ and a sensitivity of about 0.5V per 100 µg/m³
  // The sensor has a baseline voltage of around 0.6V in clean air
  
  // Modified formula to better handle low values and account for baseline
  if (voltage < 0.6) {
    // Below baseline, considered as no dust
    return 0.0;
  } else {
    // Linear conversion using datasheet formula: 100 µg/m³ per 0.5V above baseline
    float dustDensity = (voltage - 0.6) * 200.0;  // (V - 0.6) * (100 µg/m³ / 0.5V)
    
    // Sanity check - cap at reasonable maximum
    if (dustDensity > 1000) {
      dustDensity = 1000;  // Cap at 1000 µg/m³ as a reasonable maximum for indoor air
    }
    
    return dustDensity;
  }
}

float getMQ135PPM() {
  int raw = analogRead(MQ135_PIN);
  
  // Debug print for raw value
  Serial.print("Raw MQ135 ADC Value: ");
  Serial.println(raw);
  
  float voltage = raw * (3.3 / 4095.0);  // 0 to 3.3V range
  float ppm = map(raw, 0, 4095, 400, 1000); // Estimation: clean air ~400ppm to polluted ~1000ppm
  return ppm;
}

void loop() {
  // Read sensor data
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  float dustDensity = getDustDensity();
  float gasPPM = getMQ135PPM();
  
  // Store raw dust sensor value
  int rawDustValue = analogRead(DUST_ANALOG_PIN);

  // Check if readings are valid
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("DHT11 failed to read. Retrying in 5 seconds...");
    delay(5000);
    return;
  }

  // Print sensor readings for debugging
  Serial.println("Sensor Readings:");
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");
  
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
  
  Serial.print("Dust Density: ");
  Serial.print(dustDensity);
  Serial.println(" µg/m³");
  
  Serial.print("Gas PPM: ");
  Serial.print(gasPPM);
  Serial.println(" PPM");
  
  Serial.print("Raw Dust Value: ");
  Serial.println(rawDustValue);

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("Sending data to server...");
    
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Clear the document before populating it
    StaticJsonDocument<256> doc;
    
    // Send values with renamed fields plus raw dust value
    doc["temperature"] = temperature;
    doc["humidity"] = humidity;
    doc["gas_ppm"] = gasPPM;         // Renamed from air_quality_raw
    doc["dust_density"] = dustDensity; // Renamed from dust_raw
    doc["raw_dust_value"] = rawDustValue; // Added raw dust sensor value

    String jsonString;
    serializeJson(doc, jsonString);
    
    Serial.print("Sending JSON: ");
    Serial.println(jsonString);
    
    // Send the request
    int httpResponseCode = http.POST(jsonString);

    Serial.print("HTTP Response Code: ");
    Serial.println(httpResponseCode);
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server response: " + response);
      
      if (httpResponseCode == 200) {
        Serial.println("Data sent successfully!");
      } else {
        Serial.print("Server returned error: ");
        Serial.println(httpResponseCode);
        Serial.println(response);
      }
    } else {
      Serial.print("Error sending HTTP request: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi disconnected! Attempting to reconnect...");
    WiFi.begin(ssid, password);
    
    // Wait a bit for connection
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 10) {
      delay(500);
      Serial.print(".");
      attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("Reconnected to WiFi!");
    } else {
      Serial.println("Failed to reconnect.");
    }
  }

  Serial.println("Waiting 30 seconds before next reading...");
  Serial.println("=======================================");
  delay(30000);  // Send every 30 seconds
}
