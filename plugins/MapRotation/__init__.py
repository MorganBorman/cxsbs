from cxsbs.Plugin import Plugin

class MapRotation(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass

import cxsbs
Config = cxsbs.getResource("Config")
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
MessageFramework = cxsbs.getResource("MessageFramework")

import string
import DefaultMapRotation

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
			messageModule.sendPlayerMessage('nextmap_response', p, dictionary={'mapname':getSuccessor(ServerCore.gameMode(), ServerCore.mapName())})
		except (KeyError, ValueError):
			messageModule.sendPlayerMessage('nextmap_unknown', p)

def onServerStart(*args):
		startMapName = modeMapLists[start_mode][0]
		startModeNumber = Game.modeNumber(start_mode)
		try:
			Game.setMap(startMapName, startModeNumber)
		except Commands.StateError:
			Logging.warning('Start server map set tried to change the map while server was frozen.')

def init():
	global preset_rotation, start_mode, nextmap_response, modeMapLists
	config = Config.PluginConfig('MapRotation')
	preset_rotation = config.getBoolOption('Config', 'use_preset_rotation', True)
	start_mode = config.getOption('Config', 'start_mode', 'ffa')
	newmap_on_empty = config.getBoolOption('Config', 'newmap_on_empty', True)
	modeMapLists = {}
	
	modeMapLists["hold"] = config.getOption('Map Rotation', 'hold', DefaultMapRotation.hold).split()
	modeMapLists["instahold"] = config.getOption('Map Rotation', 'instahold', DefaultMapRotation.instahold).split()
	modeMapLists["effichold"] = config.getOption('Map Rotation', 'effichold', DefaultMapRotation.effichold).split()
	modeMapLists["capture"] = config.getOption('Map Rotation', 'capture', DefaultMapRotation.capture).split()
	modeMapLists["regencapture"] = config.getOption('Map Rotation', 'regencapture', DefaultMapRotation.regencapture).split()
	modeMapLists["ctf"] = config.getOption('Map Rotation', 'ctf', DefaultMapRotation.ctf).split()
	modeMapLists["instactf"] = config.getOption('Map Rotation', 'instactf', DefaultMapRotation.instactf).split()
	modeMapLists["efficctf"] = config.getOption('Map Rotation', 'efficctf', DefaultMapRotation.efficctf).split()
	modeMapLists["coop"] = config.getOption('Map Rotation', 'coop', DefaultMapRotation.coop).split()
	modeMapLists["protect"] = config.getOption('Map Rotation', 'protect', DefaultMapRotation.protect).split()
	modeMapLists["instaprotect"] = config.getOption('Map Rotation', 'instaprotect', DefaultMapRotation.instaprotect).split()
	modeMapLists["efficprotect"] = config.getOption('Map Rotation', 'efficprotect', DefaultMapRotation.efficprotect).split()
	modeMapLists["tacteam"] = config.getOption('Map Rotation', 'tacteam', DefaultMapRotation.tacteam).split()
	modeMapLists["tac"] = config.getOption('Map Rotation', 'tac', DefaultMapRotation.tac).split()
	modeMapLists["insta"] = config.getOption('Map Rotation', 'insta', DefaultMapRotation.insta).split()
	modeMapLists["effic"] = config.getOption('Map Rotation', 'effic', DefaultMapRotation.effic).split()
	modeMapLists["ffa"] = config.getOption('Map Rotation', 'ffa', DefaultMapRotation.ffa).split()
	modeMapLists["efficteam"] = config.getOption('Map Rotation', 'efficteam', DefaultMapRotation.efficteam).split()
	modeMapLists["instateam"] = config.getOption('Map Rotation', 'instateam', DefaultMapRotation.instateam).split()
	modeMapLists["teamplay"] = config.getOption('Map Rotation', 'teamplay', DefaultMapRotation.teamplay).split()
	modeMapLists["demo"] = config.getOption('Map Rotation', 'demo', DefaultMapRotation.demo).split()
	
	del config
	
	global allRotationMaps
	allRotationMaps = []
	for mapNames in modeMapLists.values():
		for mapName in mapNames:
			if not mapName in allRotationMaps:
				allRotationMaps.append(mapName)
	
	global messageModule
	messageModule = MessageFramework.MessagingModule()
	messageModule.addMessage('nextmap_response', '${info}The next map is ${blue}${mapname}${white}.', "MapRotation")
	messageModule.addMessage('nextmap_unknown', '${info}Could not determine next map in rotation.', "MapRotation")
	messageModule.finalize()
	
	if preset_rotation:
		Events.registerServerEventHandler('intermission_ended', presetRotate)
		Events.registerServerEventHandler('server_start', onServerStart)
		
		if newmap_on_empty:
			Events.registerServerEventHandler('no_clients', presetRotate)
		
		Commands.registerCommandHandler('nextmap', onNextMapCmd)
	else:
		Events.registerServerEventHandler('intermission_ended', presetRotate)
		#Events.registerServerEventHandler('intermission_ended', onIntermEnd)
