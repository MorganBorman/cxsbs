class policy_events(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		handlers()
		
		Interfaces = {}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
def handlers():
	import sbserver
		
	org = pyTensible.plugin_loader.get_resource("org")
	
	@org.cxsbs.core.events.manager.event_handler('client_connect_pre')
	def on_client_connect_pre(event):
		sbserver.clientInitialize(event.args[0])
	
	@org.cxsbs.core.events.manager.event_handler('client_auth_timout')
	def on_client_auth_timout(event):
		pass
	
	@org.cxsbs.core.events.manager.event_handler('client_auth_challenge_response')
	def on_client_auth_challenge_response(event):
		pass
	
	@org.cxsbs.core.events.manager.event_handler('client_message_pre')
	def on_client_auth_timout(event):
		if event.args[1] == "#reload":
			sbserver.serverReload()