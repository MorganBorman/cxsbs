import pyTensible, org

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint

class main(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = 	{'Map': Map}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.main')
		
@org.cxsbs.core.settings.manager.Setting
def maps_table_name():
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
	__tablename__ = settings["maps_table_name"]
	id = Column(Integer, primary_key=True)
	name = Column(String(16), index=True)
	crc = Column(Integer, index=True)
	
	def __init__(self, name, crc):
		self.name = name
		self.crc = crc
		
org.cxsbs.core.database.initialize_tables()

@org.cxsbs.core.events.manager.event_handler('client_map_crc')
def on_client_map_crc(event):
	'''
	@thread maps
	'''
	cn = event.args[0]
	client = org.cxsbs.core.clients.get_client(cn)
	
	if (org.cxsbs.core.server.state.map_name != client.map_name):
		org.cxsbs.core.maps.modified.mark(client)
		return
	
	valid_crc = get_valid_map_crc(org.cxsbs.core.server.state.map_name)
	if valid_crc != None:
		if client.map_crc != valid_crc:
			org.cxsbs.core.maps.modified.mark(client)
	else:
		if settings['update_on_new'] and client.map_crc > 0:
			update_valid_map_crc(org.cxsbs.core.server.state.map_name, client.map_crc)

def update_valid_map_crc(map_name, crc):
	with org.cxsbs.core.database.Session() as session:
		try:
			map_entry = session.query(Map).filter(Map.name==name).one()
			map_entry.crc = crc
			session.add(map_entry)
			session.commit()
		except NoResultFound:
			map_entry = Map(map_name, crc)
			session.add(map_entry)
			session.commit()
			
def get_valid_map_crc(map_name):
	with org.cxsbs.core.database.Session() as session:
		try:
			map_entry = session.query(Map).filter(Map.name==map_name).one()
			return map_entry.crc
		except NoResultFound:
			return None
		
		