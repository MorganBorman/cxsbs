class voting(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		handlers()
		
		Interfaces = {}
		Resources = 	{}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
def handlers():
	
	import sbserver
	
	org = pyTensible.plugin_loader.get_resource("org")
	
	@org.cxsbs.core.events.manager.event_handler('client_map_vote')
	def on_client_map_vote(event):
		sbserver.serverSetMapMode(event.args[1], event.args[2])