"""Toggle compressor"""

import enum

from actions.action import Action

class State(enum.Enum):
  ON = 1
  OFF = 2

class CompressorToggle(Action):
    def __init__(self, state):
      self.state = state
    def __call__(self, robot):
      if self.state == State.ON:
        robot.ActivateCompressor()
      elif self.state == State.OFF:
        robot.DeactivateCompressor()
      else:
        print "BAD COMPRESSOR OPTION"
