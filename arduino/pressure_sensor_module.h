#ifndef NEBREE8_ARDUINO_PRESSURE_SENSOR_MODULE_H_
#define NEBREE8_ARDUINO_PRESSURE_SENSOR_MODULE_H_

#include <string.h>

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/message.h"
#include "../arduinoio/lib/timed_callback.h"
#include "MS5803/SparkFun_MS5803_I2C.h"

namespace nebree8 {

const size_t kPressureSize = 4; // 4 bytes per float.

class PressureSensorModule : public arduinoio::UCModule {
 public:
  PressureSensorModule() {
    sensor_ = new MS5803(ADDRESS_HIGH);  // Default address is 0x76, based on jumpers soldered.
    sensor_->reset();
    sensor_->begin();
    timed_callback_ = NULL;
  }

  virtual const arduinoio::Message* Tick() {
    if (timed_callback_ == NULL) {
      int kOutgoingAddress = 99;
      message_.Reset(kOutgoingAddress, kPressureSize, pressure_);
      timed_callback_ = new arduinoio::TimedCallback<PressureSensorModule>(1000, this,
          &PressureSensorModule::ReadPressure);
      return &message_;
    }
    timed_callback_->Update();
    return NULL;
  }

  void ReadPressure() {
    float *pressure_float = (float*) pressure_;
    pressure_float[0] = sensor_->getPressure(ADC_4096);  // high-level precision
    timed_callback_ = NULL;
  }

  // TODO: Respond to messages asking to maintain a given pressure setting using a particular pin (or, maybe raise a message to UCIOModule to set the pin).
  virtual bool AcceptMessage(const arduinoio::Message &message) {
    return false;
  }

 private:
  MS5803* sensor_;
  arduinoio::Message message_;
  arduinoio::TimedCallback<PressureSensorModule> *timed_callback_;
  unsigned char pressure_[kPressureSize];
};

}  // namespace nebree8
#endif  // NEBREE8_ARDUINO_PRESSURE_SENSOR_MODULE_H_
