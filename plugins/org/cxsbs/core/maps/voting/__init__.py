import pyTensible, org

class voting(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = 	{}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
import cube2server

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.voting')

@org.cxsbs.core.settings.manager.Setting
def immediate_change_vote_threshold():
	"""
	@category map_voting
	@display_name Immediate map change vote threshold
	@wbpolicy immediate
	@doc This is the fractional portion of the voting population of the server which must have voted for a map to get 
		 the map to change in the middle of the match.
	"""
	return 0.5

@org.cxsbs.core.settings.manager.Setting
def next_map_vote_threshold():
	"""
	@category map_voting
	@display_name Next map vote threshold
	@wbpolicy immediate
	@doc This is the portion of the voting population of the server which must vote for a map to set it as the next map.
	"""
	return 0.5

@org.cxsbs.core.events.manager.event_handler('client_map_vote')
def on_client_map_vote(event):
	cube2server.serverSetMapMode(event.args[1], event.args[2])