import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
		
import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
Messages = cxsbs.getResource("Messages")
Events = cxsbs.getResource("Events")
MapRotation = cxsbs.getResource("MapRotation")
Game = cxsbs.getResource("Game")
Logging = cxsbs.getResource("Logging")
Commands = cxsbs.getResource("Commands")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Players = cxsbs.getResource("Players")
Timers = cxsbs.getResource("Timers")

permissionsCategory = 'Permissions'
pluginSubcategory = 'SetMap'

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_change_map",
													displayName="Allow groups change map", 
													default=['__master__','__admin__'],
													doc="Groups which are permitted to change the map.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_change_map",
													displayName="Deny groups change map", 
													default=[],
													doc="Groups which are not permitted to change the map.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_change_mode",
													displayName="Allow groups change mode", 
													default=['__master__','__admin__'],
													doc="Groups which are permitted to change the mode.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_change_mode",
													displayName="Deny groups change mode", 
													default=[],
													doc="Groups which are not permitted to change the mode.",
												))
	
SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_transcend_rotation",
													displayName="Allow groups transcend rotation", 
													default=['__admin__'],
													doc="Groups which are permitted to change the map to one which is not in the rotation.\n\
													Note this is dependent on whether or not they are allowed to change the mode.\n\
													If not, then this only checks those maps that are in the current mode's rotation.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_transcend_rotation",
													displayName="Deny groups transcend rotation", 
													default=[],
													doc="Groups which are not permitted to change the map to one which is not in the rotation.\n\
													Note this is dependent on whether or not they are allowed to change the mode.\n\
													If not, then this only checks those maps that are in the current mode's rotation.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_change_without_veto",
													displayName="Allow groups change without veto", 
													default=['__admin__'],
													doc="Groups which are permitted change the map and/or mode without the mastermode being veto or higher.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_change_without_veto",
													displayName="Deny groups change without veto", 
													default=[],
													doc="Groups which are not permitted change the map and/or mode unless the mastermode is veto or higher.",
												))

groupSettings = SettingsManager.getAccessor(category=permissionsCategory, subcategory=pluginSubcategory)

pluginCategory="SetMap"

SettingsManager.addSetting(Setting.IntSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="map_change_delay",
													displayName="Map change delay", 
													default=5,
													doc="Number of seconds to wait after a command changing the map has been issued before actually changing.",
												))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="denied_change_map", 
						displayName="Denied change map", 
						default="${denied}You are not permitted to change the map.", 
						doc="Message to print when the user does not have permissions to change the map."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="denied_transcend_rotation", 
						displayName="Denied transcend rotation", 
						default="${denied}You are not permitted to transcend the rotation.", 
						doc="Message to print when"
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="denied_change_on_open", 
						displayName="Denied change on open", 
						default="${denied}You are not permitted to change the map on open mastermode.", 
						doc="Message to print when the user does not have permissions to change the mastermode."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="map_changing", 
						displayName="Map changing", 
						default="${info}Map will change to ${map}/${mode} in ${time} seconds.", 
						doc="Message to print when a map change is imminent."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="map_changed", 
						displayName="map_changed", 
						default="${info}${green}${name}${white} changed the map.", 
						doc="Message to print when the map has been changed."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

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
			messager.sendMessage('map_changed', dictionary={'name': p.name()})
		except Commands.StateError:
			Logging.warning('Start server map set tried to change the map while server was frozen.')
	
@Events.eventHandler('player_map_vote')
def onMapVote(cn, mapname, mapmode):
	p = Players.player(cn)
	
	playerGroups = p.groups()
	
	#check if players group can actually change map at all
	if not isPermitted(playerGroups, groupSettings["allow_groups_change_map"], groupSettings["deny_groups_change_map"]):
		messager.sendPlayerMessage('denied_change_map', p)
		return
	
	if mapmode != ServerCore.gameMode():
		#check whether players group can change mode
		if not isPermitted(playerGroups, groupSettings["allow_groups_change_mode"], groupSettings["deny_groups_change_mode"]):
			messager.sendPlayerMessage('denied_change_mode', p)
			return
	
		if not mapname in MapRotation.allRotationMaps:
			#check whether players group can transcend rotation
			if not isPermitted(playerGroups, groupSettings["allow_groups_transcend_rotation"], groupSettings["deny_groups_transcend_rotation"]):
				messager.sendPlayerMessage('denied_transcend_rotation', p)
				return
	else:
		if not mapname in MapRotation.modeMapLists[Game.modes[mapmode]]:
			#check whether players group can transcend rotation
			if not isPermitted(playerGroups, groupSettings["allow_groups_transcend_rotation"], groupSettings["deny_groups_transcend_rotation"]):
				messager.sendPlayerMessage('denied_transcend_rotation', p)
				return
	
	if not ServerCore.masterMode() > 0:
		#check whether players group can change mode
		if not isPermitted(playerGroups, groupSettings["allow_groups_change_without_veto"], groupSettings["deny_groups_change_without_veto"]):
			messager.sendPlayerMessage('denied_change_on_open', p)
			return
	
	if not settings["map_change_delay"] <= 0:
		messager.sendMessage('map_changing', dictionary={'map': mapname, 'mode': Game.modes[mapmode], 'time': settings["map_change_delay"]})
		Timers.addTimer(settings["map_change_delay"]*1000, whenSetMap, (p, mapname, mapmode))
	else:
		whenSetMap(p, mapname, mapmode)