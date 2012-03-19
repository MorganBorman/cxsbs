import pyTensible, org

class bases(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = 	{}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

@org.cxsbs.core.events.manager.event_handler('client_base_list')
def on_client_item_list(event):
	org.cxsbs.core.server.state.set_map_bases(event.args[1])