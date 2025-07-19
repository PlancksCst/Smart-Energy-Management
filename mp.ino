#include <Wire.h>
#include <Adafruit_INA219.h>

Adafruit_INA219 ina1(0x40);
Adafruit_INA219 ina2(0x41);
Adafruit_INA219 ina3(0x42);
Adafruit_INA219 ina4(0x43);

const int relays[] = {7, 6, 5, 4};
const int relayCount = 4;
const unsigned long delayTime = 2000;

void setup() {
  Serial.begin(9600);
  Wire.begin();

   ina1.begin();
  ina2.begin();
  ina3.begin();
  ina4.begin();
  for (int i = 0; i < relayCount; i++) {
    pinMode(relays[i], OUTPUT);
    digitalWrite(relays[i], HIGH);  // relay OFF (active LOW)
  }
}

void loop() {
  Adafruit_INA219* sensors[] = {&ina1, &ina2, &ina3, &ina4};

  for (int i = 0; i < relayCount; i++) {
    digitalWrite(relays[i], LOW); // Turn ON relay
    delay(1000); // Allow values to stabilize

    float busVoltage = sensors[i]->getBusVoltage_V();
    float shuntVoltage = sensors[i]->getShuntVoltage_mV();
    float current = sensors[i]->getCurrent_mA();
    float power = sensors[i]->getPower_mW();
    float loadVoltage = busVoltage + (shuntVoltage / 1000.0);

    // Send compact data for Python
    Serial.print("ID="); Serial.print(i + 1);
    Serial.print(",V="); Serial.print(loadVoltage, 2);
    Serial.print(",I="); Serial.print(current, 2);
    Serial.print(",P="); Serial.print(power, 2);
    Serial.println();

    digitalWrite(relays[i], HIGH); // Turn OFF relay
    delay(delayTime);

  }


  f (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    if (command.startsWith("OFF")) {
      int cid = command.substring(3).toInt();  // Get circuit ID
      if (cid >= 1 && cid <= 4) {
        digitalWrite(relays[cid - 1], HIGH);  // Turn off
        Serial.print("Circuit ");
        Serial.print(cid);
        Serial.println(" turned OFF by Python");
      }
    }
  }

}
