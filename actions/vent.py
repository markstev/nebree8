"""Vent pressure to ATM."""

from actions.action import Action

class Vent(Action):
    def __call__(self, robot):
      robot.Vent()
