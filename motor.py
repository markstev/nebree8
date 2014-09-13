#!/usr/bin/python

import RPi.GPIO as gpio
import argparse
import io_bank
import sys
import time

# dir_pin = 7
# pul_pin = 8
# en_pin = 25

#3.75 inches per revolution

# output_pins = (
#     dir_pin,
#     pul_pin,
#     en_pin)

# def Setup():
#   gpio.setmode(gpio.BCM)
#   gpio.setwarnings(False)
#   for pin in output_pins:
#     gpio.setup(pin, gpio.OUT)
# gpio.output(en_pin, 0)

def trusty_sleep(n):
  start = time.time()
  while (time.time() - start < n):
    #time.sleep(n - (time.time() - start))
    pass

class StepperMotor(object):
  def __init__(self, dry_run=False, io=None):
    self.pulse_state = False
    self.dry_run = dry_run
    if not io:
      io = io_bank.IOBank()
    self.io = io
    self.colliding_positive = False
    self.colliding_negative = False
    def HitPositiveRail(channel):
      self.colliding_positive = True
      print "Hit positive rail"
    def HitNegativeRail(channel):
      self.colliding_negative = True
      print "Hit negative rail"
    self.io.AddCallback(io_bank.Inputs.LIMIT_SWITCH_POS, gpio.FALLING,
        HitPositiveRail)
    self.io.AddCallback(io_bank.Inputs.LIMIT_SWITCH_NEG, gpio.FALLING,
        HitNegativeRail)


  def Move(self, steps, forward=1, ramp_seconds=0):
    if self.dry_run:
      print "DRY RUN: Moving %d steps in direction: %d" % (steps, forward)
    self.io.WriteOutput(io_bank.Outputs.STEPPER_PULSE, 0)
    self.io.WriteOutput(io_bank.Outputs.STEPPER_DIR, forward)
    #gpio.output(pul_pin, 0)
    #gpio.output(dir_pin, forward)
    for i in range(steps):
      if (not ((self.colliding_positive and forward)
               or (self.colliding_negative and not forward))):
        #print self.pulse_state
        self.io.WriteOutput(io_bank.Outputs.STEPPER_PULSE, int(self.pulse_state))
        #gpio.output(pul_pin, int(self.pulse_state))
        #time.sleep(0.001)  # one millisecond
        trusty_sleep(0.001)
        self.pulse_state = not self.pulse_state
      if forward:
        self.colliding_negative = False
      else:
        self.colliding_positive = False
    self.io.WriteOutput(io_bank.Outputs.STEPPER_PULSE, 0)

def InchesToSteps(inches):
  return int(inches / 3.75 * 800)

class RobotRail(object):
  def __init__(self, motor):
    self.motor = motor
    self.position = 0

  def FillPositions(self, absolute_positions):
    for position in absolute_positions:
      forward = position > self.position
      steps = InchesToSteps(abs(position - self.position))
      print steps
      self.motor.Move(steps, forward=forward)
      self.position = position
      print "At position: %f" % position
      time.sleep(2.0)

  def CalibrateToZero(self):
    steps = InchesToSteps(200)
    self.motor.Move(steps, forward=True)
    self.position = 0

  
def main(args):
  parser = argparse.ArgumentParser(description='Move robot stepper motor.')
  parser.add_argument('--steps', type=int, nargs="?", default=1,
                      help='Steps to move the motor')
  parser.add_argument('--inches', type=float, nargs="?", default=0,
                      help='Inches to move the motor')
  parser.add_argument('--backward', type=str, nargs="?", default="False",
                      help='Direction to move')
  parser.add_argument('--dry_run', type=bool, nargs="?", default=False,
                      help='Whether to move motors')
  parser.add_argument('--positions', type=float, nargs="+", default=(),
                      help='List of positions to move the truck through')
  parser.add_argument('--absolute', type=bool, nargs="?", default=False,
                      help='Whether calibrate position')
  args = parser.parse_args()
  print args
  # For the NEMA 14 12v 350mA (#324) stepper motors from AdaFruit:
  # http://www.adafruit.com/products/324
  # Driving it with 12v using a delay of 1 microsecond.
  #Setup()
  motor = StepperMotor(args.dry_run)
  rail = RobotRail(motor)
  if args.positions:
    if args.absolute:
      rail.CalibrateToZero()
    rail.FillPositions(args.positions)
    gpio.cleanup()
    return
  forward = (args.backward != "False")
  if args.inches:
    steps = InchesToSteps(args.inches)
  else:
    steps = args.steps
  if forward:
    print "Forward %d steps" % steps
  else:
    print "Backward %d steps" % steps
  motor.Move(steps, forward=forward)
  gpio.cleanup()

if __name__ == "__main__":
  main(sys.argv)
