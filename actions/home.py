"""Return caddy to the home position."""

from actions.action import Action

class Home(Action):
    def __init__(self, carefully=True):
        self.carefully = carefully
    def __call__(self, robot):
      robot.CalibrateToZero(carefully=self.carefully)
    def sensitive(self):
      return True
