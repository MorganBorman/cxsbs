import pyTensible, org

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

class main(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		self.map_ready_manager = MapReadyManager()
		
		Interfaces = {}
		Resources = 	{'Map': Map, 'map_ready_manager': self.map_ready_manager}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.main')

class MapReadyManager(object):
	def __init__(self):
		self.components_template = {}
		self.pending_components = []
		self.already_ready = []
		self.waiting_on_mode = True
	
	def register(self, component, modes):
		self.components_template[component] = modes
		
	def new_game(self, mode):
		self.pending_components = []
		self.waiting_on_mode = False
		
		for component in self.components_template.keys():
			if mode in self.components_template[component]:
				self.pending_components.append(component)
				
		while len(self.already_ready) > 0:
			component = self.already_ready.pop(0)
			self.ready(component)
	
	def ready(self, component):
		if self.waiting_on_mode:
			self.already_ready.append(component)
		else:
			if component in self.pending_components:
				self.pending_components.remove(component)
				
			if len(self.pending_components) == 0:
				org.cxsbs.core.events.manager.trigger_event('map_ready')
			
	def pending(self, component):
		return component in self.pending_components
		
@org.cxsbs.core.settings.manager.Setting
def map_table_name():
	"""
	@category db_tables
	@display_name Maps table name
	@wbpolicy never
	@doc What should the name of the table which stores the map name:crc associations be called?
	"""
	return "maps"
		
@org.cxsbs.core.settings.manager.Setting
def update_on_new():
	"""
	@category map_check
	@display_name Update on new
	@wbpolicy never
	@doc Should map definitions be updated automatically when new maps are encountered?
	"""
	return True
	
class Map(org.cxsbs.core.database.Base):
	'''Associates a map CRC with a map name as the required map CRC'''
	__tablename__ = settings["map_table_name"]
	id = Column(Integer, primary_key=True)
	mapName = Column(String(16), index=True)
	mapCrc = Column(Integer, index=True)
	def __init__(self, mapName, mapCrc):
		self.mapName = mapName
		self.mapCrc = mapCrc
		
	@staticmethod
	def update(map_name, crc):
		with org.cxsbs.core.database.Session() as session:
			try:
				map_entry = session.query(Map).filter(Map.mapName==map_name).one()
				map_entry.mapCrc = crc
				session.add(map_entry)
				session.commit()
			except NoResultFound:
				map_entry = Map(map_name, crc)
				session.add(map_entry)
				session.commit()
				
	@staticmethod
	def retrieve(map_name):
		"Get the map entry for this map_name. Return None if it doesn't exist."
		with org.cxsbs.core.database.Session() as session:
			try:
				return session.query(Map).filter(Map.mapName==map_name).one()
			except NoResultFound:
				return None
		
org.cxsbs.core.database.initialize_tables()

@org.cxsbs.core.events.manager.event_handler('client_map_crc')
def on_client_map_crc(event):
	'''
	@thread maps
	'''
	cn = event.args[0]
	try:
		client = org.cxsbs.core.clients.get_client(cn)
	except KeyError:
		return
	
	if (org.cxsbs.core.server.state.map_name != client.map_name):
		org.cxsbs.core.maps.modified.mark(client)
		return
	
	valid_map_entry = Map.retrieve(org.cxsbs.core.server.state.map_name)
	if valid_map_entry != None:
		if client.map_crc != valid_map_entry.mapCrc:
			org.cxsbs.core.maps.modified.mark(client)
	else:
		if settings['update_on_new'] and not client.map_crc in [0, 1]:
			Map.update(org.cxsbs.core.server.state.map_name, client.map_crc)

@org.cxsbs.core.events.manager.event_handler('map_changed_pre')
def on_map_changed_pre(event):
	#'''
	#@thread maps
	#'''
	org.cxsbs.core.server.state.paused = True
	
@org.cxsbs.core.events.manager.event_handler('map_changed')
def on_map_changed(event):
	#'''
	#@thread maps
	#'''
	org.cxsbs.core.maps.main.map_ready_manager.new_game(event.args[1])
	
@org.cxsbs.core.events.manager.event_handler('map_ready')
def on_map_ready(event):
	#'''
	#@thread main
	#'''
	org.cxsbs.core.server.state.paused = False