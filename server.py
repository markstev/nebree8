#!/usr/bin/env python

import webapp2
import BaseHTTPServer
import logging
import re
import socket

def ServeFile(filename):
    class ServeFileImpl(webapp2.RequestHandler):
        def get(self):
            self.response.write(open('templates/' + filename).read())
    return ServeFileImpl


def LoadCellJson(load_cell):
    class LoadCellHandler(webapp2.RequestHandler):
        def get(self):
            self.response.write("[");
            self.response.write(','.join('[%s, %f]' % rec
                                for rec in load_cell.recent(1000)))
            self.response.write("]");
    return LoadCellHandler

def StartServer(port, robot):
    from paste import httpserver

    app = webapp2.WSGIApplication([
        ('/', ServeFile('index.html')),
        ('/load_cell', ServeFile('load_cell.html')),
        ('/load_cell.json', LoadCellJson(robot.load_cell))
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

    if args.fake:
      from robot import FakeRobot
      robot = FakeRobot()
    else:
      from physical_robot import PhysicalRobot
      robot = PhysicalRobot()
    StartServer(args.port, robot)

if __name__ == "__main__":
    main()
