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
from config import ingredients
from drinks import manual_db
from drinks.random_drinks import RandomSourDrink, RandomSpirituousDrink

robot = None
controller = None

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


class DrinkDbHandler(webapp2.RequestHandler):
  def get(self):
    self.response.content_type = 'application/javascript'
    self.response.write("db = ['%s'];" % "','".join(
      r.name for r in manual_db.db))


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
    controller.ClearAndResume()
    self.response.write(META_REFRESH.format(msg="Cleared...", url="/queue"))


class SkipQueue(webapp2.RequestHandler):
  def post(self):
    if controller.last_exception:
      controller.SkipAndResume()
    self.response.write(META_REFRESH.format(msg="Skipped...", url="/queue"))


class StaticFileHandler(webapp2.RequestHandler):
    """Serve static files out of / and /templates."""
    def get(self):
        if '.svg' in self.request.path:
            self.response.content_type = 'application/svg+xml'
        elif '.png' in self.request.path:
            self.response.content_type = 'image/png'
        elif '.jpg' in self.request.path:
            self.response.content_type = 'image/jpg'
        elif '.js' in self.request.path:
            self.response.content_type = 'application/javascript'
        relative_path = self.to_relative_path(self.request.path)
        try:
            self.response.write(open(relative_path).read())
        except IOError:
            self.response.status = 404

    def to_relative_path(self, path):
        if len(path) > 0 and path[0] == "/":
            return path[1:]


def SingleActionHandler(action):
    """Create a handler for queueing the given action class"""
    class Handler(webapp2.RequestHandler):
        def post(self):
            controller.EnqueueGroup([action(),])
            self.response.write("%s action queued." % action.__name__)
    return Handler


def valve_position(valve_no):
    return -10.75 - 4.0 * (14 - valve_no)

def actions_for_recipe(recipe):
    """Returns the actions necessary to make the given recipe.

    recipe: manual_db.Recipe
    """
    logging.info("Enqueuing actions for recipe %s", recipe)
    actions = []
    for ingredient in recipe.ingredients:
        valve = ingredients.INGREDIENTS_ORDERED.index(ingredient.name.lower())
        actions.append(Move(valve_position(valve)))
        if hasattr(ingredient.qty, 'drops'):
            actions.append(MeterBitters(
                valve_to_actuate=valve, drops_to_meter=ingredient.qty.drops))
        elif hasattr(ingredient.qty, 'oz'):
            actions.append(Meter(
                valve_to_actuate=valve, oz_to_meter=ingredient.qty.oz))
        else:
            raise Exception("Ingredient %s has no quantity for recipe %s:\n%s",
                    ingredient.name, recipe.name, recipe)
    actions.append(Move(0.0))
    actions.append(Home(carefully=False))
    return actions


class DrinkHandler(webapp2.RequestHandler):
    def post(self):
        name = self.request.get('name')
        if name:
            for drink in manual_db.db:
                if drink.name.lower() == name.lower():
                    self.response.write("Making drink %s" % drink)
                    controller.EnqueueGroup(actions_for_recipe(drink))
                    return
        elif self.request.get('random') == 'sour':
            controller.EnqueueGroup(actions_for_recipe(RandomSourDrink()))
        elif self.request.get('random') == 'spirituous':
            controller.EnqueueGroup(actions_for_recipe(RandomSpirituousDrink()))
        self.response.status = 400


class PrimeHandler(webapp2.RequestHandler):
    def post(self):
        controller.EnqueueGroup(actions_for_recipe(
            manual_db.Recipe(name='Prime', ingredients=[
                manual_db.Ingredient(manual_db.Oz(.25), ingredient)
                for ingredient in ingredients.INGREDIENTS_ORDERED])))


class FillHandler(webapp2.RequestHandler):
    def post(self):
        try:
            valve = int(self.request.get('valve'))
            oz = float(self.request.get('oz'))
            controller.EnqueueGroup([Meter(valve_to_actuate=valve, oz_to_meter=oz)])
        except ValueError:
            self.response.status = 400
            self.response.write("valve and oz arguments are required.")


class MoveHandler(webapp2.RequestHandler):
    def post(self):
        controller.EnqueueGroup([Move(float(self.request.get('to')))])


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
        # User UI
        ('/', ServeFile('index-iframe.html')),
        ('/templates/.*', StaticFileHandler),
        ('/bower_components/.*', StaticFileHandler),
        ('/drinks.js', DrinkDbHandler),
        # User API
        ('/api/drink', DrinkHandler),
        # Debug UI
        ('/load_cell', ServeFile('load_cell.html')),
        ('/load_cell.json', LoadCellJson),
        ('/queue', InspectQueue),
        ('/queue.json', InspectQueueJson),
        # Control API
        ('/queue-retry', RetryQueue),
        ('/queue-clear', ClearQueue),
        ('/queue-skip', SkipQueue),
        # Debug API
        ('/api/calibrate', SingleActionHandler(Home)),
        ('/api/vent', SingleActionHandler(Vent)),
        ('/api/compressor-on',
         SingleActionHandler(lambda: CompressorToggle(State.ON))),
        ('/api/compressor-off',
         SingleActionHandler(lambda: CompressorToggle(State.OFF))),
        ('/api/prime', PrimeHandler),
        ('/api/move', MoveHandler),
        ('/api/fill', FillHandler),
    ])
    controller.app = app
    print "serving at http://%s:%i" % (socket.gethostname(), port)
    httpserver.serve(app, host="0.0.0.0", port=port, start_loop=True)

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
