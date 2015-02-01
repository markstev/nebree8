#if defined(ARDUINO) && ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif 
#include <SoftwareSerial.h>

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/serial_module.h"
#include "../arduinoio/lib/arduinoio.h"
#include "uc_io_module.h"

const int SERIAL_RX_PIN = 0;
const int SERIAL_TX_PIN = 1;

//SoftwareSerial *serial;

arduinoio::ArduinoIO arduino_io;
void setup() {
//serial = new SoftwareSerial(SERIAL_RX_PIN, SERIAL_TX_PIN);
//serial->begin(9600);
  Serial.begin(9600);
  arduino_io.Add(new arduinoio::SerialRXModule(NULL, 0));
  arduino_io.Add(new nebree8::UCIOModule());
//pinMode(7, OUTPUT);
//digitalWrite(7, HIGH);
//pinMode(6, OUTPUT);
//digitalWrite(6, LOW);
}

void loop() {
  arduino_io.HandleLoopMessages();
}
