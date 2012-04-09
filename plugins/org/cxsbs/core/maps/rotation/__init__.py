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

@org.cxsbs.core.settings.manager.Setting
def use_custom_rotation():
	"""
	@category map_rotation
	@display_name Use custom rotation
	@wbpolicy never
	@doc If True then use the custom map rotation, else ask the clients at the end of each map what the next should be.
	"""
	return False

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.rotation')

@org.cxsbs.core.events.manager.event_handler('client_connect')
def on_client_connect(event):
	'''
	@thread maps
	'''
	pass
	#print "Client states:", org.cxsbs.core.server.state.client_states

@org.cxsbs.core.events.manager.event_handler('client_unspectated')
def on_client_unspectated(event):
	'''
	@thread maps
	'''
	#if org.cxsbs.core.server.state.map_name == "" and org.cxsbs.core.server.state.client_count == 1:
	#	print org.cxsbs.core.server.state.client_states
	#	client = org.cxsbs.core.clients.get_client(event.args[0])
	#	
	#	if len(client.gamevars['org.cxsbs.core.maps.vote']) == 2:
	#		cube2server.serverSetMapMode(*client.gamevars['org.cxsbs.core.maps.vote'])
			
@org.cxsbs.core.events.manager.event_handler('intermission_ended')
def on_intermission_ended(event):
	'''
	@thread maps
	'''
	if settings['use_custom_rotation']:
		raise NotImplementedError()
	else:
		org.cxsbs.core.server.state.send_map_reload()
		
		