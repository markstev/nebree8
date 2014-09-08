import io_bank
from robot import Robot
from parts.load_cell import LoadCellMonitor
from motor import StepperMotor, RobotRail


class PhysicalRobot(Robot):
  """Implementation of Robot that interfaces with real hardware."""
  def __init__(self):
    self.io = io_bank.IOBank()
    motor = StepperMotor(io=self.io)  # Not a dry run
    self.rail = RobotRail(motor)
    self.load_cell = LoadCellMonitor()

  def CalibrateToZero(self):
    self.rail.CalibrateToZero()

  def MoveToPosition(self, position_in_inches):
    self.rail.FillPositions([position_in_inches])

  def Fill(self, weight_in_grams):
    pass

  def ActivateCompressor(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 0)

  def DeactivateCompressor(self):
    self.io.WriteOutput(io_bank.Outputs.COMPRESSOR, 1)
