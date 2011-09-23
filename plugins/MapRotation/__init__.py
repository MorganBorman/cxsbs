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

import string
import DefaultMapRotation

def onConnect(cn):
	global rotate_on_join
	if rotate_on_join:
		rotate_on_join = False
		ServerCore.setPaused(False)

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
			raise ValueError('Empty maps list for specfied mode')
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
		ServerCore.setMap(map, ServerCore.gameMode())
	if ServerCore.numClients() == 0:
		rotate_on_join[0] = True
		ServerCore.setPaused(True)

def onNextMapCmd(cn, args):
	'''@description Display next map
	   @usage
	   @public'''
	if args != '':
		ServerCore.playerMessage(cn, UI.error('Usage: #nextmap'))
	else:
		try:
			ServerCore.playerMessage(cn, UI.info(nextmap_response.substitute(Colors.colordict, mapname=getSuccessor(ServerCore.gameMode(), ServerCore.mapName()))))
		except (KeyError, ValueError):
			ServerCore.playerMessage(cn, UI.error('Could not determine next map'))


def init():
	config = Config.PluginConfig('MapRotation')
	
	preset_rotation = config.getBoolOption('Config', 'use_preset_rotation', 'yes')
	start_mode = config.getOption('Config', 'start_mode', 'ffa')
	nextmap_response = config.getTemplateOption('Config', 'nextmap_response', 'The next map is ${blue}${mapname}')
	
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
	
	if preset_rotation:
		global rotate_on_join
		rotate_on_join = False
		
		startMapName = modeMapLists[start_mode][0]
		startModeNumber = Game.modeNumber(start_mode)
		
		ServerCore.setMap(startMapName, startModeNumber)
		
		Events.registerServerEventHandler('intermission_ended', presetRotate)
		Events.registerServerEventHandler('player_connect', onConnect)
		
		Commands.registerCommandHandler('nextmap', onNextMapCmd)
	else:
		Events.registerServerEventHandler('intermission_ended', presetRotate)
		#Events.registerServerEventHandler('intermission_ended', onIntermEnd)
