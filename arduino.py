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
    self.signal_refresh.put((pin, value), True, None)

  def __RefreshOutputs(self):
    while True:
      raw_message = []
      try:
        pin, value = self.signal_refresh.get(True, 1. / _REFRESH_RATE)
        self.outputs[pin] = value
        raw_message = [chr(pin), chr(value)]
      except Queue.Empty:
        # No refresh signals for a while, Refresh all pins
        for pin, value in self.outputs.iteritems():
          raw_message.append(chr(pin))
          raw_message.append(chr(value))
      command = "SET_IO" + "".join(raw_message)
      self.interface.Write(0, command)


def main():
  arduino = Arduino()
  while True:
    arduino.WriteOutput(2, 1)
    time.sleep(1.0)
    # for pin in [13, 12, 11, 10, 9, 2]:
    #   for setting in [1, 0]:
    #     arduino.WriteOutput(pin, setting)
    #     time.sleep(1.0)


if __name__ == "__main__":
  main()
