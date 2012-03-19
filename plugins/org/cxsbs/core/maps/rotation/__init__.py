import pyTensible, org

class rotation(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = 	{}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
import cube2server

@org.cxsbs.core.events.manager.event_handler('client_connect_pre')
def on_client_connect_pre(event):
	pass