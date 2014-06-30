#!/usr/bin/python

import RPi.GPIO as gpio
import argparse
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
  def __init__(self):
    self.pulse_state = False

  def Move(self, steps, forward=1):
    gpio.output(pul_pin, 0)
    gpio.output(dir_pin, forward)
    for i in range(steps):
      gpio.output(pul_pin, int(self.pulse_state))
      time.sleep(0.001)  # one millisecond
      self.pulse_state = not self.pulse_state

  
def main(args):
  print args
  parser = argparse.ArgumentParser(description='Process some integers.')
  parser.add_argument('--steps', type=int, nargs="?", default=1,
                      help='Steps to move the motor')
  parser.add_argument('--inches', type=float, nargs="?", default=0,
                      help='Inches to move the motor')
  parser.add_argument('--backward', type=bool, nargs="?", default=False,
                      help='Direction to move')
  parser.add_argument('--dry_run', type=bool, nargs="?", default=False,
                      help='Whether to move motors')
  args = parser.parse_args()
  # For the NEMA 14 12v 350mA (#324) stepper motors from AdaFruit:
  # http://www.adafruit.com/products/324
  # Driving it with 12v using a delay of 1 microsecond.
  Setup()
  #revolutions = 3
  motor = StepperMotor()
  #steps = revolutions * 200 * 16
  forward = not args.backward
  if args.inches:
    steps = int(args.inches / 3.75 * 800)
  else:
    steps = args.steps
  if forward:
    print "Forward %d steps" % steps
  else:
    print "Backward %d steps" % steps
  if not args.dry_run:
    print "Running motor"
    motor.Move(steps, forward=forward)
  gpio.cleanup()

if __name__ == "__main__":
  main(sys.argv)
