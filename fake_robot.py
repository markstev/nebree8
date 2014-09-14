
import time

from actions.action import ActionException
from contextlib import contextmanager
from parts.load_cell import FakeLoadCellMonitor
from robot import Robot

class FakeRobot(Robot):
  def __init__(self):
    import collections
    self.position = 30.0
    self.load_cell = FakeLoadCellMonitor()
    self.load_cell.stddev = 1
    self.valves = collections.defaultdict(lambda: False)

  def __check_position(self, valve_no):
    if abs(self.position - (-10.5 - 4. * (14 - valve_no))) > 1:
      raise ActionException("Caddy wasn't in the right position!")

  @staticmethod
  def __run_with_delay(delay_sec, fn):
    import threading
    def W():
      time.sleep(delay_sec)
      fn()
    t = threading.Thread(target=W)
    t.daemon = True
    t.start()

  def CalibrateToZero(self):
    self._FakeMove(0)
    
  def MoveToPosition(self, position_in_inches):
    old_stddev = self.load_cell.stddev
    self.load_cell.stddev *= 10
    self._FakeMove(position_in_inches)
    self.load_cell.stddev = old_stddev

  @contextmanager
  def OpenValve(self, valve_no):
    if self.valves[valve_no]:
      raise ActionException("Valve %s was already open!" % valve_no)
    self.valves[valve_no] = True
    self.__check_position(valve_no)
    self.__run_with_delay(
        .25, lambda: setattr(self.load_cell, 'load_per_second', 10))
    yield
    if not self.valves[valve_no]:
      raise ActionException("Valve %s wasn't open!" % valve_no)
    self.__check_position(valve_no)
    self.valves[valve_no] = False
    self.__run_with_delay(
        .25, lambda: setattr(self.load_cell, 'load_per_second', 0))

  def ActivateCompressor(self):
    return

  def DeactivateCompressor(self):
    return

  def _FakeMove(self, new_position):
    time.sleep(abs(self.position - new_position) / 10.0)
    self.position = new_position * 1.0
