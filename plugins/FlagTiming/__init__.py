from cxsbs.Plugin import Plugin

class PluginTemplate(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		deinit()
		
def init():
	pass

def deinit():
	pass