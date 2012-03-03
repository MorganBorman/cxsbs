import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		Players.update_game_vars_template({'modified_map': False, 'map_crc': 0, 'map_flag_list': None, 'map_item_list': None, 'map_base_list': None})
		
	def unload(self):
		pass
		
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint
Base = declarative_base()
		
import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Game = cxsbs.getResource("Game")
Net = cxsbs.getResource("Net")
Server = cxsbs.getResource("Server")
Commands = cxsbs.getResource("Commands")
Messages = cxsbs.getResource("Messages")
DatabaseManager = cxsbs.getResource("DatabaseManager")
ProcessingThread = cxsbs.getResource("ProcessingThread")

pluginCategory = 'MapCheck'

SettingsManager.addSetting(Setting.BoolSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="spectate_map_modified",
													displayName="Spectate map modified", 
													default=True,
													doc="Whether or not to automatically spectate players with modified maps.",
												))

SettingsManager.addSetting(Setting.BoolSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="update_on_new",
													displayName="Update on new", 
													default=True,
													doc="Whether or not to automatically create new map entries when a previously unplayed map is changed to.",
												))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

SettingsManager.addSetting(Setting.ListSetting	(
													category='Permissions', 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_modified_unspec",
													displayName="Allow groups modified unspec", 
													default=['__master__','__admin__'],
													doc="Groups which are permitted unspectate even with a modified map.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category='Permissions', 
													subcategory=pluginCategory, 
													symbolicName="deny_groups_modified_unspec",
													displayName="Deny groups modified unspec", 
													default=[],
													doc="Groups which are not permitted unspectate even with a modified map.",
												))

groupSettings = SettingsManager.getAccessor(category='Permissions', subcategory=pluginCategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="map_modified", 
						displayName="Map modified", 
						default="${info}${green}${name}${white} has a ${red}modified${white} map", 
						doc="Message to print when a player fails the map crc."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="modified_unspec", 
						displayName="Modified unspectate", 
						default="${warning}You cannot play with a ${red}modified${white} map.", 
						doc="Message to print when a player who has a modified map tries to unspectate."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="map_updated", 
						displayName="Map updated", 
						default="${info}Valid map definition has been ${yellow}updated${white} by ${green}${name}${white}.", 
						doc="Message to print when the valid map definition is updated."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="maps_table_name", 
												displayName="Maps Table name", 
												default="maps",
												doc="Table name for storing the user name reservations."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="item_list_table_name", 
												displayName="Item List Table name", 
												default="maps_item_lists",
												doc="Table name for storing the item types."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="flag_list_table_name", 
												displayName="Flag List Table name", 
												default="maps_flag_lists",
												doc="Table name for storing the flag teams and positions."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="base_list_table_name", 
												displayName="Base List Table name", 
												default="maps_base_lists",
												doc="Table name for storing the base types and positions."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

class Map(Base):
	'''Associates a map CRC with a map name as the required map CRC'''
	__tablename__ = tableSettings["maps_table_name"]
	id = Column(Integer, primary_key=True)
	mapName = Column(String(16), index=True)
	mapCrc = Column(Integer, index=True)
	def __init__(self, mapName, mapCrc):
		self.mapName = mapName
		self.mapCrc = mapCrc
		
class ItemList(Base):
	'''keeps an entry for each item in each mode that has an item list for each map.'''
	__tablename__ = tableSettings["item_list_table_name"]
	mapId = Column(Integer, ForeignKey(tableSettings["maps_table_name"] + '.id'))
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
		
class FlagList(Base):
	'''keeps an entry for each flag in each mode that has an item list for each map.'''
	__tablename__ = tableSettings["flag_list_table_name"]
	mapId = Column(Integer, ForeignKey(tableSettings["maps_table_name"] + '.id'))
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
		
class BaseList(Base):
	'''keeps an entry for each base in each mode that has an item list for each map.'''
	__tablename__ = tableSettings["base_list_table_name"]
	mapId = Column(Integer, ForeignKey(tableSettings["maps_table_name"] + '.id'))
	mode = Column(Integer, index=True)
	id = Column(Integer, index=True)
	ammotype = Column(Integer)
	x = Column(Integer)
	y = Column(Integer)
	z = Column(Integer)
	map = relation(Map, primaryjoin=mapId==Map.id)
	UniqueConstraint('mapId', 'mode', 'id', name='uq_mapid_mode_id')
	__mapper_args__ = {'primary_key':[mapId, mode, id]}
	def __init__(self, mapId, mode, id, ammotype, x, y, z):
		self.mapId = mapId
		self.mode = mode
		self.id = id
		self.ammotype = ammotype
		self.x = x
		self.y = y
		self.z = z

Base.metadata.create_all(DatabaseManager.dbmanager.engine)

def set_valid_map_crc(mapName, crc):
	session = DatabaseManager.dbmanager.session()
	try:
		mapEntry = session.query(Map).filter(Map.mapName==mapName).one()
		mapEntry.mapCrc = crc
		session.add(mapEntry)
		session.commit()
	except NoResultFound:
		mapEntry = Map(mapName, crc)
		session.add(mapEntry)
		session.commit()
	finally:
		session.close()
		
def set_valid_map_items(mapName, gameMode, item_list):
	mapId = get_mapId(mapName)
	
	if mapId == None:
		return
	
	session = DatabaseManager.dbmanager.session()
	try:
		session.query(ItemList).filter(ItemList.mapId==mapId).filter(ItemList.mode==gameMode).delete()
		session.commit()
		
		for id in range(len(item_list)):
			itemEntry = ItemList(mapId, gameMode, id, item_list[id])
			session.add(itemEntry)
		session.commit()
	finally:
		session.close()
	
def set_valid_map_flags(mapName, gameMode, flag_list):
	mapId = get_mapId(mapName)
	
	if mapId == None:
		return
	
	session = DatabaseManager.dbmanager.session()
	try:
		session.query(FlagList).filter(FlagList.mapId==mapId).filter(FlagList.mode==gameMode).delete()
		session.commit()
		
		for id in range(len(flag_list)):
			flagEntry = FlagList(mapId, ServerCore.gameMode(), id, flag_list[id][0], flag_list[id][1], flag_list[id][2], flag_list[id][3])
			session.add(flagEntry)
		session.commit()
	finally:
		session.close()

def set_valid_map_bases(mapName, gameMode, base_list):
	mapId = get_mapId(mapName)
	
	if mapId == None:
		return
	
	session = DatabaseManager.dbmanager.session()
	try:
		session.query(BaseList).filter(BaseList.mapId==mapId).filter(BaseList.mode==gameMode).delete()
		session.commit()
		
		for id in range(len(base_list)):
			baseEntry = BaseList(mapId, gameMode, id, base_list[id][0], base_list[id][1], base_list[id][2], base_list[id][3])
			session.add(baseEntry)
		session.commit()
	finally:
		session.close()

def get_map_crc(mapName):
	session = DatabaseManager.dbmanager.session()
	try:
		mapEntry = session.query(Map).filter(Map.mapName==ServerCore.mapName()).one()
		return mapEntry.mapCrc
	except NoResultFound:
		return None
	finally:
		session.close()

def get_mapId(mapName):
	"Get the mapId if there is a entry for this maps crc. Otherwise return None"
	session = DatabaseManager.dbmanager.session()
	try:
		mapEntry = session.query(Map).filter(Map.mapName==mapName).one()
		return mapEntry.id
	except MultipleResultsFound:
		return None
	except NoResultFound:
		return None
	finally:
		session.close()

def get_item_list(mapName, mode):
	mapId = get_mapId(mapName)
	
	if mapId == None:
		return None
	
	session = DatabaseManager.dbmanager.session()
	try:
		item_list = []
		
		item_results = session.query(ItemList).filter(ItemList.mapId==mapId).filter(ItemList.mode==mode).order_by(ItemList.id.asc()).all()
		for item in item_results:
			item_list.append(item.type)
			
		if len(item_list) == 0:
			return None
			
		return tuple(item_list)
	except NoResultFound:
		return None
	finally:
		session.close()

def get_flag_list(mapName, mode):
	mapId = get_mapId(mapName)
	
	if mapId == None:
		return None
	
	session = DatabaseManager.dbmanager.session()
	try:
		flag_list = []
		
		flag_results = session.query(FlagList).filter(FlagList.mapId==mapId).filter(FlagList.mode==mode).order_by(FlagList.id.asc()).all()
		for flag in flag_results:
			flag_list.append((flag.team, flag.x, flag.y, flag.z))
			
		if len(flag_list) == 0:
			return None
			
		return tuple(flag_list)
	except NoResultFound:
		return None
	finally:
		session.close()

def get_base_list(mapName, mode):
	mapId = get_mapId(mapName)
	
	if mapId == None:
		return None
	
	session = DatabaseManager.dbmanager.session()
	try:
		base_list = []
		
		base_results = session.query(BaseList).filter(BaseList.mapId==mapId).filter(BaseList.mode==mode).order_by(BaseList.id.asc()).all()
		for base in base_results:
			base_list.append((base.ammotype, base.x, base.y, base.z))
			
		if len(base_list) == 0:
			return None
			
		return tuple(base_list)
	except NoResultFound:
		return None
	finally:
		session.close()
		
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
		
@Events.eventHandler('map_changed_pre')
def onMapChangePre():
	global item_list_set, flag_list_set, base_list_set
	
	item_list_set = False
	flag_list_set = False
	base_list_set = False
	
@Events.eventHandler('map_changed')
def onMapChangePre(mapName, gameMode):
	global item_list_set, flag_list_set, base_list_set
	
	if (not item_list_set) and ServerCore.gameMode() in Game.item_modes:
		server_item_list = get_item_list(ServerCore.mapName(), ServerCore.gameMode())
		if server_item_list != None:
			ServerCore.setMapItems(server_item_list)
			item_list_set = True
		
	if (not flag_list_set) and ServerCore.gameMode() in Game.flag_modes:
		server_flag_list = get_flag_list(ServerCore.mapName(), ServerCore.gameMode())
		if server_flag_list != None:
			ServerCore.setMapFlags(server_flag_list)
			flag_list_set = True
			
	if (not base_list_set) and ServerCore.gameMode() in Game.capture_modes:
		server_base_list = get_base_list(ServerCore.mapName(), ServerCore.gameMode())
		if server_base_list != None:
			ServerCore.setMapBases(server_base_list)
			base_list_set = True

def mapModified(p):
	if not p.isInvisible():
		messager.sendMessage('map_modified', dictionary={'name':p.name()})
	p.logAction("modified map")
	p.gamevars['modified_map'] = True
	if not onUnspectate(p.cn, p.cn):
		p.spectate()

@Events.eventHandler('player_checkmaps')
def onMapCheck(cn):
	'''
	@threaded
	@commandtype
	@allowGroups __all__
	@denyGroups
	@doc Loops through all the players and prints a message for those who have modified maps.
	'''
	mapName = ServerCore.mapName()
	gameMode = ServerCore.gameMode()
	
	mapCrc = get_map_crc(mapName)
	
	if mapCrc != None:
		#we only need to do any of the stuff below if there is an entry for this map crc
		
		if gameMode in Game.item_modes:
			item_list = get_item_list(mapName, gameMode)
		else:
			item_list = None
		
		if gameMode in Game.flag_modes:
			flag_list = get_flag_list(mapName, gameMode)
		else:
			flag_list = None
			
		if gameMode in Game.capture_modes:
			base_list = get_base_list(mapName, gameMode)
		else:
			base_list = None
	
		for p in Players.all():
			if p.mapCrc() != mapEntry.mapCrc:
				mapModified(p)
				continue
			
			if p.gamevars['map_item_list'] != item_list:
				mapModified(p)
				continue
			
			if p.gamevars['map_flag_list'] != flag_list:
				mapModified(p)
				continue
			
			if not compare_base_lists(base_list, p.gamevars['map_base_list']):
				mapModified(p)
				continue

@Commands.commandHandler('setvalidmap')
def onSetValidMap(cn, args):
	'''
	@threaded
	@description Set your map crc as the valid map crc
	@usage
	@allowGroups __admin__
	@denyGroups
	@doc Command type event which is called when a client types \"/#setvalidmap\" and which stores that player's map crc in the maps table.
	'''
	mapName = ServerCore.mapName()
	gameMode = ServerCore.gameMode()
	
	p = Players.player(cn)	
	if p.mapCrc() != 0:
		set_valid_map_crc(mapName, p.mapCrc())
	if p.gamevars['map_item_list'] != None:
		set_valid_map_items(mapName, gameMode, p.gamevars['map_item_list'])
	if p.gamevars['map_flag_list'] != None:
		set_valid_map_flags(mapName, gameMode, p.gamevars['map_flag_list'])
	if p.gamevars['map_base_list'] != None:
		set_valid_map_bases(mapName, gameMode, p.gamevars['map_base_list'])
	messager.sendPlayerMessage('map_updated', p, dictionary={'name':p.name()})
	
@Events.eventHandler('player_map_crc')
def on_map_crc(cn, crc):
	p = Players.player(cn)
	
	if (ServerCore.mapName() != p.mapName()):
		if not p.gamevars['modified_map']:
			mapModified(p)
		return
	
	mapCrc = get_map_crc(ServerCore.mapName())
	if mapCrc != None:
		if p.mapCrc() != mapCrc:
			if not p.gamevars['modified_map']:
				mapModified(p)
	else:
		if settings['update_on_new']:
			set_valid_map_crc(ServerCore.mapName(), p.mapCrc())
	
@Events.eventHandler('player_item_list')
def on_item_list(cn, item_list):
	'''
	@threaded
	@doc Occurs when player receives map change and there are items in the mode.
	'''
	global item_list_set
	
	p = Players.player(cn)
	
	#store the item_list for future reference
	if item_list != ():
		p.gamevars['map_item_list'] = item_list
	else:
		return
	
	#bail on further checks if the map name doesn't match
	if (ServerCore.mapName() != p.mapName()):
		if not p.gamevars['modified_map']:
			mapModified(p)
	
	server_item_list = get_item_list(ServerCore.mapName(), ServerCore.gameMode())
	
	if server_item_list != None: 
		if server_item_list != item_list:
			if not p.gamevars['modified_map']:
				mapModified(p)
	else:
		#and finally update the server copy if settings say we should do so
		if settings['update_on_new']:
			mapId = get_mapId(ServerCore.mapName())
			
			#actually set the item list
			ServerCore.setMapItems(item_list)
			item_list_set = True
			
			if mapId != None:
				set_valid_map_items(ServerCore.mapName(), ServerCore.gameMode(), item_list)

@Events.eventHandler('player_flag_list')
def on_flag_list(cn, flag_list):
	'''
	@threaded
	@doc Occurs when player receives map change and there are flags in the mode.
	'''
	global flag_list_set
	
	p = Players.player(cn)
	
	#store the flag_list for future reference
	p.gamevars['map_flag_list'] = flag_list
	
	#bail on further checks if the map name doesn't match
	if (ServerCore.mapName() != p.mapName()):
		if not p.gamevars['modified_map']:
			mapModified(p)
	
	server_flag_list = get_flag_list(ServerCore.mapName(), ServerCore.gameMode())
	
	if server_flag_list != None: 
		if server_flag_list != flag_list:
			if not p.gamevars['modified_map']:
				mapModified(p)
	else:
		if settings['update_on_new']:
			mapId = get_mapId(ServerCore.mapName())
			
			#actually set the item list
			ServerCore.setMapFlags(flag_list)
			flag_list_set = True
			
			if mapId != None:
				set_valid_map_flags(ServerCore.mapName(), ServerCore.gameMode(), flag_list)

@Events.eventHandler('player_base_list')
def on_base_list(cn, base_list):
	'''
	@threaded
	@doc Occurs when player receives map change and there are bases in the mode.
	'''
	
	global base_list_set
	
	p = Players.player(cn)
	
	#store the flag_list for future reference
	p.gamevars['map_base_list'] = base_list
	
	#bail on further checks if the map name doesn't match
	if (ServerCore.mapName() != p.mapName()):
		if not p.gamevars['modified_map']:
			mapModified(p)
	
	server_base_list = get_base_list(ServerCore.mapName(), ServerCore.gameMode())
	
	if server_base_list != None: 
		if not compare_base_lists(server_base_list, p.gamevars['map_base_list']):
			if not p.gamevars['modified_map']:
				mapModified(p)
	else:
		#and finally update the server copy if settings say we should do so
		if settings['update_on_new']:
			mapId = get_mapId(ServerCore.mapName())
			
			#actually set the item list
			ServerCore.setMapBases(base_list)
			base_list_set = True
			
			if mapId != None:
				set_valid_map_bases(ServerCore.mapName(), ServerCore.gameMode(), base_list)

@Events.policyHandler('player_unspectate')
def onUnspectate(cn, tcn):
	if not settings["spectate_map_modified"]:
		return True
		
	p = Players.player(cn)
	try:
		if not p.gamevars['modified_map']:
			return True
	except KeyError:
		return True
		
	if p.isPermitted(groupSettings["allow_groups_modified_unspec"], groupSettings["deny_groups_modified_unspec"]):
		return True
		
	if cn == tcn:
		messager.sendPlayerMessage('modified_unspec', p)
		
	return False
