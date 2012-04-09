import pyTensible, org
import cube2crypto

class policy_events(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
import cube2server

@org.cxsbs.core.events.manager.event_handler('client_connect_pol')
def on_client_connect_pol(event):
	'''
	@thread policy_events
	'''
	
	cn = event.args[0]
	client = org.cxsbs.core.clients.get_client(cn)
	
	#if the client is banned or the server is in private then we need to wait to initialize
	#until they have had a chance to 
	policy_query = org.cxsbs.core.policies.Query('client_can_connect', True, (client,))
	response = org.cxsbs.core.policies.query_policy(policy_query)
	if not response or org.cxsbs.core.server.state.mastermode == 3:
		#org.cxsbs.core.events.manager.trigger_event('client_map_vote', (client, mapName, modeNum))
		
		filters = 	{
						'client_auth_finished': lambda xevent: xevent.args[0].cn == cn,
					}
		
		@org.cxsbs.core.events.manager.select(filters=filters, timeout=5, thread='policy_events')
		def on_client_auth_finished(event):
			policy_query = org.cxsbs.core.policies.Query('client_can_connect', True, (client,))
			response = org.cxsbs.core.policies.query_policy(policy_query)
			if response:
				post_connect_initialization(client)
	else:
		post_connect_initialization(client)
		
		
def post_connect_initialization(client):
	policy_query = org.cxsbs.core.policies.Query('client_can_unspectate_self', True, (client,))
	response = org.cxsbs.core.policies.query_policy(policy_query)
	
	if response and org.cxsbs.core.server.state.mastermode <= 1:
		join_state = 0
	else:
		join_state = 1
		
	if client.connect_password == cube2crypto.hashstring("%d %d %s" % (client.cn, client.sessionid, 'invisible')):
		policy_query = org.cxsbs.core.policies.Query('client_can_connect_invisible', False, (client,))
		response = org.cxsbs.core.policies.query_policy(policy_query)
		if response:
			join_state = 2
	
	pyTensible.plugin_loader.logger.debug("initializing client cn: %d, join_state: %d" % (client.cn, join_state))
	org.cxsbs.core.threads.queue('main', cube2server.clientInitialize, (client.cn, join_state), {})
	
@org.cxsbs.core.events.manager.event_handler('client_set_spectator_pol')
def on_client_set_spectator_pol(event):
	'''
	@thread policy_events
	'''
	cn = event.args[0]
	who = event.args[1]
	val = event.args[2]
	self = (cn == who)
	
	client = org.cxsbs.core.clients.get_client(cn)
	
	if self:
		target = client
		
		if val:
			policy_query = org.cxsbs.core.policies.Query('client_can_spectate_self', True, (client,))
		else:
			policy_query = org.cxsbs.core.policies.Query('client_can_unspectate_self', True, (client,))
	else:
		target = org.cxsbs.core.clients.get_client(who)
		
		if val:
			policy_query = org.cxsbs.core.policies.Query('client_can_spectate_other', False, (client, target))
		else:
			policy_query = org.cxsbs.core.policies.Query('client_can_unspectate_other', False, (client, target))
	
	response = org.cxsbs.core.policies.query_policy(policy_query)
	
	if response:
		target.spectator = bool(val)
		
@org.cxsbs.core.events.manager.event_handler('client_set_team_pol')
def on_client_set_team_pol(event):
	'''
	@thread policy_events
	'''
	cn = event.args[0]
	who = event.args[1]
	team = event.args[2]
	self = (cn == who)
	
	client = org.cxsbs.core.clients.get_client(cn)
	
	if self:
		target = client
		
		policy_query = org.cxsbs.core.policies.Query('client_can_change_team_self', True, (client, team))
		
	else:
		target = org.cxsbs.core.clients.get_client(who)
		
		policy_query = org.cxsbs.core.policies.Query('client_can_change_team_other', True, (client, target, team))
	
	response = org.cxsbs.core.policies.query_policy(policy_query)
	
	if response:
		target.team = team

@org.cxsbs.core.events.manager.event_handler('client_map_vote_pol')
def on_client_message_pol(event):
	'''
	@thread policy_events
	'''
	cn = event.args[0]
	mapName = event.args[1]
	modeNum = event.args[2]
	
	client = org.cxsbs.core.clients.get_client(cn)
	
	policy_query = org.cxsbs.core.policies.Query('client_can_map_vote', True, (client, mapName, modeNum))
	response = org.cxsbs.core.policies.query_policy(policy_query)
	if response:
		org.cxsbs.core.events.manager.trigger_event('client_map_vote', (client, mapName, modeNum))

@org.cxsbs.core.events.manager.event_handler('client_message_pol')
def on_client_message_pol(event):
	'''
	@thread policy_events
	'''
	cn = event.args[0]
	msg = event.args[1]
	
	client = org.cxsbs.core.clients.get_client(cn)
	
	if msg[0] == '#':
		org.cxsbs.core.events.manager.trigger_event('command', (client, msg))
	else:
		#find out whether this client is allowed to talk
		policy_query = org.cxsbs.core.policies.Query('client_can_chat', True, (client, msg))
		response = org.cxsbs.core.policies.query_policy(policy_query)
		if response:
			org.cxsbs.core.chat.message(client, msg)