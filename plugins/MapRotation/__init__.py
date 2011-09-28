import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass

import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
Logging = cxsbs.getResource("Logging")
UI = cxsbs.getResource("UI")
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Net = cxsbs.getResource("Net")
Server = cxsbs.getResource("Server")
Commands = cxsbs.getResource("Commands")
Game = cxsbs.getResource("Game")
Messages = cxsbs.getResource("Messages")

import string
import DefaultMapRotation

pluginCategory = 'MapRotation'

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="use_preset_rotation", 
												displayName="Use preset rotation", 
												default=True, 
												doc="Use the preset rotation. If set to False server will ask clients for what the next map is."
											))
SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="start_mode", 
												displayName="Start mode", 
												default="ffa", 
												doc="The start mode."
											))
SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="newmap_on_empty", 
												displayName="New map on empty", 
												default=True, 
												doc="Use a new map when the first player joins again after the server has been empty."
											))

for modeName, rotationParams in DefaultMapRotation.defaultMapModeLists.items():
	mapNames = rotationParams[0].split()
	SettingsManager.addSetting(Setting.ListSetting	(
														category=pluginCategory, 
														subcategory="Rotation", 
														symbolicName=modeName, 
														displayName=rotationParams[1], 
														default=mapNames,
														doc=rotationParams[2]
													))
	
rotationSettings = SettingsManager.getAccessor(category=pluginCategory, subcategory="Rotation")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="nextmap_response", 
						displayName="Next map response", 
						default="${info}The next map is ${blue}${mapname}${white}.", 
						doc="Message to print when user should be informed about what the next map is."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="nextmap_unknown", 
						displayName="Next map unknown", 
						default="${info}Could not determine next map in rotation.", 
						doc="Message to print when the next map in the rotation could not be determined."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

class Map:
	def __init__(self, name, mode):
		self.name = name
		self.mode = mode

def getSuccessor(mode_num, map):
	try:
		maps = modeMapLists[Game.modes[mode_num]]
		if map == '':
			return maps[0]
		else:
			ndx = maps.index(map)
	except ValueError:
		if len(maps) > 0:
			Logging.info('Current map not in rotation list.  Restarting rotation.')
			return maps[0]
		else:
			raise ValueError('Empty maps list for specified mode.')
	try:
	 	return maps[ndx+1]
	except IndexError:
		return maps[0]

def clientReloadRotate():
	Events.triggerServerEvent('reload_map_selection', ())
	ServerCore.sendMapReload()
	
def isRotationMap(mapName):
	for modeName in Game.modes:
		mapNames = rotationSettings[modeName]
		if mapName in mapNames:
			return True
	return False

def presetRotate():
	try:
		map = getSuccessor(ServerCore.gameMode(), ServerCore.mapName())
	except KeyError:
		Logging.warning('No map list specified for current mode.  Defaulting to user-specified rotation.')
		clientReloadRotate()
	except ValueError:
		Logging.info('Maps list for current mode is empty.  Defaulting to user-specified rotation.')
		clientReloadRotate()
	else:
		try:
			Game.setMap(map, ServerCore.gameMode())
		except Commands.StateError:
			Logging.warning('Preset rotation tried to change the map while server was frozen.')

def onNextMapCmd(cn, args):
	'''@description Display next map
	   @usage
	   @allowGroups __all__'''
	if args != '':
		raise Commands.UsageError()
	else:
		p = Players.player(cn)
		try:
			messager.sendPlayerMessage('nextmap_response', p, dictionary={'mapname':getSuccessor(ServerCore.gameMode(), ServerCore.mapName())})
		except (KeyError, ValueError):
			messager.sendPlayerMessage('nextmap_unknown', p)

def onServerStart(*args):
		startMapName = modeMapLists[settings['start_mode']][0]
		startModeNumber = Game.modeNumber(settings['start_mode'])
		try:
			Game.setMap(startMapName, startModeNumber)
		except Commands.StateError:
			Logging.warning('Start server map set tried to change the map while server was frozen.')

if settings['preset_rotation']:
	Events.registerServerEventHandler('intermission_ended', presetRotate)
	Events.registerServerEventHandler('server_start', onServerStart)
	
	if settings['newmap_on_empty']:
		Events.registerServerEventHandler('no_clients', presetRotate)
	
	Commands.registerCommandHandler('nextmap', onNextMapCmd)
else:
	Events.registerServerEventHandler('intermission_ended', presetRotate)
	#Events.registerServerEventHandler('intermission_ended', onIntermEnd)