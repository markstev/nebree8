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

const int pin = 13;
const int inside_output_pin = 7;
const int outside_output_pin = 6;
const int IR_RX_PIN = 2;
const int IR_TX_PIN= 3;
const int SERIAL_RX_PIN = 0;
const int SERIAL_TX_PIN = 1;
const int MOTOR_DIR_PIN = 10;
const int MOTOR_ON_PIN = 8;
const int SONAR_TRIGGER_PIN = 11;
const int SONAR_ECHO_PIN = 12;
const int OPEN_STOP_PIN = 4;
const int CLOSE_STOP_PIN = 5;

const int INSIDE_LIGHTS_ADDRESS = 1;

SoftwareSerial *serial;

arduinoio::ArduinoIO arduino_io;
void setup() {                
  serial = new SoftwareSerial(SERIAL_RX_PIN, SERIAL_TX_PIN);
  serial->begin(9600);
  arduino_io.Add(new arduinoio::SerialRXModule(serial, 0));
  arduino_io.Add(new nebree8::UCIOModule());
}

void loop() {
  arduino_io.HandleLoopMessages();
}
