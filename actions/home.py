"""Return caddy to the home position."""

from actions.action import Action

class Home(Action):
    def __call__(self, robot):
      robot.CalibrateToZero()
    def sensitive(self):
      return True
