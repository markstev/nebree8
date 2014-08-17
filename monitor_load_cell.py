#!/usr/bin/python

import time
import threading
from Adafruit_ADS1x15 import ADS1x15
from collections import deque


class LoadCellMonitor(threading.Thread):
    def __init__(self, bufsize=10000):
        super(LoadCellMonitor, self).__init__()
        self.buffer = deque(maxlen=bufsize)
        self.adc = ADS1x15(ic=1)  # 1 for ADS1115
        self.shutdown = False

    def recent(self, n):
        return list(deque(self.buffer, n))

    def stop(self):
        self.shutdown = True
        self.join()

    def run(self):
        while not self.shutdown:
            val = self.adc.readADCDifferential01(4096, 250)/1000.0
            ts = time.time()
            self.buffer.append((ts, val))


def main():
  from math import sqrt
  while True:
    monitor = LoadCellMonitor(bufsize=100000)
    monitor.start()
    time.sleep(1)
    monitor.stop()
    recs = monitor.recent(100000)
    n = len(recs)
    mean = sum(v for t, v in recs)
    stddev = sqrt(sum((v - mean)**2 for t, v in recs) / (n - 1))
    print "n=%i mean=%f stddev=%f" % (n, mean, stddev)



if __name__ == "__main__":
  main()
