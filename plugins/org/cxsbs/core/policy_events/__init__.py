import pyTensible, org

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
	
	cube2server.clientInitialize(cn)
	
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
			policy_query = org.cxsbs.core.policies.Query('client_can_spectate_other', True, (client, target))
		else:
			policy_query = org.cxsbs.core.policies.Query('client_can_unspectate_other', True, (client, target))
	
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

@org.cxsbs.core.events.manager.event_handler('client_message_pol')
def on_client_message_pol(event):
	'''
	@thread policy_events
	'''
	cn = event.args[0]
	msg = event.args[1]
	
	client = org.cxsbs.core.clients.get_client(cn)
	
	if msg == "#reload":
		cube2server.serverReload()
	elif msg[0] == '#':
		org.cxsbs.core.events.manager.trigger_event('command', (client, msg))
	else:
		#find out whether this client is allowed to talk
		policy_query = org.cxsbs.core.policies.Query('client_can_chat', True, (client, msg))
		response = org.cxsbs.core.policies.query_policy(policy_query)
		if response:
			org.cxsbs.core.chat.message(client, msg)
	
	
	'''
	if event.args[1] == "#reload":
		cube2server.serverReload()
	elif event.args[1] == "#setscore":
		org.cxsbs.core.server.state.teams['good'].score = 8
	elif event.args[1] == "#paused":
		org.cxsbs.core.server.state.paused = True
	elif event.args[1] == "#unpaused":
		org.cxsbs.core.server.state.paused = False
	elif event.args[1] == "#name":
		client = org.cxsbs.core.clients.get_client(event.args[0])
		client.variables['name'] = "foobar"
	elif event.args[1] == "#invisible":
		client = org.cxsbs.core.clients.get_client(event.args[0])
		client.invisible = True
	elif event.args[1] == "#visible":
		client = org.cxsbs.core.clients.get_client(event.args[0])
		client.invisible = False
	'''