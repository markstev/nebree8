#!/usr/bin/env python

import threading
from controller import Controller
import Queue

class CharWrapper:
  def __init__(self, x):
    self.x = x
  def __call__(self, *args): pass

def testInspectQueue():
  controller = Controller(None)
  controller.EnqueueGroup(map(CharWrapper, "abcdef"))
  inspect_result = ''.join(a.x for a in controller.InspectQueue())
  if inspect_result != "abcdef":
    raise ValueError("Read bad result %s" % inspect_result)

def testMultiThreadedProcessing():
  controller = Controller(None)
  q = Queue.Queue()
  class CharWrapperAddToQueue(CharWrapper):
    def __call__(self, *args): q.put(self.x)
  def addItems():
    controller.EnqueueGroup(map(CharWrapperAddToQueue, 'abcd'))
  threads = [threading.Thread(target=addItems) for _ in range(100)]
  for thread in threads: thread.start()

  read = [q.get(True, 1) for _ in range(100 * len('abcd'))]
  if ''.join(read) != ('abcd' * 100):
    raise ValueError('Read bad result %s' % ''.join(read))

if __name__ == "__main__":
  testInspectQueue()
  testMultiThreadedProcessing()
