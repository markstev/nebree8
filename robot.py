# Encapsulates all the mechanical functions and sensors that comprise the
# Nebree8 robot.

class Robot(object):
  def __init__(self):
    self.cannot_interrupt = False
  def UninterruptableMethod(self):
    return self.cannot_interrupt
  def CalibrateToZero(self):
    """Moves the truck to position zero, relying on the touch sensor to stop it.
    """
    raise NotImplementedError()

  def MoveToPosition(self, position_in_inches):
    """Moves the truck to the requested absolute position.
    """
    raise NotImplementedError()

  def OpenValve(self, valve_no):
    """Returns a context manager than holds open the specified valve.
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


