"""Meter a given amount of fluid into the container."""

import logging
import time

from actions.action import Action


VALVE_ACTUATION_DELAY_SECS = 0.3
ADC_VALUES_TO_OZ = 2.5 / (1000 * 1./30)
MAX_TARE_STDDEV = .03
TARE_TIMEOUT_SECS = 2
MAX_METER_SECS = 5

class TareTimeout(Exception):
    """Thrown when attempt to tare times out"""

class MeterTimeout(Exception):
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


def __tare(robot):
    """Waits for load cell readings to stabilize.

    returns: load_cell.Summary
    throws: Exception
    """
    tare_start = time.time()
    tare = robot.load_cell.recent_summary(secs=.1)
    while (tare.stddev > MAX_TARE_STDDEV and
            time.time() < tare_start + TARE_TIMEOUT_SECS):
        time.sleep(.1)
        tare = robot.load_cell.recent_summary(secs=.1)
    if tare.stddev > MAX_TARE_STDDEV:
        raise TareTimeout('Reading standard deviation while taring above ' +
                '%s for %s secs. Last result: %s' % (
                    MAX_TARE_STDDEV, TARE_TIMEOUT_SECS, tare))
    return tare

def __predict_fill_completion(summary, target_reading):
    """Predicts when the ADC reading will hit the target value based on the last
    100ms of readings.

    args: summary is a load_cell.Summary
          target_reading is a target value in ADC space.
    returns: time as floating point secs since epoch
    """
    if summary.mean >= target_reading:
        return 0
    else:
        return time.time() + VALVE_ACTUATION_DELAY_SECS + .01

class Meter(Action):
    def __init__(self, valve_to_actuate, oz_to_meter):
        self.valve_to_actuate = valve_to_actuate
        self.oz_to_meter = oz_to_meter

    def __callable__(self, robot):
        if self.oz_to_meter == 0:
            logging.warning("oz_to_meter was zero, returning early.")
        tare = __tare(robot)
        target_reading = self.oz_to_meter / ADC_VALUES_TO_OZ * tare.mean
        summary = tare
        target_ts = tare.timestamp + MAX_METER_SECS
        # TODO(sagarmittal): Actuate valve_to_actuate
        while target_ts - VALVE_ACTUATION_DELAY_SECS > time.time():
            if time.time() > tare.timestamp + MAX_METER_SECS:
                raise MeterTimeout(tare=tare, target_ts=target_ts,
                        recent=summary,
                        readings=robot.load_cell.recent_summary(secs=MAX_METER_SECS))
            time.sleep(.05)
            summary = robot.load_cell.recent_summary(secs=.1)
            # Log when readings actually start increasing.
            if summary.mean > tare.mean + tare.stddev * 2:
                logging.info("Detected increase in weight after %ss: %s -> %s",
                        time.time() - tare.timestamp, tare, summary)
            target_ts = __predict_fill_completion(summary, target_reading)
        #TODO(sagarmittal): Actuate valve_to_actuate
