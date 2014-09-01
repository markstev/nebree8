#!/usr/bin/python
import math
import time
import threading
from Adafruit_ADS1x15 import ADS1x15
from collections import deque


class LoadCellMonitor(threading.Thread):
    def __init__(self, bufsize=10000):
        super(LoadCellMonitor, self).__init__()
        self.buffer = deque(maxlen=bufsize)
        try:
          self.adc = ADS1x15(ic=1)  # 1 for ADS1115
        except IOError, e:
          print "Failed to open i2c device -- have you run ./setup.py initialize?\n"
          raise
        self.shutdown = False

    def recent(self, n):
        """Return the last n readings as (time, value) tuples."""
        return list(deque(self.buffer, n))

    def recent_summary(self, n):
        """Return the mean and standard deviation of the last n readings."""
        recs = self.recent(n)
        mean = sum(v for t, v in recs)
        stddev = math.sqrt(sum((v - mean)**2 for t, v in recs) / (n - 1))
        return mean, stddev

    def stop(self):
        self.shutdown = True
        self.join()

    def run(self):
        while not self.shutdown:
            val = self.adc.readADCSingleEnded(1, 4096, 256)/1000.0
            ts = time.time()
            self.buffer.append((ts, val))


def main():
  from math import sqrt
  N = 100000
  while True:
    monitor = LoadCellMonitor(bufsize=N)
    monitor.daemon = True
    monitor.start()
    time.sleep(1)
    monitor.stop()
    n = len(monitor.recent(N))
    mean, stddev = monitor.recent_summary(N)
    print "n=%i mean=%f stddev=%f" % (n, mean, stddev)



if __name__ == "__main__":
  main()
