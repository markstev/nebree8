#!/usr/bin/env python

import webapp2
import BaseHTTPServer
import json
import logging
import re
import socket
import time

from actions.compressor import CompressorToggle
from actions.compressor import State
from actions.home import Home
#from actions.meter import Meter
#from actions.meter_dead_reckoned import MeterDeadReckoned as Meter
from actions.meter_simple import MeterSimple as Meter
from actions.meter_bitters import MeterBitters
from actions.move import Move
from actions.vent import Vent
from actions.wait_for_glass_removal import WaitForGlassRemoval
from controller import Controller
import ingredients

robot = None
controller = None

WT_TO_OZ = 0.375

class CustomJsonEncoder(json.JSONEncoder):
  def default(self, obj):
    if (hasattr(obj, '__class__') and
        obj.__class__.__name__ in ('ActionException', 'LoadCellMonitor',
            'TareTimeout', 'MeterTimeout')):
      key = '__%s__' % obj.__class__.__name__
      return {key: obj.__dict__}
    return json.JSONEncoder.default(self, obj)

def GetTemplate(filename):
    return open('templates/' + filename).read()


def ServeFile(filename):
    class ServeFileImpl(webapp2.RequestHandler):
        def get(self):
            self.response.write(GetTemplate(filename))
    return ServeFileImpl


class LoadCellJson(webapp2.RequestHandler):
    def get(self):
        self.response.write("[")
        self.response.write(','.join('[%s, %f]' % rec
                            for rec in robot.load_cell.recent(1000)))
        self.response.write("]")


class MakeTestDrink(webapp2.RequestHandler):
    def get(self):  # TODO: Switch to post.
        controller.EnqueueGroup([
            Home(),
            Move(5),
            Meter(valve_to_actuate=1, oz_to_meter=1),
            Move(10),
            Meter(valve_to_actuate=2, oz_to_meter=2),
        ])
        self.response.write("Queued.")


class InspectQueueJson(webapp2.RequestHandler):
    def get(self):
        """Displays the state of the action queue."""
        self.response.write(json.dumps({
          'actions': [action.inspect() for action in controller.InspectQueue()],
          'exception': controller.last_exception}, cls=CustomJsonEncoder))

class InspectQueue(webapp2.RequestHandler):
    def get(self):
        """Displays the state of the action queue."""
        actions = controller.InspectQueue()
        content = []
        if not actions:
            content.append("Queue is empty")
        else:
            for action in actions:
                d = action.inspect()
                name, props = d['name'], d['args']
                content.append(name)
                for prop in props.items():
                  content.append('\t%s: %s' % prop)
        self.response.write(GetTemplate('queue.html').format(
          exception=controller.last_exception, content='\n'.join(content),
          robot_dict=robot.__dict__))

META_REFRESH="""
<html>
  <head>
    <title>{msg}</title>
    <meta http-equiv="refresh" content="2;URL={url}">
  </head>
<body>
{msg}
</body>
</html>
"""

class RetryQueue(webapp2.RequestHandler):
  def post(self):
    if controller.last_exception:
      controller.Retry()
    self.response.write(META_REFRESH.format(msg="Retrying...", url="/queue"))


class ClearQueue(webapp2.RequestHandler):
  def post(self):
    if controller.last_exception:
      controller.ClearAndResume()
    self.response.write(META_REFRESH.format(msg="Cleared...", url="/queue"))


class SkipQueue(webapp2.RequestHandler):
  def post(self):
    if controller.last_exception:
      controller.SkipAndResume()
    self.response.write(META_REFRESH.format(msg="Skipped...", url="/queue"))


class StaticFileHandler(webapp2.RequestHandler):
    def get(self):
        if '.svg' in self.request.path:
            self.response.content_type = 'application/svg+xml'
        elif '.png' in self.request.path:
            self.response.content_type = 'image/png'
        elif '.jpg' in self.request.path:
            self.response.content_type = 'image/jpg'
        self.response.write(open(self.ToRelativePath(self.request.path)).read())
    def ToRelativePath(self, path):
        if (len(path) > 0 and path[0] == "/"):
            return path[1:]


class RobotControlHandler(webapp2.RequestHandler):
    def post(self):
        command = self.request.get("command")
        details = self.request.get("text")
        print command
        print details
        if "calibrate" in command:
          controller.EnqueueGroup([
              Home(),
          ])
        elif "drink" in command:
          target_composition = None
          print "DRINK COMMAND: %s" % command
          if "test1" in command:
            print "DRINK COMMAND: %s" % command
            ingredient_to_wt_loc = ingredients.CreateTestDrink(1)
          elif "test" in command:
            print "DRINK COMMAND: %s" % command
            ingredient_to_wt_loc = ingredients.CreateTestDrink()
          elif "sour drink" in command:
            target_composition = [2, 1, 1, 0]
            ingredient_to_wt_loc = ingredients.CreateRandomDrink(target_composition)
          elif "!!prime" in command:
            ingredient_to_wt_loc = ingredients.PrimeRun()
          else:
            target_composition = [4, 1, 0, 1]
            ingredient_to_wt_loc = ingredients.CreateRandomDrink(target_composition)
          actions = []
          ingredient_tuples = [(x, y, z) for x, (y, z) in ingredient_to_wt_loc.iteritems()]
          ingredient_tuples = sorted(ingredient_tuples, key=lambda x: -x[2])
          for ingredient, wt, loc in ingredient_tuples:
            print "%s oz of %s at %f on valve %s" % (wt, ingredient, loc, loc)
            actions.append(Move(-10.5 - 4.0 * (14 - loc)))
            if 'bitter' in ingredient:
              actions.append(MeterBitters(valve_to_actuate=loc, drops_to_meter=6))
            else:
              actions.append(Meter(valve_to_actuate=loc, oz_to_meter=(wt * WT_TO_OZ)))
          actions.append(Home())
          actions.append(WaitForGlassRemoval())
          controller.EnqueueGroup(actions)
          self.response.write("Randomized ingredients: %s" %
              ", ".join([x[0] for x in ingredient_tuples]))
          return
        elif "fill" in command:
          oz, valve = details.split(",")
          oz = float(oz)
          valve = int(valve)
          controller.EnqueueGroup([
              Meter(valve_to_actuate = valve, oz_to_meter = oz),
          ])
        elif "move" in command:
          controller.EnqueueGroup([
              Move(float(details)),
          ])
        elif "vent" in command:
          controller.EnqueueGroup([
              Vent(),
          ])
        elif "compressor on" in command:
          controller.EnqueueGroup([
              CompressorToggle(State.ON)
          ])
        elif "compressor off" in command:
          controller.EnqueueGroup([
              CompressorToggle(State.OFF)
          ])
        self.response.write("ok")
    def get(self):
        print "Shouldn't call get!"


class PausableWSGIApplication(webapp2.WSGIApplication):
  def __init__(self, routes=None, debug=False, config=None):
    super(PausableWSGIApplication, self).__init__(routes=routes, debug=debug, config=config)
    self.drop_all = False

  def __call__(self, environ, start_response):
    while self.drop_all:
      time.sleep(1.0)
    return super(PausableWSGIApplication, self).__call__(environ, start_response)

def StartServer(port):
    from paste import httpserver

    logging.basicConfig(
        filename="/dev/stdout",
        #filename="server_%s.log" % time.strftime("%Y%m%d_%H%M%S"),
        filemode='w',
        level=logging.INFO)
    #app = webapp2.WSGIApplication([
    app = PausableWSGIApplication([
        ('/', ServeFile('index-iframe.html')),
        ('/test_drink', MakeTestDrink),
        ('/load_cell', ServeFile('load_cell.html')),
        ('/load_cell.json', LoadCellJson),
        ('/queue', InspectQueue),
        ('/queue.json', InspectQueueJson),
        ('/queue-retry', RetryQueue),
        ('/queue-clear', ClearQueue),
        ('/queue-skip', SkipQueue),
        ('/robot-control', RobotControlHandler),
        ('/templates/.*', StaticFileHandler),
        ('/bower_components/.*', StaticFileHandler)
    ])
    controller.app = app
    print "serving at http://%s:%i" % (socket.gethostname(), port)
    # from multiprocessing import Pool
    # pool = Pool(5)
    # while True:
    #   while app.drop_all:
    #     time.sleep(1.0)
    httpserver.serve(app, host="0.0.0.0", port=port, start_loop=True)  #, use_threadpool=pool)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="N.E.BRE-8 control server")
    parser.add_argument('--port', type=int, default=8000, help='Port to run on')
    parser.add_argument('--fake', dest='fake', action='store_true')
    parser.add_argument('--nofake', dest='fake', action='store_false')
    parser.set_defaults(fake=False)
    args = parser.parse_args()

    global robot
    global controller
    if args.fake:
        from fake_robot import FakeRobot
        robot = FakeRobot()
    else:
        from physical_robot import PhysicalRobot
        robot = PhysicalRobot()
    controller = Controller(robot)
    StartServer(args.port)

if __name__ == "__main__":
    main()
