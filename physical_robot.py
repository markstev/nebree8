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
    motor = StepperMotor(io=self.io, use_separate_process=True)  # Not a dry run
    self.rail = RobotRail(motor)
    self.load_cell = LoadCellMonitor()

  def CalibrateToZero(self, carefully=True):
    self.ChuckVent()
    self.cannot_interrupt = True
    self.rail.CalibrateToZero()
    self.cannot_interrupt = False
    self.PressurizeHead()
    self.io.WriteOutput(io_bank.Outputs.CHUCK, 1)
    # time.sleep(5)
    self.CompressorLock()
    # self.io.WriteOutput(io_bank.Outputs.CHUCK, 1)

  def MoveToPosition(self, position_in_inches):
    self.cannot_interrupt = True
    self.ChuckHoldHeadPressure()
    time.sleep(2)
    self.rail.FillPositions([position_in_inches])
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1)
    self.cannot_interrupt = False

  def PressurizeHead(self):
    print "Pressurize Head"
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 0)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0)
    self.io.WriteOutput(io_bank.Outputs.CHUCK, 0)

  def Vent(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1)

  def ChuckVent(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0)
    self.io.WriteOutput(io_bank.Outputs.CHUCK, 0)

  def ChuckHoldHeadPressure(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 0)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0)
    self.io.WriteOutput(io_bank.Outputs.CHUCK, 0)

  def CompressorLock(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_HEAD, 0)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 1)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1)
    time.sleep(0.5)
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR_VENT, 0)
    self.io.WriteOutput(io_bank.Outputs.CHUCK, 0)

  @contextmanager
  def OpenValve(self, valve_no):
    self.PressurizeHead()
    valve_io = io_bank.GetValve(valve_no)
    self.io.WriteOutput(valve_io, 1)
    print "OPEN VALVE: %d -> %s (wired at %d)" % (valve_no, valve_io, valve_io.value)
    yield
    self.io.WriteOutput(valve_io, 0)
    self.CompressorLock()
    print "CLOSE VALVE: %s" % valve_io

  def ActivateCompressor(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0)

  def DeactivateCompressor(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1)
