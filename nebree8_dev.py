#!/usr/bin/python
"""Top-level program to call all the various components

Components:
  1) user-input drink request
  2) drink db lookup -> ingredients
  3) stock drinks match; translate to positions
  4) robot driver to fill from positions
"""

import argparse
import io_bank
import sys
import time
from motor import StepperMotor, RobotRail
from parts.load_cell import LoadCellMonitor
import RPi.GPIO as gpio

def main(args):
  parser = argparse.ArgumentParser(description='Drink to mix')
  parser.add_argument('--drink', type=str, nargs="?", default="margarita",
                      help='Name of a drink')
  parser.add_argument('--set_io', type=int, nargs="?", default=0,
                      help='IO pin to set')
  parser.add_argument('--set_valve', type=int, nargs="?", default=0,
                      help='IO pin to set')
  parser.add_argument('--set_io_value', type=int, nargs="?", default=0,
                      help='Value to set on the pin.')
  parser.add_argument('--wait_for_falling_io', type=int, nargs="?", default=0,
                      help='IO pin to wait for a falling edge on')
  parser.add_argument('--valve_motor1_direction', type=int, nargs="?", default=0,
                      help='Direction to move valve motor1')
  parser.add_argument('--positions', type=float, nargs="+", default=(),
                      help='List of positions to move the truck through')
  args = parser.parse_args()

  if args.set_io or args.set_valve:
    io = io_bank.IOBank()
    if args.set_io:
      io.WriteOutput(io_bank.Outputs(args.set_io), args.set_io_value)
    else:
      valve_io = io_bank.GetValve(args.set_valve)
      io.WriteOutput(valve_io, args.set_io_value)
  if args.valve_motor1_direction:
    io = io_bank.IOBank()
    io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1)
    if args.valve_motor1_direction > 0:
      io.WriteOutput(io_bank.Outputs(io_bank.Outputs.MOTOR_UP_B), 0)
      io.WriteOutput(io_bank.Outputs(io_bank.Outputs.MOTOR_DOWN_B1), 0)
      io.WriteOutput(io_bank.Outputs(io_bank.Outputs.MOTOR_UP_A), 1)
      io.WriteOutput(io_bank.Outputs(io_bank.Outputs.MOTOR_DOWN_A1), 1)
    else:
      io.WriteOutput(io_bank.Outputs(io_bank.Outputs.MOTOR_UP_A), 0)
      io.WriteOutput(io_bank.Outputs(io_bank.Outputs.MOTOR_DOWN_A1), 0)
      io.WriteOutput(io_bank.Outputs(io_bank.Outputs.MOTOR_UP_B), 1)
      io.WriteOutput(io_bank.Outputs(io_bank.Outputs.MOTOR_DOWN_B1), 1)
      print "not ready yet"
  if args.positions:
    load_cell = LoadCellMonitor()
    io = io_bank.IOBank()
    motor = StepperMotor(io=io)
    rail = RobotRail(motor)
    rail.FillPositions(args.positions)
    gpio.cleanup()
  if args.wait_for_falling_io:
    io = io_bank.IOBank()
    def PrintCallback(channel):
      print("triggered! on " + str(channel))
    io.AddCallback(io_bank.Inputs(args.wait_for_falling_io), gpio.FALLING,
                   PrintCallback)
    while True:
      time.sleep(60)
  time.sleep(2)

if __name__ == "__main__":
  main(sys.argv)
