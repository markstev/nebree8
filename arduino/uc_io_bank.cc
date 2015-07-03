#if defined(ARDUINO) && ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif 
#include <SoftwareSerial.h>
#include <Wire.h>  // Needed by cmake to generate the pressure sensor deps. (Gross!)

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/serial_module.h"
#include "../arduinoio/lib/arduinoio.h"
#include "MS5803/SparkFun_MS5803_I2C.h"
#include "pressure_sensor_module.h"
#include "uc_io_module.h"
//#include "uc_servo_module.h"

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
  //arduino_io.Add(new nebree8::UCServoModule());
  arduino_io.Add(new nebree8::PressureSensorModule());
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
//pinMode(6, OUTPUT);
//digitalWrite(6, LOW);
}

void loop() {
  arduino_io.HandleLoopMessages();
}
