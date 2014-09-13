from contextlib import contextmanager
import time

import io_bank
from robot import Robot
from parts.load_cell import LoadCellMonitor
from motor import StepperMotor, RobotRail


def IngredientToValve(ingredient_index):
  return Outputs(1000 + ingredient_index)


class PhysicalRobot(Robot):
  """Implementation of Robot that interfaces with real hardware."""
  def __init__(self):
    self.io = io_bank.IOBank()
    motor = StepperMotor(io=self.io)  # Not a dry run
    self.rail = RobotRail(motor)
    self.load_cell = LoadCellMonitor()

  def CalibrateToZero(self):
    self.cannot_interrupt = True
    self.rail.CalibrateToZero()
    self.cannot_interrupt = False

  def MoveToPosition(self, position_in_inches):
    self.cannot_interrupt = True
    self.rail.FillPositions([position_in_inches])
    self.cannot_interrupt = False

  @contextmanager
  def OpenValve(self, valve_no):
    valve_io = io_bank.GetValve(valve_no)
    self.io.WriteOutput(valve_io, 1)
    print "OPEN VALVE: %s" % valve_io
    time.sleep(5)
    yield
    self.io.WriteOutput(valve_io, 0)

  def ActivateCompressor(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0)

  def DeactivateCompressor(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1)
