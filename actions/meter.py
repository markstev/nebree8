"""Meter a given amount of fluid into the container."""

import logging
import numpy

from actions.action import Action, ActionException
from collections import namedtuple
from time import time, sleep

VALVE_ACTUATION_DELAY_SECS = 0.5
OZ_TO_ADC_VALUES = 40
MAX_TARE_STDDEV = 5.
TARE_TIMEOUT_SECS = 2.
MAX_METER_SECS = 15.

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


def _format_summary(start_ts, s):
  return 'elapsed=%s mean=%s stddev=%s' % (s.timestamp - start_ts, s.mean, s.stddev)


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
    return 0, None, None
  x = numpy.array([r[0] - summary.timestamp for r in summary.records])
  A = numpy.vstack([x, numpy.ones(len(x))]).T
  y = numpy.array([r[1] for r in summary.records])
  w = numpy.linalg.lstsq(A, y)[0]
  target_ts = (target_reading - w[1]) / (w[0]) + summary.timestamp
  if target_ts < summary.timestamp:  # Slope is negative, probably due to noise.
    return summary.timestamp + MAX_METER_SECS, w[0], w[1]
  return (target_ts, w[0], w[1])

FillInfo = namedtuple('FillInfo', ['m_actuation_delay', 'target_ts', 'summary',
    'slope', 'intercept'])

def _wait_until_filled(tare, load_cell, target_reading, deadline):
  summary = tare
  target_ts = deadline
  mes_actuation_delay = None
  slope, intercept = None, None
  while target_ts - VALVE_ACTUATION_DELAY_SECS > time():
    yield FillInfo(mes_actuation_delay, target_ts, summary, slope, intercept)
    if time() > deadline:
      raise MeterTimeout(tare=tare, target_ts=target_ts,
          recent_readings=summary,
          complete_readings=load_cell.recent_summary(secs=MAX_METER_SECS))
    sleep(.01)
    summary = load_cell.recent_summary(secs=.3)
    # Log when readings actually start increasing.
    if not mes_actuation_delay and summary.mean > tare.mean + tare.stddev * 3:
      mes_actuation_delay = time() - tare.timestamp
      logging.info("Detected increase in weight after %ss", mes_actuation_delay)
    target_ts, slope, intercept = _predict_fill_completion(
        summary, target_reading)


class Meter(Action):
  def __init__(self, valve_to_actuate, oz_to_meter):
    self.valve_to_actuate = valve_to_actuate
    self.oz_to_meter = oz_to_meter

  def __call__(self, robot):
    if self.oz_to_meter == 0:
        logging.warning("oz_to_meter was zero, returning early.")
    start_ts = time()
    print "Waiting to tare"
    self.tare = _tare(robot)
    print "Tared", _format_summary(start_ts, self.tare)
    self.adc_units_to_meter = self.oz_to_meter * OZ_TO_ADC_VALUES
    self.target_reading = self.adc_units_to_meter + self.tare.mean
    print "target_reading=%s oz_to_meter=%s self.tare.mean=%s" % (
       self.target_reading, self.oz_to_meter, self.tare.mean)
    self.measured_actuation_delay = 2.
    last_print = 0
    self.last_readings = self.tare
    while (self.last_readings.mean <
            (self.adc_units_to_meter * .8) + self.tare.mean):
      with robot.OpenValve(self.valve_to_actuate):
        for info in _wait_until_filled(
            tare=self.tare,
            load_cell=robot.load_cell,
            target_reading=self.target_reading,
            deadline=self.tare.timestamp + MAX_METER_SECS):
          self.info = info
          self.elapsed = time() - self.tare.timestamp
          self.time_remaining = info.target_ts - time()
          self.measured_actuation_delay = info.m_actuation_delay
          if time() - last_print > (1 if not info.m_actuation_delay else .2):
            print "Info mad=%s target_ts=%s elapsed=%s time_remaining=%s slope=%s intercept=%s %s" % (
                info.m_actuation_delay, info.target_ts, self.elapsed,
                self.time_remaining, info.slope, info.intercept,
                _format_summary(start_ts, info.summary))
            last_print = time()
      print "Valve was open for %s seconds." % (time() - self.tare.timestamp)
      sleep(max(2 * (self.measured_actuation_delay or 0), 1))
      self.last_readings = robot.load_cell.recent_summary(secs=.3)
      print "Readings after sleep: %s" % (
          _format_summary(start_ts, self.last_readings))

