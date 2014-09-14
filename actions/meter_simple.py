#!/usr/bin/env python
import time

from actions.action import Action
from actions.meter import OZ_TO_ADC_VALUES, _tare

class MeterSimple(Action):
  def __init__(self, valve_to_actuate, oz_to_meter):
    self.valve_to_actuate = valve_to_actuate
    self.oz_to_meter = oz_to_meter
  def __call__(self, robot):
    if self.oz_to_meter == 0:
      logging.warning("oz_to_meter was zero, returning early.")
    tare = _tare(robot)
    self.target_reading = (tare.mean + OZ_TO_ADC_VALUES * self.oz_to_meter)
    with robot.OpenValve(self.valve_to_actuate):
      while robot.load_cell.recent_summary(secs=.2).mean < self.target_reading:
        time.sleep(.05)
    time.sleep(1)
    r = robot.load_cell.recent(secs = time.time() - tare.timestamp + 5)
    f = open('readings_%s_%foz.csv' % (
        time.strftime("%Y%m%d_%H%M%S"), self.oz_to_meter), 'w')
    for ts, v in r: print >>f, "%s,%s" % (ts, v)
    f.close()
