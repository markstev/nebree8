"""Move the caddy to an absolute position"""

import time

from actions.action import Action

class Move(Action):
    def __init__(self, position_in_inches):
      self.position_in_inches = position_in_inches
    def __call__(self, robot):
      robot.MoveToPosition(self.position_in_inches)
