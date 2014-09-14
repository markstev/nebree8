"""Move the caddy to an absolute position"""

from time import sleep

from actions.action import Action
from actions.meter import TARE_TIMEOUT_SECS

class WaitForGlassRemoval(Action):
    def __call__(self, robot):
      sleep(.1)
      self.initial = robot.load_cell.recent_summary(secs=.1)
      sleep(.1)
      while True:
        self.summary = robot.load_cell.recent_summary(secs=.1)
        if self.summary.mean < self.initial.mean - self.initial.stddev * 3:
          return
