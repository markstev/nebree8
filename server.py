#!/usr/bin/env python

import BaseHTTPServer
import logging
from monitor_load_cell import LoadCellMonitor

class NEEBre8Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, load_cell, *args, **kwargs):
        self.load_cell = load_cell
        self.dispatch = [
                ('/', lambda: self.serve('index.html')),
                ('/load_cell', lambda: self.serve('load_cell.html')),
                ('/load_cell.json', self.monitor_load_cell),
        ]
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def send_responsecode_and_headers(self, code, headers=()):
        self.send_response(code)
        for header in headers:
            self.send_header(*header)
        self.end_headers()

    def serve(self, fname):
        self.send_responsecode_and_headers(200, (("Content-type", "text/html"),))
        self.wfile.write(open('templates/' + fname, 'r').read())

    def find_handler(self):
        for route, handler in self.dispatch:
            if route == self.path:
                return handler
        return None

    def do_HEAD(self):
        if self.find_handler():
            self.send_responsecode_and_headers(200, (("Content-type", "text/html"),))
        else:
            self.send_responsecode_and_headers(404)

    def do_GET(self):
        handler = self.find_handler()
        if handler:
            try:
                handler()
            except IOError, e:
                logging.exception("Ignoring IOError while handling %s", self.path)
        else:
            self.send_response(404)
            self.end_headers()
        #DEBUG
        global httpd
        import threading
        class KillServer(threading.Thread):
            def run(self):
              self.load_cell.stop()
              httpd.shutdown()
        #KillServer().start()

    def monitor_load_cell(self):
        self.send_responsecode_and_headers(200, (("Content-type", "text/json"),))
        self.wfile.write("var data = [");
        self.wfile.write(','.join('[%s, %f]' % rec for rec in self.load_cell.recent(1000)))
        self.wfile.write("];");


def StartServer(port):
    global httpd # DEBUG
    load_cell = LoadCellMonitor()
    load_cell.start()
    httpd = BaseHTTPServer.HTTPServer(('', port), lambda *args: NEEBre8Handler(load_cell, *args))
    print "serving at http://localhost:%i" % port
    try:
        httpd.serve_forever(.2)
    except KeyboardInterrupt: pass


def main():
    import argparse

    parser = argparse.ArgumentParser(description="N.E.BRE-8 control server")
    parser.add_argument('--port', type=int, default=8000, help='Port to run on')
    args = parser.parse_args()
    StartServer(args.port)

if __name__ == "__main__":
    main()
