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

def main(args):
  parser = argparse.ArgumentParser(description='Drink to mix')
  parser.add_argument('--drink', type=str, nargs="?", default="margarita",
                      help='Name of a drink')
  parser.add_argument('--set_io', type=int, nargs="?", default=0,
                      help='IO pin to set')
  parser.add_argument('--set_io_value', type=int, nargs="?", default=0,
                      help='Value to set on the pin.')
  args = parser.parse_args()

  if args.set_io:
    io = io_bank.IOBank()
    io.WriteOutput(io_bank.Outputs(args.set_io), args.set_io_value)

if __name__ == "__main__":
  main(sys.argv)
