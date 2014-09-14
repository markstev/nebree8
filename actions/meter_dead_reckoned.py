#!/usr/bin/env python
import time

from actions.action import Action

SECONDS_PER_OZ = 3

class MeterDeadReckoned(Action):
  def __init__(self, valve_to_actuate, oz_to_meter):
    self.valve_to_actuate = valve_to_actuate
    self.oz_to_meter = oz_to_meter
  def __call__(self, robot):
    if self.oz_to_meter == 0:
      logging.warning("oz_to_meter was zero, returning early.")
    t = self.oz_to_meter * SECONDS_PER_OZ
    with robot.OpenValve(self.valve_to_actuate):
      time.sleep(self.oz_to_meter * SECONDS_PER_OZ)
    r = robot.load_cell.recent(secs = t + 5)
    f = open('readings_%s_%fs.csv' % (
        time.strftime("%Y%m%d_%H%M%S"), t), 'w')
    for ts, v in r: print >>f, "%s,%s" % (ts, v)
    f.close()
