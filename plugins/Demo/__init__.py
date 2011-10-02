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
Events = cxsbs.getResource("Events")
UI = cxsbs.getResource("UI")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Colors = cxsbs.getResource("Colors")
Logging = cxsbs.getResource("Logging")
Players = cxsbs.getResource("Players")
Commands = cxsbs.getResource("Commands")
Messages = cxsbs.getResource("Messages")

pluginCategory = 'Demo'

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="persistent_recording", 
												displayName="Persistent recording", 
												default=True, 
												doc="Use persistent recording on startup."
											))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

permissionsCategory = "Permissions"

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_enable_recording",
													displayName="Allow groups enable recording", 
													default=['__all__'],
													doc="Groups which are allowed to enable single match recording.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="deny_groups_enable_recording",
													displayName="Deny groups enable recording", 
													default=[],
													doc="Groups which are not allowed to enable single match recording.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_disable_recording",
													displayName="Allow groups disable recording", 
													default=['__admin__'],
													doc="Groups which are allowed to enable single match recording.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="deny_groups_disable_recording",
													displayName="Deny groups disable recording", 
													default=[],
													doc="Groups which are not allowed to enable single match recording.",
												))

groupSettings = SettingsManager.getAccessor(category=permissionsCategory, subcategory=pluginCategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="record_next_message", 
						displayName="Record next message", 
						default="Demo recording has been ${blue}${action}${white} for next match by ${green}${name}${white}.", 
						doc="Format of message to print when a player sets demo record status for the next match."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="record_persistent_message", 
						displayName="Record persistent message", 
						default="Persistent demo recording has been ${blue}${action}${white} by ${green}${name}${white}.", 
						doc="Format of message to print when a player sets persistent demo record status."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

@Events.eventHandler('player_record_demo')
def playerRecordNextMatch(cn, val):
	p = Players.player(cn)
	if not (p.isPermitted(groupSettings['allow_groups_enable_recording'], groupSettings['deny_groups_enable_recording']) and val):
		UI.insufficientPermissions(cn)
	elif not (p.isPermitted(groupSettings['allow_groups_disable_recording'], groupSettings['deny_groups_disable_recording']) and not val):
		UI.insufficientPermissions(cn)
	else:
		if val == ServerCore.nextMatchRecorded():
			return
		if val:
			action = 'enabled'
		else:
			action = 'disabled'
		ServerCore.setRecordNextMatch(val)
		messager.sendMessage('record_next_message', p, dictionary={'action': action, 'name': p.name()})

@Events.eventHandler('server_start')
@Events.eventHandler('map_changed')
def persistRecordNextMatch(*args):
	ServerCore.setRecordNextMatch(settings["persistent_recording"])

@Commands.commandHandler('toggledemo')
def togglePersistantDemoRecord(cn, args):
	'''
	@description Toggle persistent demo
	@usage
	@allowGroups __admin__
	@denyGroups
	@doc Toggle the status of persistent demo.
	'''
	if settings["persistent_recording"]:
		settings["persistent_recording"] = False
		action = "disabled"
	else:
		settings["persistent_recording"] = True
		action = "enable"
		
	p = Players.player(cn)
	ServerCore.setRecordNextMatch(settings["persistent_recording"])
	messager.sendMessage('record_persistent_message', dictionary={'action': action, 'name': p.name()})
	