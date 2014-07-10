"""Top-level program to run the nebree8 robot.

Components:
  1) user-input drink request
  2) drink db lookup -> ingredients
  3) stock drinks match; translate to positions
  4) robot driver to fill from positions
"""

import argparse

def main(args):
  parser = argparse.ArgumentParser(description='Drink to mix')
  parser.add_argument('--drink', type=str, nargs="?", default="margarita",
                      help='Name of a drink')
  args = parser.parse_args()
  print "Not yet implemented"


if __name__ == "__main__":
  main(sys.argv)
