#!/usr/bin/env python
import logging
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
    self.initial_reading = robot.load_cell.recent_summary(secs=.2).mean
    tare = _tare(robot)
    self.tare_reading = tare.mean
    self.target_reading = (tare.mean + OZ_TO_ADC_VALUES * self.oz_to_meter)
    last_summary = tare
    with robot.OpenValve(self.valve_to_actuate):
      while last_summary.mean < self.target_reading:
        time.sleep(.05)
        last_summary = robot.load_cell.recent_summary(secs=.2)
        self.current_reading = last_summary.mean
      self.final_reading = self.current_reading
    time.sleep(1)
    r = robot.load_cell.recent(secs = time.time() - tare.timestamp + 5)
    f = open('readings_%s_%foz.csv' % (
        time.strftime("%Y%m%d_%H%M%S"), self.oz_to_meter), 'w')
    for ts, v in r: print >>f, "%s,%s" % (ts, v)
    f.close()
