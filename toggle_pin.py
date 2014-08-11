#!/usr/bin/python

import RPi.GPIO as gpio
import argparse
import io_bank
import sys
import time

dir_pin = 17
pul_pin = 27
en_pin = 22

#3.75 inches per revolution

output_pins = (
    dir_pin,
    pul_pin,
    en_pin)

def Setup():
  gpio.setmode(gpio.BCM)
  gpio.setwarnings(False)
  for pin in output_pins:
    gpio.setup(pin, gpio.OUT)
  gpio.output(en_pin, 0)

class StepperMotor(object):
  def __init__(self, dry_run=False):
    self.pulse_state = False
    self.dry_run = dry_run
    self.io = io_bank.IOBank()
    self.colliding_positive = False
    def HitPositiveRail(channel):
      self.colliding_positive = True
    self.io.AddCallback(io_bank.Inputs.LIMIT_SWITCH, gpio.FALLING,
        HitPositiveRail)
    #lambda x: self.HitPositiveRail)


  def Move(self, steps, forward=1):
    if self.dry_run:
      print "DRY RUN: Moving %d steps in direction: %d" % (steps, forward)
    gpio.output(pul_pin, 0)
    gpio.output(dir_pin, forward)
    for i in range(steps):
      if not (self.colliding_positive and forward):
        gpio.output(pul_pin, int(self.pulse_state))
        time.sleep(0.001)  # one millisecond
        self.pulse_state = not self.pulse_state
      if not forward:
        self.colliding_positive = False
    gpio.output(pul_pin, 0)

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
      self.motor.Move(steps, forward=forward)
      self.position = position
      print "At position: %f" % position
      time.sleep(2.0)

  
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
  args = parser.parse_args()
  print args
  # For the NEMA 14 12v 350mA (#324) stepper motors from AdaFruit:
  # http://www.adafruit.com/products/324
  # Driving it with 12v using a delay of 1 microsecond.
  Setup()
  motor = StepperMotor(args.dry_run)
  rail = RobotRail(motor)
  if args.positions:
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
