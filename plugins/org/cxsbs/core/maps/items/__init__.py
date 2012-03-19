import pyTensible, org

class items(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = 	{}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

@org.cxsbs.core.events.manager.event_handler('client_item_list')
def on_client_item_list(event):
	org.cxsbs.core.server.state.set_map_items(event.args[1])