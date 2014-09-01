#!/usr/bin/env python

import webapp2
import BaseHTTPServer
import logging
import re
import socket
from monitor_load_cell import LoadCellMonitor


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

def StartServer(port):
    from paste import httpserver
    load_cell = LoadCellMonitor()
    load_cell.daemon = True
    load_cell.start()

    app = webapp2.WSGIApplication([
        ('/', ServeFile('index.html')),
        ('/load_cell', ServeFile('load_cell.html')),
        ('/load_cell.json', LoadCellJson(load_cell))
    ])
    print "serving at http://%s:%i" % (socket.gethostname(), port)
    httpserver.serve(app, host="0.0.0.0", port=port)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="N.E.BRE-8 control server")
    parser.add_argument('--port', type=int, default=8000, help='Port to run on')
    args = parser.parse_args()
    StartServer(args.port)

if __name__ == "__main__":
    main()
