"""Meter a given amount of fluid into the container."""

import logging
import numpy

from actions.action import Action, ActionException
from collections import namedtuple
from time import time, sleep

VALVE_ACTUATION_DELAY_SECS = 0.3
ADC_VALUES_TO_OZ = 42
MAX_TARE_STDDEV = 2
TARE_TIMEOUT_SECS = 2
MAX_METER_SECS = 15

class TareTimeout(ActionException):
  """Thrown when attempt to tare times out"""


class MeterTimeout(ActionException):
  """Throw when metering takes too long after tare."""
  def __init__(self, tare, target_ts, recent_readings,
      complete_readings):
    super(MeterTimeout, self).__init__()
    self.tare = tare
    self.target_ts = target_ts
    self.recent_readings = recent_readings
    self.complete_readings = complete_readings
  def __str__(self):
    return ("Failed to meter within %s seconds. Tare=%s, Recent=%s" %
        (MAX_METER_SECS, self.tare, self.recent_readings))


def _tare(robot):
  """Waits for load cell readings to stabilize.

  returns: load_cell.Summary
  throws: Exception
  """
  tare_start = time()
  tare = robot.load_cell.recent_summary(secs=.1)
  while (tare.stddev > MAX_TARE_STDDEV and
         time() < tare_start + TARE_TIMEOUT_SECS):
    sleep(.1)
    tare = robot.load_cell.recent_summary(secs=.1)
  if tare.stddev > MAX_TARE_STDDEV:
    raise TareTimeout('Reading standard deviation while taring above ' +
        '%s for %s secs. Last result: %s' % (
          MAX_TARE_STDDEV, TARE_TIMEOUT_SECS, tare))
  return tare


def _predict_fill_completion(summary, target_reading):
  """Predicts when the ADC reading will hit the target value based on the last
  100ms of readings.

  args: summary is a load_cell.Summary
        target_reading is a target value in ADC space.
  returns: time as floating point secs since epoch
  """
  if summary.mean >= target_reading:
    return 0
  A = numpy.array([numpy.array([r[0] for r in summary.records]),
      numpy.ones(len(summary.records))])
  y = numpy.array([r[1] for r in summary.records])
  w = numpy.linalg.lstsq(A.T, y)[0]
  target_ts = (target_reading - w[1]) / (w[0])
  logging.info("target_ts=%s slope=%s intercept=%s", target_ts, w[0], w[1])
  return target_ts

FillInfo = namedtuple('FillInfo', ['m_actuation_delay', 'target_ts'])

def _wait_until_filled(tare, load_cell, target_reading, deadline):
  summary = tare
  target_ts = deadline
  mes_actuation_delay = None
  now = time()
  while target_ts - VALVE_ACTUATION_DELAY_SECS > now:
    yield FillInfo(mes_actuation_delay, target_ts)
    if time() > deadline:
      raise MeterTimeout(tare=tare, target_ts=target_ts,
          recent_readings=summary,
          complete_readings=load_cell.recent_summary(secs=MAX_METER_SECS))
    sleep(.01)
    now = time()
    summary = load_cell.recent_summary(secs=.1)
    # Log when readings actually start increasing.
    if summary.mean > tare.mean + tare.stddev * 2:
      mes_actuation_delay = now - tare.timestamp
      logging.info("Detected increase in weight after %ss: %s -> %s",
                mes_actuation_delay, tare, summary)
    target_ts = _predict_fill_completion(summary, target_reading)


class Meter(Action):
  def __init__(self, valve_to_actuate, oz_to_meter):
    self.valve_to_actuate = valve_to_actuate
    self.oz_to_meter = oz_to_meter

  def __call__(self, robot):
    if self.oz_to_meter == 0:
        logging.warning("oz_to_meter was zero, returning early.")
    self.tare = _tare(robot)
    target_reading = self.oz_to_meter / ADC_VALUES_TO_OZ * self.tare.mean
    with robot.OpenValve(self.valve_to_actuate):
      for info in _wait_until_filled(
          tare=self.tare,
          load_cell=robot.load_cell,
          target_reading=target_reading,
          deadline=self.tare.timestamp + MAX_METER_SECS):
        self.info = info
        self.elapsed = time() - self.tare.timestamp
        self.time_remaining = info.target_ts - time()
