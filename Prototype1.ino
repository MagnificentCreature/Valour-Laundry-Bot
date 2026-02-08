#include <secrets.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <NetworkClientSecure.h>

// Mapping for XIAO ESP32-S3 on Grove Shield D0
const int VIBRATION_PIN = 1;
const int mqtt_port = 8883;
int measurement = 0;         // variable for reading the pushbutton status

// Initialize the WiFi and MQTT client objects
NetworkClientSecure espClient;
PubSubClient client(espClient);

void debugInit() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect. Needed for native USB
  }
  Serial.println("Debug Initialized...");
}

void pinSetup() {
  pinMode(VIBRATION_PIN, INPUT);
}

void WiFiSetup() {  // Connect to WiFi network
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void MQTTConnect() {
  Serial.println("Connecting to MQTT");

  espClient.setInsecure();
  // Set the MQTT broker server IP address and port
  client.setServer(mqtt_server, mqtt_port);

  // Connect to MQTT broker
  while (!client.connected()) {
    if (client.connect("ESP32_Laundry_Room", mqtt_user, mqtt_pass)) {
      Serial.println("Connected to MQTT broker");
    } else {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.println("retrying in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  debugInit(); //blocking until debug is ready
  pinSetup();
  WiFiSetup();
  MQTTConnect();
}

void loop() {
  if (!client.connected()) {
    MQTTConnect();
  }
  client.loop(); // This processes background pings and keeps the link alive

  long measurement = digitalRead(VIBRATION_PIN);
  if (measurement == LOW) {
    // Note if need be, can publish F for finished

    // bool success = client.publish("laundry/washer/6", "90");
    bool success = client.publish("laundry/dryer/7", "90");

    if (success) {
      Serial.println("Vibration Detected & Published!");
    } else {
      Serial.println("Publish failed. Check connection.");
    }

    //debounce delay
    delay(3000);
  }
}