#!/usr/bin/env python

import time
import threading
import collections
import logging
import os

from actions.action import ActionException

class Controller:
  def __init__(self, robot):
    self.current_action = None
    self.queue = collections.deque()
    self.queued_sem = threading.Semaphore(0)
    self.queue_lock = threading.Lock()
    self.resume_lock = threading.Lock()
    self.resume_lock.acquire()
    self.robot = robot
    self.last_exception = None
    self.__StartThread()

  def __StartThread(self):
    thread = threading.Thread(target=self.__Process)
    thread.daemon = True
    thread.start()

  def __Process(self):
    while True:
      print "Waiting for actions..."
      self.queued_sem.acquire() # Ensure there are items to process.
      with self.queue_lock:
        self.current_action = self.queue.popleft()
      try:
        self.current_action(self.robot)
      except ActionException, e:
        self.last_exception = e
        print "Waiting for resume signal..."
        self.resume_lock.acquire()
        print "...got it."
      except Exception, e:
        threading.Thread(target=self.KillProcess).start()
        raise
      finally:
        self.current_action = None

  def EnqueueGroup(self, action_group):
    with self.queue_lock:
      for action in action_group:
        self.queue.append(action)
        # Signal that there are items to process.
        self.queued_sem.release() 

  def InspectQueue(self):
    with self.queue_lock:
      return (([self.current_action] if self.current_action else []) +
          list(self.queue))

  def KillProcess(self):
    time.sleep(1)
    os._exit(1)

  def ClearAndResume(self):
    print "Clearing queue"
    self.last_exception = None
    self.queue.clear()
    self.resume_lock.release()

  def Retry(self):
    print "Kicking off retry..."
    self.last_exception = None
    self.queue.appendleft(self.current_action)
    self.queued_sem.release()
    self.resume_lock.release()
