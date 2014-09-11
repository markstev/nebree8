#!/usr/bin/env python

import webapp2
import BaseHTTPServer
import logging
import re
import socket

from actions.compressor import CompressorToggle
from actions.compressor import State
from actions.home import Home
from actions.meter import Meter
from actions.move import Move
from controller import Controller

robot = None
controller = None


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


class InspectQueue(webapp2.RequestHandler):
    def get(self):
        """Displays the state of the action queue."""
        actions = controller.InspectQueue()
        content = []
        if not actions:
            content.append("Queue is empty")
        else:
            for action in actions:
                name, props = action.inspect()
                content.append(name)
                for prop in props.items():
                  content.append('\t%s: %s' % prop)
        self.response.write(GetTemplate('queue.html').format(
          exception=controller.last_exception, content='\n'.join(content)))


class RetryQueue(webapp2.RequestHandler):
  def post(self):
    if controller.last_exception:
      controller.Retry()
    self.response.write("Restarted queue")


class ClearQueue(webapp2.RequestHandler):
  def post(self):
    if controller.last_exception:
      controller.ClearAndResume()
    self.response.write("Cleared queue")


class StaticFileHandler(webapp2.RequestHandler):
    def get(self):
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
        elif "test drink" in command:
          controller.EnqueueGroup([
              Home(),
              Meter(valve_to_actuate=0, oz_to_meter=1),
          ])
        elif "fill" in command:
          pass
        elif "move" in command:
          controller.EnqueueGroup([
              Move(float(details)),
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


def StartServer(port):
    from paste import httpserver

    app = webapp2.WSGIApplication([
        ('/', ServeFile('index.html')),
        ('/test_drink', MakeTestDrink),
        ('/load_cell', ServeFile('load_cell.html')),
        ('/load_cell.json', LoadCellJson),
        ('/queue', InspectQueue),
        ('/queue-retry', RetryQueue),
        ('/queue-clear', ClearQueue),
        ('/robot-control', RobotControlHandler),
        ('/templates/.*', StaticFileHandler),
        ('/bower_components/.*', StaticFileHandler)
    ])
    print "serving at http://%s:%i" % (socket.gethostname(), port)
    httpserver.serve(app, host="0.0.0.0", port=port)

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
