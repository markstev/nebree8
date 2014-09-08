#!/usr/bin/env python

import webapp2
import BaseHTTPServer
import logging
import re
import socket

from controller import Controller
from actions.meter import Meter
from actions.home import Home

robot = None
controller = None

def ServeFile(filename):
    class ServeFileImpl(webapp2.RequestHandler):
        def get(self):
            self.response.write(open('templates/' + filename).read())
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
            Meter(valve_to_actuate=0, oz_to_meter=1),
        ])
        self.response.write("Queued.")


class CheckQueue(webapp2.RequestHandler):
    def get(self):
        self.response.write('\n'.join('%s\n\t%s' % a.inspect()
            for a in controller.InspectQueue()))

def StartServer(port):
    from paste import httpserver

    app = webapp2.WSGIApplication([
        ('/', ServeFile('index.html')),
        ('/test_drink', MakeTestDrink),
        ('/load_cell', ServeFile('load_cell.html')),
        ('/load_cell.json', LoadCellJson)
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
        from robot import FakeRobot
        robot = FakeRobot()
    else:
        from physical_robot import PhysicalRobot
        robot = PhysicalRobot()
    controller = Controller(robot)
    StartServer(args.port)

if __name__ == "__main__":
    main()
