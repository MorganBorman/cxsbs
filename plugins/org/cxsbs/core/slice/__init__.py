import pyTensible, org

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
	pass

@org.cxsbs.core.events.manager.event_handler('server_stop')
def on_server_stop(event):
	print "\nServer going down."
	org.cxsbs.core.events.manager.trigger_event('server_shutdown')
	pyTensible.plugin_loader.unload_all()
	
@org.cxsbs.core.events.manager.event_handler('server_reload')
def on_server_reload(event):
	print "Reloading server. Hang on."
	pyTensible.plugin_loader.unload_all()