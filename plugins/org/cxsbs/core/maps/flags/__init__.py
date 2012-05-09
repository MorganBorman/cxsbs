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

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.flags')
		
@org.cxsbs.core.settings.manager.Setting
def map_flags_table_name():
	"""
	@category db_tables
	@display_name Map flags table name
	@wbpolicy never
	@doc What should the name of the table which stores the map flag lists be called?
	"""
	return "map_flags"

Map = org.cxsbs.core.maps.main.Map

class FlagList(org.cxsbs.core.database.Base):
	'''keeps an entry for each flag in each mode that has an item list for each map.'''
	__tablename__ = settings["map_flags_table_name"]
	mapId = Column(Integer, ForeignKey(Map.id))
	mode = Column(Integer, index=True)
	id = Column(Integer, index=True)
	team = Column(Integer)
	x = Column(Integer)
	y = Column(Integer)
	z = Column(Integer)
	map = relation(Map, primaryjoin=mapId==Map.id)
	UniqueConstraint('mapId', 'mode', 'id', name='uq_mapid_mode_id')
	__mapper_args__ = {'primary_key':[mapId, mode, id]}
	def __init__(self, mapId, mode, id, team, x, y, z):
		self.mapId = mapId
		self.mode = mode
		self.id = id
		self.team = team
		self.x = x
		self.y = y
		self.z = z
		
	@staticmethod
	def update(mapName, gameMode, flag_list):
		map_entry = Map.retrieve(mapName)
		
		if map_entry == None:
			return
		
		with org.cxsbs.core.database.Session() as session:
			session.query(FlagList).filter(FlagList.mapId==map_entry.id).filter(FlagList.mode==gameMode).delete()
			session.commit()
			
			for id in range(len(flag_list)):
				flagEntry = FlagList(map_entry.id, org.cxsbs.core.server.state.game_mode, id, flag_list[id][0], flag_list[id][1], flag_list[id][2], flag_list[id][3])
				session.add(flagEntry)
			session.commit()
		
	@staticmethod	
	def retrieve(mapName, mode):
		map_entry = Map.retrieve(mapName)
		
		if map_entry == None:
			return
		
		with org.cxsbs.core.database.Session() as session:
			try:
				flag_list = []
				
				flag_results = session.query(FlagList).filter(FlagList.mapId==map_entry.id).filter(FlagList.mode==mode).order_by(FlagList.id.asc()).all()
				for flag in flag_results:
					flag_list.append((flag.team, flag.x, flag.y, flag.z))
					
				if len(flag_list) == 0:
					return None
					
				return tuple(flag_list)
			except NoResultFound:
				return None
		
org.cxsbs.core.database.initialize_tables()
	
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
		if settings['org.cxsbs.core.maps.main.update_on_new']:
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