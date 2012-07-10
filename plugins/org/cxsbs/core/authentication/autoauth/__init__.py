import pyTensible, org

class autoauth(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

@org.cxsbs.core.events.manager.event_handler('client_init')
def on_client_init(event):
	cn = event.args[0]
	client = org.cxsbs.core.clients.get_client(cn)
	client.requestAuth("local."+org.cxsbs.core.server.instance.domain)