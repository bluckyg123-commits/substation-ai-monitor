// ESP32: read sensors -> POST to PC server -> AI replies -> drive relay + LCD
// Libraries: WiFi, HTTPClient (built in), LiquidCrystal_I2C
#include <WiFi.h>
#include <HTTPClient.h>
#include <LiquidCrystal_I2C.h>

const char* SSID = "YOUR_WIFI";
const char* PASS = "YOUR_PASSWORD";
const char* URL  = "http://192.168.1.50:5000/data";   // PC IP running server.py

// ---- pins (CHANGE to your wiring). All ADC pins are 3.3 V max! ----
#define PIN_VIN   34   // ZMPT101B / divider on mains side
#define PIN_VOUT  35   // divider on 12 V secondary
#define PIN_CURR  32   // ACS712 (5V module -> use divider to 3.3 V)
#define PIN_TEMP  33   // LM35 / NTC
#define PIN_RELAY 26   // relay module IN (many are active LOW)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// --- calibration: tune these against a multimeter ---
float readVin()  { return analogRead(PIN_VIN)  * (3.3/4095.0) * 100.0; }  // TODO calibrate
float readVout() { return analogRead(PIN_VOUT) * (3.3/4095.0) * 5.0;  }  // TODO
float readCurr() { return fabs(analogRead(PIN_CURR)*(3.3/4095.0) - 1.65) / 0.185; } // TODO
float readTemp() { return analogRead(PIN_TEMP) * (3.3/4095.0) * 100.0; } // LM35 10mV/C

void setup() {
  pinMode(PIN_RELAY, OUTPUT); digitalWrite(PIN_RELAY, LOW);  // load ON (adjust polarity)
  lcd.init(); lcd.backlight();
  WiFi.begin(SSID, PASS);
  while (WiFi.status() != WL_CONNECTED) delay(300);
}

void loop() {
  float vi = readVin(), vo = readVout(), a = readCurr(), t = readTemp();
  String body = "{\"input_voltage\":" + String(vi) + ",\"output_voltage\":" + String(vo) +
                ",\"load_current\":" + String(a) + ",\"temperature\":" + String(t) + "}";
  String label = "NO LINK"; bool trip = false;
  HTTPClient http; http.begin(URL); http.addHeader("Content-Type", "application/json");
  if (http.POST(body) == 200) {
    String r = http.getString();
    trip = r.indexOf("\"trip\":true") >= 0;
    int s = r.indexOf("\"label\":\"") + 9; label = r.substring(s, r.indexOf("\"", s));
  }
  http.end();
  digitalWrite(PIN_RELAY, trip ? HIGH : LOW);               // trip = disconnect load
  lcd.clear(); lcd.setCursor(0,0); lcd.print("V:" + String(vi,0) + " I:" + String(a,2));
  lcd.setCursor(0,1); lcd.print(label.substring(0,16));
  delay(1000);
}
