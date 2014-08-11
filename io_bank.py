"""Provides a layer of abstraction for setting output pins.

This lets the rest of the system assign a function to a pin, update that
function, etc. Handles details like some outputs being on shift registers,
etc."""

import enum
import time
import RPi.GPIO as gpio

DEBUG = True
def DebugPrint(*args):
  if DEBUG == True:
    print args
    #time.sleep(0.01)

class Outputs(enum.Enum):
  STEPPER_DIR = 22
  STEPPER_PULSE = 27
  STEPPER_ENABLE = 17

  #SHIFT_REG_ENABLE = 8  # mid
  SHIFT_REG_CLOCK = 7  # bottom -> green -> clock
  SHIFT_REG_RCLOCK = 8  # mid
  SHIFT_REG_SERIAL = 25  # top

  #UNUSED = 3 # green; 2 is above it and yellow
  VALVE_0 = 1006
  VALVE_1 = 1001
  VALVE_2 = 1002
  VALVE_3 = 1003
  VALVE_4 = 1004
  VALVE_5 = 1005
  VALVE_6 = 1000
  VALVE_7 = 1007

  COMPRESSOR = 2

class Inputs(enum.Enum):
  LIMIT_SWITCH_POS = 3
  LIMIT_SWITCH_NEG = 4
  
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
    self.shift_reg = [0, 0]
    #self.WriteOutput(Outputs.SHIFT_REG_ENABLE, 0)
    self.Shift(0xff)
    self.Shift(0)

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

      byte = value
      DebugPrint("output value is ", byte)
      for unused_i in range(shift_register_index):
        byte = byte << 1
      DebugPrint("shifted value is ", byte)
      self.Shift(byte)

      # self.shift_reg[shift_register_index] = value

      # shift_reg_backwards = self.shift_reg
      # shift_reg_backwards.reverse()
      # for bit in shift_reg_backwards:
      #   self.WriteOutput(Outputs.SHIFT_REG_SERIAL, bit)
      #   time.sleep(_SHIFT_REG_SLEEP_TIME)
      #   self.WriteOutput(Outputs.SHIFT_REG_CLOCK, 0)
      #   time.sleep(_SHIFT_REG_SLEEP_TIME)
      #   self.WriteOutput(Outputs.SHIFT_REG_CLOCK, 1)
      #   time.sleep(_SHIFT_REG_SLEEP_TIME)
      #   self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, 0)
      #   time.sleep(_SHIFT_REG_SLEEP_TIME)
      #   self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, 1)
      #   time.sleep(_SHIFT_REG_SLEEP_TIME)

  def Shift(self, byte): 
    SLEEP_TIME = 0.000
    DebugPrint("Writing byte ", byte, " into shift register.")
    for bitnum in range(8):
      foodbit = bool((byte & 0x0080) >> 7)
      DebugPrint("food piece ", 7 - bitnum, " into mouth with this piece of food ", foodbit, " and chew")
      self.WriteOutput(Outputs.SHIFT_REG_SERIAL, foodbit)
      time.sleep(SLEEP_TIME)
      #GPIO.output(gpiomap[mouth],foodbit)
      self.WriteOutput(Outputs.SHIFT_REG_CLOCK, gpio.LOW)
      time.sleep(SLEEP_TIME)
      #GPIO.output(gpiomap[chew], GPIO.LOW)
      self.WriteOutput(Outputs.SHIFT_REG_CLOCK, gpio.HIGH)
      time.sleep(SLEEP_TIME)
      #GPIO.output(gpiomap[chew], GPIO.HIGH)
      byte = byte << 1
    self.WriteOutput(Outputs.SHIFT_REG_CLOCK, gpio.LOW)  # Reset to a safe state.
    DebugPrint("and swallow")
    self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.LOW)
    #GPIO.output(gpiomap[swallow], GPIO.LOW)
    self.WriteOutput(Outputs.SHIFT_REG_RCLOCK, gpio.HIGH)
    #GPIO.output(gpiomap[swallow], GPIO.HIGH)
