from cxsbs.Plugin import Plugin

class SetMap(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		deinit()
		
import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
MessageFramework = cxsbs.getResource("MessageFramework")
Events = cxsbs.getResource("Events")
MapRotation = cxsbs.getResource("MapRotation")
Game = cxsbs.getResource("Game")
Logging = cxsbs.getResource("Logging")
Commands = cxsbs.getResource("Commands")
Config = cxsbs.getResource("Config")
Players = cxsbs.getResource("Players")
Timers = cxsbs.getResource("Timers")

def isPermitted(playerGroups, allowGroups, denyGroups):
	permitted = False
	for group in playerGroups:
		if group in denyGroups:
			return False
		if group in allowGroups:
			permitted = True
	return permitted

def whenSetMap(p, startMapName, startModeNumber):
		try:
			Game.setMap(startMapName, startModeNumber)
			messageModule.sendMessage('map_changed', dictionary={'name': p.name()})
		except Commands.StateError:
			Logging.warning('Start server map set tried to change the map while server was frozen.')
		
def init():	
	global allow_groups_change_map, deny_groups_change_map, allow_groups_change_mode, deny_groups_change_mode
	global allow_groups_transcend_rotation, deny_groups_transcend_rotation, allow_groups_change_without_veto, deny_groups_change_without_veto
	config = Config.PluginConfig('Permissions')
	allow_groups_change_map = config.getOption('SetMap', 'allow_groups_change_map', '__master__ __admin__')
	deny_groups_change_map =  config.getOption('SetMap', 'deny_groups_change_map', '')
	
	allow_groups_change_mode = config.getOption('SetMap', 'allow_groups_change_mode', '__master__ __admin__')
	deny_groups_change_mode =  config.getOption('SetMap', 'deny_groups_change_mode', '')
	
	allow_groups_transcend_rotation = config.getOption('SetMap', 'allow_groups_transcend_rotation', '__admin__')
	deny_groups_transcend_rotation =  config.getOption('SetMap', 'deny_groups_transcend_rotation', '')
	
	allow_groups_change_without_veto = config.getOption('SetMap', 'allow_groups_change_without_veto', '__admin__')
	deny_groups_change_without_veto =  config.getOption('SetMap', 'deny_groups_change_without_veto', '')
	del config
	
	config = Config.PluginConfig('SetMap')
	map_change_delay = config.getIntOption('Config', 'map_change_delay', 5)
	del config
	
	global messageModule
	messageModule = MessageFramework.MessagingModule()
	messageModule.addMessage('denied_change_map', '${denied}You are not permitted to change the map.', "SetMap")
	messageModule.addMessage('denied_change_mode', '${denied}You are not permitted to change the mode.', "SetMap")
	messageModule.addMessage('denied_transcend_rotation', '${denied}You are not permitted to transcend the rotation.', "SetMap")
	messageModule.addMessage('denied_change_on_open', '${denied}You are not permitted to change the map on open mastermode.', "SetMap")
	messageModule.addMessage('map_changing', '${info}Map will change to ${map}/${mode} in ${time} seconds.', "SetMap")
	messageModule.addMessage('map_changed', '${info}${green}${name}${white} changed the map.', 'SetMap')
	messageModule.finalize()

	@Events.eventHandler('player_map_vote')
	def onMapVote(cn, mapname, mapmode):
		p = Players.player(cn)
		
		playerGroups = p.groups()
		
		#check if players group can actually change map at all
		if not isPermitted(playerGroups, allow_groups_change_map, deny_groups_change_map):
			messageModule.sendPlayerMessage('denied_change_map', p)
			return
		
		if mapmode != ServerCore.gameMode():
			#check whether players group can change mode
			if not isPermitted(playerGroups, allow_groups_change_mode, deny_groups_change_mode):
				messageModule.sendPlayerMessage('denied_change_mode', p)
				return
		
			if not mapname in MapRotation.allRotationMaps:
				#check whether players group can transcend rotation
				if not isPermitted(playerGroups, allow_groups_transcend_rotation, deny_groups_transcend_rotation):
					messageModule.sendPlayerMessage('denied_transcend_rotation', p)
					return
		else:
			if not mapname in MapRotation.modeMapLists[Game.modes[mapmode]]:
				#check whether players group can transcend rotation
				if not isPermitted(playerGroups, allow_groups_transcend_rotation, deny_groups_transcend_rotation):
					messageModule.sendPlayerMessage('denied_transcend_rotation', p)
					return
		
		if not ServerCore.masterMode() > 0:
			#check whether players group can change mode
			if not isPermitted(playerGroups, allow_groups_change_without_veto, deny_groups_change_without_veto):
				messageModule.sendPlayerMessage('denied_change_on_open', p)
				return
		
		if not map_change_delay <= 0:
			messageModule.sendMessage('map_changing', dictionary={'map': mapname, 'mode': Game.modes[mapmode], 'time': map_change_delay})
			Timers.addTimer(map_change_delay*1000, whenSetMap, (p, mapname, mapmode))
		else:
			whenSetMap(p, mapname, mapmode)

def deinit():
	pass