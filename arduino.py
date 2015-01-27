from arduinoio import serial_control
import time


class Arduino:
  def __init__(self):
    pass


def main():
  message = serial_control.Message()
  interface = serial_control.SerialInterface()
  while True:
    for setting in [0x01, 0x00]:
      raw_message = [chr(x) for x in [0x07, setting]]
      print raw_message
      command = "SET_IO" + "".join(raw_message)
      interface.Write(0, command)
      time.sleep(1.0)


if __name__ == "__main__":
  main()
