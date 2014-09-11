#!/usr/bin/python

import math
import random
import time
import threading

from collections import deque, namedtuple

SAMPLES_PER_SECOND=256
ADS1115 = 1

Summary = namedtuple('Summary', ['records', 'mean', 'stddev', 'timestamp'])

class LoadCellMonitor(threading.Thread):
    """Continuously monitors and logs weight sensor readings."""
    def __init__(self, bufsize=10000, adc=None):
        super(LoadCellMonitor, self).__init__()
        self.buffer = deque(maxlen=bufsize)
        if not adc:
          try:
              from Adafruit_ADS1x15 import ADS1x15
              self.adc = ADS1x15(ic=ADS1115)
          except IOError:
              print ("Failed to open i2c device -- have you run ./setup.py " +
                      "initialize?\n")
              raise
        else:
          self.adc = adc
        self.shutdown = False
        self.daemon = True
        self.start()

    def recent(self, n=0, secs=0):
        """Return the last n readings as (time, value) tuples."""
        if n <= 0 and secs <= 0:
            return []
        if n > 0:
            return list(deque(self.buffer, n))
        n = SAMPLES_PER_SECOND * secs * 2
        recs = list(deque(self.buffer, n))
        threshold = time.time() - secs
        return [(ts, v) for ts, v in recs if ts > threshold]

    def recent_summary(self, n=0, secs=0):
        """Return a Summary of the last n readings."""
        recs = self.recent(n, secs)
        n = len(recs)
        if n == 0:
            return Summary([], 0, 0, time.time())
        mean = sum(v for t, v in recs) / n
        stddev = math.sqrt(sum((v - mean)**2 for t, v in recs) / (n - 1))
        return Summary(recs, mean, stddev, max(ts for ts, v in recs))

    def stop(self):
        self.shutdown = True
        self.join()

    def run(self):
        while not self.shutdown:
            val = self.adc.readADCSingleEnded(
                    1, 4096, SAMPLES_PER_SECOND)
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
  monitor = LoadCellMonitor(bufsize=100000)
  while True:
    time.sleep(1)
    recent = monitor.recent_summary(secs=1)
    n = len(recent.records)
    print "n=%i mean=%f stddev=%f" % (n, recent.mean, recent.stddev)



if __name__ == "__main__":
  main()
