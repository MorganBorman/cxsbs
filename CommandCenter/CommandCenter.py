#!/usr/bin/env python

import os

orginal_dir = os.path.curdir

path = os.path.abspath(__file__)
path, _ = os.path.split(path)

os.chdir(path + "/www")

import SimpleHTTPServer
import SocketServer

PORT = 9998

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("192.168.1.7", PORT), Handler)

print "serving at port", PORT

try:
	httpd.serve_forever()
except KeyboardInterrupt:
	print ""
	httpd.shutdown()
	os.chdir(orginal_dir)