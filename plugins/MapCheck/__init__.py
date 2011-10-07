import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
		
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
		
Base = declarative_base()
		
import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Net = cxsbs.getResource("Net")
Server = cxsbs.getResource("Server")
Commands = cxsbs.getResource("Commands")
Messages = cxsbs.getResource("Messages")
DatabaseManager = cxsbs.getResource("DatabaseManager")

pluginCategory = 'MapCheck'

SettingsManager.addSetting(Setting.ListSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="spectate_map_modified",
													displayName="Spectate map modified", 
													default=['__master__','__admin__'],
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
												symbolicName="table_name", 
												displayName="Table name", 
												default="maps",
												doc="Table name for storing the user name reservations."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

class Map(Base):
	'''Associates a map CRC with a map name as the required map CRC'''
	__tablename__ = tableSettings["table_name"]
	id = Column(Integer, primary_key=True)
	mapName = Column(String(16), index=True)
	mapCrc = Column(Integer, index=True)
	def __init__(self, mapName, mapCrc):
		self.mapName = mapName
		self.mapCrc = mapCrc
		
Base.metadata.create_all(DatabaseManager.dbmanager.engine)

def mapModified(p):
	if not p.isInvisible():
		messager.sendPlayerMessage('map_modified', p, dictionary={'name':p.name()})
	p.gamevars['modified_map'] = True
	if not onUnspectate(p.cn, p.cn):
		p.spectate()

@Events.eventHandler('player_checkmaps')
def onMapCheck(cn):
	'''
	@commandType
	@allowGroups __admin__
	@denyGroups
	@doc Command type event which is called when a client types \"/checkmaps\" and which stores that player's map crc in the maps table.
	'''
	p = Players.player(cn)	
	session = DatabaseManager.dbmanager.session()
	try:
		mapEntry = session.query(Map).filter(Map.mapName==ServerCore.mapName()).one()
		mapEntry.mapCrc = p.mapCrc()
		session.add(mapEntry)
		session.commit()
	except NoResultFound:
		mapEntry = Map(ServerCore.mapName(), p.mapCrc())
		session.add(mapEntry)
		session.commit()
	finally:
		session.close()
	messager.sendPlayerMessage('map_updated', p, dictionary={'name':p.name()})

@Events.eventHandler('player_map_crc')
def onMapCrc(cn, crc):
	p = Players.player(cn)
	if (ServerCore.mapName() != p.mapName()):
		mapModified(p)
		return
	session = DatabaseManager.dbmanager.session()
	try:
		mapEntry = session.query(Map).filter(Map.mapName==ServerCore.mapName()).one()
		if crc != mapEntry.mapCrc:
			mapModified(p)
	except NoResultFound:
		if settings['update_on_new']:
			mapEntry = Map(ServerCore.mapName(), crc)
			session.add(mapEntry)
			session.commit()
	finally:
		session.close()

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

@Events.eventHandler('player_active')
def checkModified(cn):
	try:
		p = Players.player(cn)
		if not onUnspectate(cn, cn):
			p.spectate()
	except KeyError:
		pass
	except ValueError:
		pass