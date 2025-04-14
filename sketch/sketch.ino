#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h> // Add ArduinoJson library
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHTPIN 4     // DHT11 connected to GPIO4
#define DHTTYPE DHT11
#define MQ135_PIN 32 // MQ-135 connected to GPIO32 (Moved from GPIO15 due to ADC2/WiFi conflict)
#define DUST_LED_PIN 25 // GP2Y1010AU0F LED pin connected to GPIO25
#define DUST_ANALOG_PIN 34 // GP2Y1010AU0F analog output connected to GPIO34

// --- WiFi and Server Configuration ---
const char* ssid = "ssid"; // Replace with your WiFi SSID
const char* password = "password"; // Replace with your WiFi Password
const char* serverUrl = "http://SERVER_IP:5000/data"; // Replace SERVER_IP with the IP address of the machine running Flask
// --- End Configuration ---

DHT dht(DHTPIN, DHTTYPE);

void setupWifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
    Serial.begin(9600);
    setupWifi(); // Connect to WiFi
    dht.begin();
    pinMode(DUST_LED_PIN, OUTPUT); // Set LED pin as output
}

void loop() {
    // Read temperature & humidity
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    // Read MQ-135 value
    int air_quality = analogRead(MQ135_PIN);

    // Read GP2Y1010AU0F dust value
    int dust_value = readDustSensor();

    // Create JSON document
    StaticJsonDocument<200> jsonDoc; // Adjust size as needed

    // Check sensor data validity and add to JSON
    if (!isnan(temperature) && !isnan(humidity)) {
        jsonDoc["temperature"] = temperature;
        jsonDoc["humidity"] = humidity;
    } else {
        Serial.println("Failed to read from DHT sensor!");
        // Optionally send null or skip sending data
        jsonDoc["temperature"] = nullptr;
        jsonDoc["humidity"] = nullptr;
    }

    jsonDoc["air_quality_raw"] = air_quality;
    jsonDoc["dust_raw"] = dust_value;

    // Serialize JSON to String
    String jsonString;
    serializeJson(jsonDoc, jsonString);

    // Print JSON to Serial for debugging
    Serial.println(jsonString);

    // Send data to server if WiFi is connected
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverUrl);
        http.addHeader("Content-Type", "application/json");

        int httpResponseCode = http.POST(jsonString);

        if (httpResponseCode > 0) {
            Serial.print("HTTP Response code: ");
            Serial.println(httpResponseCode);
            String payload = http.getString();
            Serial.println(payload);
        } else {
            Serial.print("Error code: ");
            Serial.println(httpResponseCode);
        }
        http.end();
    } else {
        Serial.println("WiFi Disconnected");
        // Optional: try to reconnect
        // setupWifi();
    }

    delay(30000); // Send data every 30 seconds
}

// Function to read GP2Y1010AU0F dust sensor
int readDustSensor() {
    digitalWrite(DUST_LED_PIN, LOW); // Turn IRED LED off
    delayMicroseconds(280); // Wait 0.28ms

    int rawValue = analogRead(DUST_ANALOG_PIN); // Read the output voltage
    
    // --- Add Debug Print ---
    Serial.print("Raw Dust ADC Value: ");
    Serial.println(rawValue); 
    // --- End Debug Print ---

    delayMicroseconds(40); // Wait 0.04ms
    digitalWrite(DUST_LED_PIN, HIGH); // Turn IRED LED on
    delayMicroseconds(9680); // Wait 9.68ms before the next cycle
    
    return rawValue;
}