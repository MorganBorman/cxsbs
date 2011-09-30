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
UI = cxsbs.getResource("UI")
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Net = cxsbs.getResource("Net")
Server = cxsbs.getResource("Server")
Commands = cxsbs.getResource("Commands")
Messages = cxsbs.getResource("Messages")

pluginCategory = 'MapCheck'

SettingsManager.addSetting(Setting.ListSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="spectate_map_modified",
													displayName="Spectate map modified", 
													default=['__master__','__admin__'],
													doc="Whether or not to automatically spectate players with modified maps.",
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

messager = Messages.getAccessor(subcategory=pluginCategory)

@Events.eventHandler('player_modified_map')
def onMapModified(cn):
	p = Players.player(cn)
	if not p.isInvisible():
		messager.messagePlayer('map_modified', p, dictionary={'name':p.name()})
	p.gamevars['modified_map'] = True
	if not onUnspectate(cn, cn):
		p.spectate()

@Events.policyHandler('player_unspectate')
def onUnspectate(cn, tcn):
	if not settings["spectate_map_modified"]:
		return True
		
	p = Players.player(cn)
	if not p.gamevars['modified_map']:
		return True
		
	for group in p.groups():
		if group in groupSettings["allow_groups_modified_unspec"]:
			return True
		
	if cn == tcn:
		messager.messagePlayer('modified_unspec', p)
		
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