# Encapsulates all the mechanical functions and sensors that comprise the
# Nebree8 robot.

import time
from parts.load_cell import FakeLoadCellMonitor

class Robot(object):
  def CalibrateToZero(self):
    """Moves the truck to position zero, relying on the touch sensor to stop it.
    """
    raise NotImplementedError()

  def MoveToPosition(self, position_in_inches):
    """Moves the truck to the requested absolute position.
    """
    raise NotImplementedError()

  def Fill(self, weight_in_grams):
    """Fills the cup at the current position with the given weight.
    """
    raise NotImplementedError()

  def ActivateCompressor(self):
    """Turns on the compressor.
    """
    raise NotImplementedError()

  def DeactivateCompressor(self):
    """Turns off the compressor.
    """
    raise NotImplementedError()


class FakeRobot(Robot):
  def __init__(self):
    self.position = 30.0
    self.load_cell = FakeLoadCellMonitor()

  def CalibrateToZero(self):
    self._FakeMove(0)
    
  def MoveToPosition(self, position_in_inches):
    self._FakeMove(0)
    
  def Fill(self, weight_in_grams):
    self.load_cell.load_per_second = .05  # estimated flow rate
    time.sleep(weight_in_grams / 20.0)
    self.load_cell.load_per_second = 0

  def ActivateCompressor(self):
    return

  def DeactivateCompressor(self):
    return

  def _FakeMove(self, new_position):
    time.sleep((self.position - new_position) / 10.0)
    self.position = new_position * 1.0
