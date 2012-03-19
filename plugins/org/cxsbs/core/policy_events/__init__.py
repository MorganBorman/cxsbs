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
	cube2server.clientInitialize(event.args[0])
	
@org.cxsbs.core.events.manager.event_handler('client_spectate_pol')
def on_client_spectate_pol(event):
	cube2server.clientSetSpectator(event.args[1], event.args[2])

@org.cxsbs.core.events.manager.event_handler('client_auth_timout')
def on_client_auth_timout(event):
	pass

@org.cxsbs.core.events.manager.event_handler('client_auth_challenge_response')
def on_client_auth_challenge_response(event):
	pass

@org.cxsbs.core.events.manager.event_handler('client_message_pol')
def on_client_message_pol(event):
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
	