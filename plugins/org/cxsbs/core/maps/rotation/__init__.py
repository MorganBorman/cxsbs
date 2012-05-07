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
		
@org.cxsbs.core.commands.handler("nextmatch")
def on_nextmatch(client, map_name=None, mode_name=None):
	"""
	@usage #nextmatch [<map> [<mode>]]
	@description View or set the next map mode.
	$execute __all__
	$setmap 
	$setmode 
	@doc When no arguments are specified this command prints the next map and mode.
	If the first argument is given then the next map is set as indicated and the mode remains the same.
	If the first and second arguments are given then the map and mode are set.
	
	Note: This functionality co-exists with the normal rotation but supersedes anything which is in the match queue. 
	When there is no-longer a next map set the server will go back to processing the match queue.
	the server will continue in it's normal rotation for whichever mode it was left in.
	"""
	if map_name is not None:
		if not client.isActionPermitted("org.cxsbs.core.maps.rotation.nextmatch_setmap"):
			raise Exception()
		
		if mode_name is not None:
			if not client.isActionPermitted("org.cxsbs.core.maps.rotation.nextmatch_setmode"):
				raise Exception()
			
			pass
			#set the map and mode
			
		else:
			pass
			#just set the map
	else:
		pass
		#print the next match
		client.message("The next match is...")
		
@org.cxsbs.core.commands.handler("queuematch")
def on_queuematch(client, map_name=None, mode_name=None):
	"""
	@usage #queuematch [<map> [<mode>]]
	@description View or add a match to the match queue.
	$execute __all__
	$setmap 
	$setmode 
	@doc When no arguments are specified this command prints the current match queue.
	If the first argument is given then a new match is added to the queue with the specified map and the current mode.
	If the first and second arguments is given then a new match is added to the queue with the specified map and mode.
	
	Note: This functionality co-exists with the normal rotation. The next match is taken from the match queue when
	there is no next match set. This continues until there are no more matches in the queue.
	At which time the server continues in it's normal map rotation for whichever mode it is in.
	"""
	if map_name is not None:
		if not client.isActionPermitted("org.cxsbs.core.maps.rotation.queuematch_setmap"):
			raise org.cxsbs.core.commands.InsufficientPermissions()
		
		if mode_name is not None:
			if not client.isActionPermitted("org.cxsbs.core.maps.rotation.queuematch_setmode"):
				raise org.cxsbs.core.commands.InsufficientPermissions()
			
			pass
			#set the map and mode
			
		else:
			pass
			#just set the map
	else:
		pass
		#print the next map
		client.message("The current state of the match queue is: blah blah blah")

