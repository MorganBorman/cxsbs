import pyTensible, org

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

class items(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		org.cxsbs.core.clients.client_manager.game_vars_template['org.cxsbs.core.maps.items.list'] = ()
		
		org.cxsbs.core.maps.main.map_ready_manager.register('org.cxsbs.core.maps.items', org.cxsbs.core.server.constants.item_modes[:])
		
		Interfaces = {}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.items')
		
@org.cxsbs.core.settings.manager.Setting
def map_items_table_name():
	"""
	@category db_tables
	@display_name Map items table name
	@wbpolicy never
	@doc What should the name of the table which stores the map item lists be called?
	"""
	return "map_items"

Map = org.cxsbs.core.maps.main.Map

class ItemList(org.cxsbs.core.database.Base):
	'''keeps an entry for each item in each mode that has an item list for each map.'''
	__tablename__ = settings["map_items_table_name"]
	mapId = Column(Integer, ForeignKey(Map.id))
	mode = Column(Integer, index=True)
	id = Column(Integer, index=True)
	type = Column(Integer)
	map = relation(Map, primaryjoin=mapId==Map.id)
	UniqueConstraint('mapId', 'mode', 'id', name='uq_mapid_mode_id')
	__mapper_args__ = {'primary_key':[mapId, mode, id]}
	def __init__(self, mapId, mode, id, type):
		self.mapId = mapId
		self.mode = mode
		self.id = id
		self.type = type
		
	@staticmethod
	def update(mapName, gameMode, item_list):
		map_entry = Map.retrieve(mapName)
		
		if map_entry == None:
			return
		
		with org.cxsbs.core.database.Session() as session:
			session.query(ItemList).filter(ItemList.mapId==map_entry.id).filter(ItemList.mode==gameMode).delete()
			session.commit()
			
			for id in range(len(item_list)):
				itemEntry = ItemList(map_entry.id, gameMode, id, item_list[id])
				session.add(itemEntry)
			session.commit()
			
	@staticmethod
	def retrieve(mapName, mode):
		map_entry = Map.retrieve(mapName)
		
		if map_entry == None:
			return
		
		with org.cxsbs.core.database.Session() as session:
			try:
				item_list = []
				
				item_results = session.query(ItemList).filter(ItemList.mapId==map_entry.id).filter(ItemList.mode==mode).order_by(ItemList.id.asc()).all()
				for item in item_results:
					item_list.append(item.type)
					
				if len(item_list) == 0:
					return None
					
				return tuple(item_list)
			except NoResultFound:
				return None
		
org.cxsbs.core.database.initialize_tables()

@org.cxsbs.core.events.manager.event_handler('client_item_list')
def on_client_item_list(event):
	'''
	@thread maps
	'''
	cn = event.args[0]
	try:
		client = org.cxsbs.core.clients.get_client(cn)
	except KeyError:
		return
	item_list = event.args[1]
	
	#store the item_list for future reference
	if item_list != ():
		client.gamevars['org.cxsbs.core.maps.items.list'] = item_list
	else:
		return
	
	if not org.cxsbs.core.server.state.game_mode in org.cxsbs.core.server.constants.item_modes:
		return
	
	if (org.cxsbs.core.server.state.map_name != client.map_name):
		org.cxsbs.core.maps.modified.mark(client)
		return
	
	server_item_list = ItemList.retrieve(org.cxsbs.core.server.state.map_name, org.cxsbs.core.server.state.game_mode)
	
	if server_item_list != None: 
		if server_item_list != item_list:
			org.cxsbs.core.maps.modified.mark(client)
	else:
		if not org.cxsbs.core.maps.main.map_ready_manager.pending('org.cxsbs.core.maps.items'):
			return
		
		#actually set the item list
		org.cxsbs.core.server.state.set_map_items(item_list)
		org.cxsbs.core.maps.main.map_ready_manager.ready('org.cxsbs.core.maps.items')
		
		#and finally update the server copy if settings say we should do so
		if settings['org.cxsbs.core.maps.main.update_on_new']:
			ItemList.update(org.cxsbs.core.server.state.map_name, org.cxsbs.core.server.state.game_mode, item_list)
			
			
@org.cxsbs.core.events.manager.event_handler('map_changed')
def on_map_changed(event):
	#'''
	#@thread maps
	#'''
	if org.cxsbs.core.server.state.game_mode in org.cxsbs.core.server.constants.item_modes:
		server_item_list = ItemList.retrieve(org.cxsbs.core.server.state.map_name, org.cxsbs.core.server.state.game_mode)
		if server_item_list != None:
			org.cxsbs.core.server.state.set_map_items(server_item_list)
			org.cxsbs.core.maps.main.map_ready_manager.ready('org.cxsbs.core.maps.items')
