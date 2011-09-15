from cxsbs.Plugin import Plugin

from PluginConfig import PluginConfig

class Config(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		print "Config Plugin: load function"
		
	def reload(self):
		print "Config Plugin: reload function"
		
	def unload(self):
		print "Config Plugin: unload function"
		