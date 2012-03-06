class slice(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {'update': update}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

def update():
	try:
		pass
	except:
		pass

org = pyTensible.plugin_loader.get_resource("org")

@org.cxsbs.core.events.manager.event_handler('server_stop')
def on_server_stop(event):
	org.cxsbs.core.events.manager.trigger_event('server_shutdown')
	pyTensible.plugin_loader.unload_all()
	
@org.cxsbs.core.events.manager.event_handler('server_reload')
def on_server_stop(event):
	pyTensible.plugin_loader.unload_all()