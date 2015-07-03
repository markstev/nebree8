import struct

from arduinoio import serial_control

def main():
  interface = serial_control.SerialInterface()
  while True:
    message = interface.Read(no_checksums=True)
    if message:
      print "Message:"
      float_bytes = message.command
      #float_bytes.reverse()
      print struct.unpack('<f', struct.pack('4B', *float_bytes))[0]
      #print struct.unpack_from('<f', struct.pack('4b', *message.command))[0]

if __name__ == "__main__":
  main()
