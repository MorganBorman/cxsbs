import pyTensible, org

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

class flags(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		org.cxsbs.core.clients.client_manager.game_vars_template['org.cxsbs.core.maps.flags.list'] = ()
		
		org.cxsbs.core.maps.main.map_ready_manager.register('org.cxsbs.core.maps.flags', org.cxsbs.core.server.constants.flag_modes[:])
		
		Interfaces = {}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
Map = org.cxsbs.core.maps.tables.maps.Map
FlagList = org.cxsbs.core.maps.tables.flags.FlagList

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.main')
	
@org.cxsbs.core.events.manager.event_handler('client_flag_list')
def on_client_flag_list(event):
	'''
	@thread maps
	'''
	cn = event.args[0]
	try:
		client = org.cxsbs.core.clients.get_client(cn)
	except KeyError:
		return
	flag_list = event.args[1]
	
	#store the flag_list for future reference
	if flag_list != ():
		client.gamevars['org.cxsbs.core.maps.flags.list'] = flag_list
	else:
		return
	
	if not org.cxsbs.core.server.state.game_mode in org.cxsbs.core.server.constants.flag_modes:
		return
	
	if (org.cxsbs.core.server.state.map_name != client.map_name):
		org.cxsbs.core.maps.modified.mark(client)
		return
	
	server_flag_list = FlagList.retrieve(org.cxsbs.core.server.state.map_name, org.cxsbs.core.server.state.game_mode)
	
	if server_flag_list != None:
		if server_flag_list != flag_list:
			org.cxsbs.core.maps.modified.mark(client)
	else:
		if not org.cxsbs.core.maps.main.map_ready_manager.pending('org.cxsbs.core.maps.flags'):
			return
		
		#actually set the item list
		org.cxsbs.core.server.state.set_map_flags(flag_list)
		org.cxsbs.core.maps.main.map_ready_manager.ready('org.cxsbs.core.maps.flags')
			
		#and finally update the server copy if settings say we should do so
		if settings['update_on_new']:
			FlagList.update(org.cxsbs.core.server.state.map_name, org.cxsbs.core.server.state.game_mode, flag_list)
			
			
@org.cxsbs.core.events.manager.event_handler('map_changed')
def on_map_changed(event):
	#'''
	#@thread maps
	#'''
	if org.cxsbs.core.server.state.game_mode in org.cxsbs.core.server.constants.flag_modes:
		server_flag_list = FlagList.retrieve(org.cxsbs.core.server.state.map_name, org.cxsbs.core.server.state.game_mode)
		if server_flag_list != None:
			org.cxsbs.core.server.state.set_map_flags(server_flag_list)
			org.cxsbs.core.maps.main.map_ready_manager.ready('org.cxsbs.core.maps.flags')