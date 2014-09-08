"""Return caddy to the home position."""

import time

from actions.action import Action

class Home(Action):
    def __init__(self):
        self.remaining = 3

    def __call__(self, robot):
        for t in range(3):
            self.remaining = 3 - t  # For inspection
            time.sleep(1)
