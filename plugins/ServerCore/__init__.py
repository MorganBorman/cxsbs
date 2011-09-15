from sbserver import *

from cxsbs.Plugin import Plugin

class ServerCore(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		print "ServerCore Plugin: load function"
		
	def reload(self):
		print "ServerCore Plugin: reload function"
		
	def unload(self):
		print "ServerCore Plugin: unload function"
		