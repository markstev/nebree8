#!/usr/bin/env python

import logging
import time

from actions.action import Action

class MeterBitters(Action):
  def __init__(self, valve_to_actuate, drops_to_meter):
    self.valve_to_actuate = valve_to_actuate
    self.drops_to_meter = drops_to_meter
  def __call__(self, robot):
    if self.drops_to_meter == 0:
      logging.warning("oz_to_meter was zero, returning early.")
    with robot.OpenValve(self.valve_to_actuate):
      time.sleep(self.drops_to_meter)
    time.sleep(1)
    records = robot.load_cell.recent(secs=self.drops_to_meter + 5)
    csv = open('readings_bitters_%s_%fs.csv' % (
      time.strftime("%Y%m%d_%H%M%S"), self.drops_to_meter), 'w')
    for record in records:
      print >>csv, "%s,%s" % record
    csv.close()
