#!/usr/bin/python

import math
import random
import time
import threading

from Adafruit_ADS1x15 import ADS1x15
from collections import deque

SAMPLES_PER_SECOND=256
ADS1115 = 1

class LoadCellMonitor(threading.Thread):
    def __init__(self, bufsize=10000, adc=None):
        super(LoadCellMonitor, self).__init__()
        self.buffer = deque(maxlen=bufsize)
        try:
          self.adc = ADS1x15(ic=ADS1115) if not adc else adc
        except IOError, e:
          print "Failed to open i2c device -- have you run ./setup.py initialize?\n"
          raise
        self.shutdown = False
        self.daemon = True
        self.start()

    def recent(self, n):
        """Return the last n readings as (time, value) tuples."""
        return list(deque(self.buffer, n))

    def recent_summary(self, n):
        """Return the mean and standard deviation of the last n readings."""
        recs = self.recent(n)
        n = len(recs)
        mean = sum(v for t, v in recs) / n
        stddev = math.sqrt(sum((v - mean)**2 for t, v in recs) / (n - 1))
        return mean, stddev

    def stop(self):
        self.shutdown = True
        self.join()

    def run(self):
        while not self.shutdown:
            val = self.adc.readADCSingleEnded(
                    1, 4096, SAMPLES_PER_SECOND) / 1000.0
            ts = time.time()
            self.buffer.append((ts, val))


class FakeLoadCellMonitor(LoadCellMonitor):
  def __init__(self, *args, **kwargs):
    self.random = random.Random()
    self.load_per_second = 0
    self.mean = 100.
    self.stddev = 2.
    self.last_read = time.time()
    self.sample_time_pct_var = .1
    super(FakeLoadCellMonitor, self).__init__(
            *args, adc=self, **kwargs)

  def readADCSingleEnded(self, _ch, _max, sample_rate):
    time.sleep(self.random.gauss(1., self.sample_time_pct_var) /
            sample_rate)  # sleep for the sample period
    sample_ts = time.time()
    self.mean += self.load_per_second * (sample_ts - self.last_read)
    self.last_read = sample_ts
    return self.random.gauss(self.mean, self.stddev)


def main():
  from math import sqrt
  N = 100000
  while True:
    monitor = FakeLoadCellMonitor(bufsize=N)
    time.sleep(1)
    monitor.stop()
    n = len(monitor.recent(N))
    mean, stddev = monitor.recent_summary(N)
    print "n=%i mean=%f stddev=%f" % (n, mean, stddev)



if __name__ == "__main__":
  main()
