class policy_events(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
org = pyTensible.plugin_loader.get_resource("org")

@org.cxsbs.core.events.event_handler('client_connect_pre')
def on_client_connect_pre(event):
	pass