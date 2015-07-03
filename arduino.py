import threading
import time
import Queue

from arduinoio import serial_control

_REFRESH_RATE = 1  # Refreshes per second

class Arduino:
  def __init__(self):
    self.interface = serial_control.SerialInterface()
    self.outputs = {}
    self.signal_refresh = Queue.Queue(1)
    self.thread = threading.Thread(target=self.__RefreshOutputs)
    self.thread.daemon = True
    self.thread.start()

  def WriteOutput(self, pin, value):
    self.outputs[pin] = value
    self.signal_refresh.put((pin, value), True, None)  # Values don't matter.

  def WriteServo(self, pin, start_degrees, end_degrees, seconds):
    raw_message = [chr(pin), chr(start_degrees), chr(end_degrees), chr(seconds)]
    command = "SERVO" + "".join(raw_message)
    self.interface.Write(0, command)
    print "set servo"

  def __SendOutputsMessage(self):
    raw_message = []
    for pin, value in self.outputs.iteritems():
      raw_message.append(chr(pin))
      raw_message.append(chr(value))
    command = "SET_IO" + "".join(raw_message)
    self.interface.Write(0, command)

  def __RefreshOutputs(self):
    while True:
      try:
        unused_pin, unused_value = self.signal_refresh.get(True, 1. / _REFRESH_RATE)
        self.__SendOutputsMessage()
      except Queue.Empty:
        # No refresh signals for a while, Refresh all pins
        self.__SendOutputsMessage()


def main():
  arduino = Arduino()
  #hile True:
  # #arduino.WriteOutput(2, 1)
  # #time.sleep(1.0)
  # # for pin in [13, 12, 11, 10, 9, 2]:
  # #   for setting in [1, 0]:
  # #     arduino.WriteOutput(pin, setting)
  # #     time.sleep(1.0)
  # arduino.WriteServo(21, 90, 180, 5)
  # time.sleep(5)
  # print "should be done"
  # time.sleep(2)
  # arduino.WriteServo(21, 180, 90, 5)
  # time.sleep(5)
  # print "should be done"

  end = 160
  middle = 100
  ts = 3
  arduino.WriteServo(22, end, middle, ts)
  arduino.WriteServo(21, 180, 90, ts)
  time.sleep(10)
  print "should be done"
  time.sleep(2)
  arduino.WriteServo(22, 90, 180, ts)
  arduino.WriteServo(21, 90, 180, ts)
  time.sleep(10)
  print "should be done"


if __name__ == "__main__":
  main()
