import pyTensible, org

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

class bases(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		org.cxsbs.core.clients.client_manager.game_vars_template['org.cxsbs.core.maps.bases.list'] = ()
		
		org.cxsbs.core.maps.main.map_ready_manager.register('org.cxsbs.core.maps.bases', org.cxsbs.core.server.constants.base_modes[:])
		
		Interfaces = {}
		Resources = 	{}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

Map = org.cxsbs.core.maps.tables.maps.Map
BaseList = org.cxsbs.core.maps.tables.bases.BaseList

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.main')

def compare_base_lists(server_base_list, client_base_list):
	"returns True if they are functionally the same and False otherwise"
	if len(server_base_list) != len(client_base_list):
		return False
	
	for i in range(len(server_base_list)):
		server_base = server_base_list[i]
		client_base = client_base_list[i]
		
		if server_base[0] != 0:
			if server_base[0] != client_base[0]:
				return False
			
		for j in range(1, 4):
			if server_base[j] != client_base[j]:
				return False
			
	return True

@org.cxsbs.core.events.manager.event_handler('client_base_list')
def on_client_base_list(event):
	'''
	@thread maps
	'''
	cn = event.args[0]
	try:
		client = org.cxsbs.core.clients.get_client(cn)
	except KeyError:
		return
	base_list = event.args[1]
	
	#store the base_list for future reference
	if base_list != ():
		client.gamevars['org.cxsbs.core.maps.bases.list'] = base_list
	else:
		return
	
	if not org.cxsbs.core.server.state.game_mode in org.cxsbs.core.server.constants.base_modes:
		return
	
	if (org.cxsbs.core.server.state.map_name != client.map_name):
		org.cxsbs.core.maps.modified.mark(client)
		return
	
	server_base_list = BaseList.retrieve(org.cxsbs.core.server.state.map_name, org.cxsbs.core.server.state.game_mode)
	
	if server_base_list != None: 
		if not compare_base_lists(server_base_list, base_list):
			org.cxsbs.core.maps.modified.mark(client)
	else:
		if not org.cxsbs.core.maps.main.map_ready_manager.pending('org.cxsbs.core.maps.bases'):
			return
		
		#actually set the item list
		org.cxsbs.core.server.state.set_map_bases(base_list)
		org.cxsbs.core.maps.main.map_ready_manager.ready('org.cxsbs.core.maps.bases')
		
		#and finally update the server copy if settings say we should do so
		if settings['update_on_new']:
			BaseList.update(org.cxsbs.core.server.state.map_name, org.cxsbs.core.server.state.game_mode, base_list)
			
			
@org.cxsbs.core.events.manager.event_handler('map_changed')
def on_map_changed(event):
	#'''
	#@thread maps
	#'''
	if org.cxsbs.core.server.state.game_mode in org.cxsbs.core.server.constants.base_modes:
		server_base_list = BaseList.retrieve(org.cxsbs.core.server.state.map_name, org.cxsbs.core.server.state.game_mode)
		if server_base_list != None:
			org.cxsbs.core.server.state.set_map_bases(server_base_list)
			org.cxsbs.core.maps.main.map_ready_manager.ready('org.cxsbs.core.maps.bases')