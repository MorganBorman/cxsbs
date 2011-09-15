from cxsbs.Plugin import Plugin

class Logging(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		print "Logging Plugin: load function"
		
	def reload(self):
		print "Events Plugin: reload function"
		
	def unload(self):
		print "Events Plugin: unload function"
		