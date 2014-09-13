"""Provides a layer of abstraction for setting output pins.

This lets the rest of the system assign a function to a pin, update that
function, etc. Handles details like some outputs being on shift registers,
etc."""

import enum
import threading
import time
import Queue
import RPi.GPIO as gpio

DEBUG = True
def DebugPrint(*args):
  if DEBUG == True:
    print args
    #time.sleep(0.01)

class Outputs(enum.Enum):
  STEPPER_DIR = 7
  STEPPER_PULSE = 8
  STEPPER_ENABLE = 25

  # SHIFT_REG_CLOCK = 8
  # SHIFT_REG_RCLOCK = 25
  # SHIFT_REG_SERIAL = 7
  SHIFT_REG_CLOCK = 9
  SHIFT_REG_RCLOCK = 11
  SHIFT_REG_SERIAL = 10

  MOTOR_UP_A = 27
  MOTOR_UP_B = 22

  X_6 = 1000
  COMPRESSOR = 1001
  X_2 = 1002
  X_3 = 1003
  X_4 = 1004
  MOTOR_DOWN_A1 = 1005
  MOTOR_DOWN_B1 = 1006
  X_7 = 1007

class Inputs(enum.Enum):
  LIMIT_SWITCH_POS = 23
  LIMIT_SWITCH_NEG = 24
  
_SHIFT_REG_REFRESH_RATE = 1
_SHIFT_REG_SLEEP_TIME = 0.1 # 1 ms -> 1khz
_SHIFT_REG_ADDRESS_OFFSET = 1000

class IOBank(object):
  def __init__(self):
    gpio.setmode(gpio.BCM)
    gpio.setwarnings(False)
    for output in Outputs:
      if output.value < _SHIFT_REG_ADDRESS_OFFSET:
        gpio.setup(output.value, gpio.OUT)
    for pin in Inputs:
      gpio.setup(pin.value, gpio.IN, pull_up_down=gpio.PUD_UP)
    self.current_shifted_byte = [0] * 8
    self.signal_refresh = Queue.Queue(1)
    self.thread = threading.Thread(target=self.__RefreshShiftOutputs)
    self.thread.daemon = True
    self.thread.start()
    #self.WriteOutput(Outputs.COMPRESSOR, 0)

  def ReadInput(self, input_enum):
    return gpio.input(input_enum.value)

  # rising_or_falling should be gpio.RISING or gpio.FALLING
  def AddCallback(self, input_enum, rising_or_falling, callback):
    gpio.add_event_detect(input_enum.value, rising_or_falling, callback=callback)

  def WriteOutput(self, output_enum, value):
    if output_enum.value < _SHIFT_REG_ADDRESS_OFFSET:
      gpio.output(output_enum.value, value)
    else:
      # Shift register output.
      # Steps to write:
      # 1: update current shift reg bytes overall
      # 2: set bit, then toggle clock
      shift_register_index = output_enum.value - _SHIFT_REG_ADDRESS_OFFSET
      self.current_shifted_byte[shift_register_index] = value
      self.__SignalRefresh()


  def __Shift(self, byte):
    SLEEP_TIME = 0.0001
    byte = list(byte)
    byte.reverse()
    self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.LOW)
    for bitnum, bit in enumerate(byte):
      foodbit = bit
      self.WriteOutput(Outputs.SHIFT_REG_CLOCK, gpio.LOW)
      time.sleep(SLEEP_TIME)
      self.WriteOutput(Outputs.SHIFT_REG_SERIAL, foodbit)
      time.sleep(SLEEP_TIME)
      self.WriteOutput(Outputs.SHIFT_REG_CLOCK, gpio.HIGH)
      time.sleep(SLEEP_TIME)
    self.WriteOutput(Outputs.SHIFT_REG_CLOCK, gpio.LOW)  # Reset to a safe state.
    self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.LOW)
    #GPIO.output(gpiomap[swallow], GPIO.LOW)
    self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.HIGH)
    self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.LOW)
    #GPIO.output(gpiomap[swallow], GPIO.HIGH)

  def __RefreshShiftOutputs(self):
    while True:
      # TODO: Do we need to shift multiple times?
      self.__Shift(self.current_shifted_byte)
      try:
        self.signal_refresh.get(True, 1. / _SHIFT_REG_REFRESH_RATE)
      except:  #Queue.Empty:
        pass # No refresh signals for a while, refresh anyway.

  def __SignalRefresh(self):
    try:
      self.signal_refresh.put(None, False)
    except Queue.Full:
      pass  # Refresh already scheduled.
