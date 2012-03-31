import pyTensible, org

class commands(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

@org.cxsbs.core.events.manager.event_handler('command')
def on_command(event):
	'''
	@thread commands
	'''
	print "got command."