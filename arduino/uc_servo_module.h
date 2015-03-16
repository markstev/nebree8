#ifndef NEBREE8_ARDUINO_UC_SERVO_MODULE_H_
#define NEBREE8_ARDUINO_UC_SERVO_MODULE_H_

#include <string.h>

#include <Servo.h>

#include "../arduinoio/lib/message.h"
#include "../arduinoio/lib/timed_callback.h"
#include "../arduinoio/lib/uc_module.h"

namespace nebree8 {

const char* SET_SERVO = "SERVO";
const int SET_SERVO_LENGTH = 5;
const int MAX_NUM_SERVOS = 8;

class ServoCommand;
typedef arduinoio::TimedCallback<ServoCommand> Callback;

class ServoCommand {
 public:
  int start_degrees_;
  int end_degrees_;
  unsigned long start_time_millis_;
  unsigned char total_seconds_;
  Servo* servo;
  Callback* callback_;

  // Update every 20msec (though it shouldn't really matter).
  void Rotate() {
    unsigned long millis_so_far = millis() - start_time_millis_;
    float time_so_far = millis_so_far / 1000.0 / total_seconds_;
    if (time_so_far > 1.0) {
      time_so_far = 1.0;
      callback_ = NULL;
    } else {
      callback_ = new Callback(5, this, &ServoCommand::Rotate);
    }
    int degrees_now = start_degrees_ + (end_degrees_ - start_degrees_) * time_so_far;
    //servo->writeMicroseconds(degrees_now);
    servo->write(degrees_now);
    digitalWrite(13, HIGH);
  }
};

class UCServoModule : public arduinoio::UCModule {
 public:
  UCServoModule() : servos_used_(0) {
    for (int i = 0; i < MAX_NUM_SERVOS; ++i) {
      servo_pins_[i] = -1;
    }
  }

  virtual const arduinoio::Message* Tick() {
    for (int i = 0; i < servos_used_; i++) {
      if (commands_[i].callback_ != NULL) {
        commands_[i].callback_->Update();
      }
    }
    return NULL;
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (strncmp(command, SET_SERVO, SET_SERVO_LENGTH) == 0) {
      int i = SET_SERVO_LENGTH;
      unsigned char pin = command[i];
      unsigned char start_degrees = command[i + 1];
      unsigned char degrees = command[i + 2];
      unsigned char seconds = command[i + 3];
      for (int servo_pin = 0; servo_pin < servos_used_; ++servo_pin) {
        if (servo_pins_[servo_pin] == pin) {
          MoveServo(servo_pin, start_degrees, degrees, seconds);
          return true;
        }
      }
      servo_pins_[servos_used_] = pin;
      commands_[servos_used_].servo = new Servo();
      commands_[servos_used_].servo->attach(pin);
      MoveServo(servos_used_, start_degrees, degrees, seconds);
      servos_used_++;
      return true;
    }
  }

  int DegreesToMicroseconds(unsigned char degrees) {
    //return (((int) degrees) * 2000) / 180.0 + 1000;
    return degrees;
  }

  void MoveServo(unsigned char servo_pin_index, unsigned char start_degrees, unsigned char degrees, unsigned char seconds) {
    commands_[servo_pin_index].start_degrees_ = DegreesToMicroseconds(start_degrees);
    commands_[servo_pin_index].end_degrees_ = DegreesToMicroseconds(degrees);
    commands_[servo_pin_index].start_time_millis_ = millis();
    commands_[servo_pin_index].total_seconds_ = seconds;
    commands_[servo_pin_index].callback_ =
        new Callback(0, &commands_[servo_pin_index], &ServoCommand::Rotate);
  }

 private:
  unsigned char servo_pins_[MAX_NUM_SERVOS];
  int servos_used_;
  ServoCommand commands_[MAX_NUM_SERVOS];
};

}  // namespace nebree8
#endif  // NEBREE8_ARDUINO_UC_SERVO_MODULE_H_
