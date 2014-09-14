#!/usr/bin/env python

import time
import threading
import collections
import logging
import os

from actions.action import ActionException
from actions.move import Move

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
    self.app = None

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
        if self.current_action.sensitive():
          self.app.drop_all = True
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
        self.app.drop_all = False

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

  def __Resume(self):
    self.last_exception = None
    self.resume_lock.release()

  def ClearAndResume(self):
    print "Clearing queue"
    self.queue.clear()
    self.__Resume()

  def SkipAndResume(self):
    self.__Resume()

  def Retry(self):
    print "Kicking off retry..."
    self.queue.appendleft(self.current_action)
    self.queued_sem.release()
    self.__Resume()
