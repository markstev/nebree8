# Encapsulates all the mechanical functions and sensors that comprise the
# Nebree8 robot.

import time

class Robot(object):
  def CalibrateToZero(self):
    """Moves the truck to position zero, relying on the touch sensor to stop it.
    """
    pass

  def MoveToPosition(self, position_in_inches):
    """Moves the truck to the requested absolute position.
    """
    pass

  def Fill(self, weight_in_grams):
    """Fills the cup at the current position with the given weight.
    """
    pass

  def ActivateCompressor(self):
    """Turns on the compressor.
    """
    pass

  def DeactivateCompressor(self):
    """Turns off the compressor.
    """
    pass


class FakeRobot(Robot):
  def __init__(self):
    self.position = 30.0

  def CalibrateToZero(self):
    self._FakeMove(0)
    
  def MoveToPosition(self, position_in_inches):
    self._FakeMove(0)
    
  def Fill(self, weight_in_grams):
    time.sleep(weight_in_grams / 20.0)

  def ActivateCompressor(self):
    return

  def DeactivateCompressor(self):
    return

  def _FakeMove(self, new_position):
    time.sleep((self.position - new_position) / 10.0)
    self.position = new_position * 1.0
