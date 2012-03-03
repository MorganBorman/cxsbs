import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass

import cxsbs
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
UI = cxsbs.getResource("UI")
ServerCore = cxsbs.getResource("ServerCore")
Server = cxsbs.getResource("Server")
Logging = cxsbs.getResource("Logging")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Messages = cxsbs.getResource("Messages")
Commands = cxsbs.getResource("Commands")
ProcessingThread = cxsbs.getResource("ProcessingThread")

permissionsCategory = 'Permissions'
pluginSubcategory = 'Spectate'

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_spectate_players",
													displayName="Allow groups spectate players", 
													default=['__master__','__admin__'],
													doc="Groups which are permitted to spectate other players.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_spectate_players",
													displayName="Deny groups spectate players", 
													default=[],
													doc="Groups which are permitted to spectate other players.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_spectate_self",
													displayName="Allow groups spectate self", 
													default=['__all__'],
													doc="Groups which are permitted to spectate themselves.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_spectate_self",
													displayName="Deny groups spectate self", 
													default=[],
													doc="Groups which are not permitted to spectate themselves.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_unspectate_self",
													displayName="Allow groups unspectate self", 
													default=['__all__'],
													doc="Groups which are permitted to unspectate themselves.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_unspectate_self",
													displayName="Deny groups unspectate self", 
													default=[],
													doc="Groups which are not permitted to unspectate themselves.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_unspectate_self_locked",
													displayName="Allow groups unspectate self locked", 
													default=['__master__', '__admin__'],
													doc="Groups which are permitted to unspectate themselves when the server is locked.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_unspectate_self_locked",
													displayName="Deny groups unspectate self locked", 
													default=[],
													doc="Groups which are not permitted to unspectate themselves when the server is locked.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_unspectate_players",
													displayName="Allow groups unspectate players", 
													default=['__master__', '__admin__'],
													doc="Groups which are permitted to unspectate other players.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_unspectate_players",
													displayName="Deny groups unspectate players", 
													default=[],
													doc="Groups which are not permitted to unspectate other players.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_unspectate_players_locked",
													displayName="Allow groups unspectate players locked", 
													default=['__master__', '__admin__'],
													doc="Groups which are permitted to unspectate other players when the server is locked.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_unspectate_players_locked",
													displayName="Deny groups unspectate players locked", 
													default=[],
													doc="Groups which are not permitted to unspectate other players when the server is locked.",
												))

groupSettings = SettingsManager.getAccessor(category=permissionsCategory, subcategory=pluginSubcategory)

pluginCategory = "Spectate"

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='unspectate_denied_locked', 
						displayName='Unspectate denied locked', 
						default="${denied}The mastermode is ${red}locked${white} you cannot unspectate.",
						doc="Message to print when a player cannot unspectate."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

@Events.policyHandler('player_spectate')
def onSpectate(cn, tcn):
	p = Players.player(cn)
	if tcn != cn:
		if p.isPermitted(groupSettings["allow_groups_spectate_players"], groupSettings["deny_groups_spectate_players"]):
			return True
		else:
			UI.insufficientPermissions(cn)
			return False
	else:
		if p.isPermitted(groupSettings["allow_groups_spectate_self"], groupSettings["deny_groups_spectate_self"]):
			return True
		else:
			UI.insufficientPermissions(cn)
			return False
		
@Events.policyHandler('player_unspectate')
def onUnspectate(cn, tcn):
	p = Players.player(cn)
	if tcn != cn:
		if ServerCore.masterMode() > 1:
			if p.isPermitted(groupSettings["allow_groups_unspectate_players_locked"], groupSettings["deny_groups_unspectate_players_locked"]):
				return True
			else:
				UI.insufficientPermissions(cn)
				return False
		else:
			if p.isPermitted(groupSettings["allow_groups_unspectate_players"], groupSettings["deny_groups_unspectate_players"]):
				return True
			else:
				UI.insufficientPermissions(cn)
				return False
	else:
		if ServerCore.masterMode() > 1:
			if p.isPermitted(groupSettings["allow_groups_unspectate_self_locked"], groupSettings["deny_groups_unspectate_self_locked"]):
				return True
			else:
				messager.sendPlayerMessage("unspectate_denied_locked", p)
				return False
		else:
			if p.isPermitted(groupSettings["allow_groups_unspectate_self"], groupSettings["deny_groups_unspectate_self"]):
				return True
			else:
				UI.insufficientPermissions(cn)
				return False
			
"""
@Events.eventHandler('player_connect')
def on_connect_sync(cn):
	ProcessingThread.queue(on_connect, (cn,))

def on_connect(cn):
	if ServerCore.masterMode() > 1:
		return
	else:
		if Events.triggerPolicyEvent("player_unspectate", (cn, cn)):
			ServerCore.unspectate(cn)
"""
	
@Commands.commandHandler('specall')
def specAll(cn, args):
	'''
	@description Spectate all players
	@usage
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Spectate all players.
	'''
	if args != '':
		raise Commands.ExtraArgumentError()
	else:
		for s in ServerCore.players():
			ServerCore.spectate(s)

@Commands.commandHandler('unspecall')
def unspecAll(cn, args):
	'''
	@description Unspectate all players
	@usage
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Unspectate all players.
	'''
	if args != '':
		raise Commands.ExtraArgumentError()
	else:
		for s in ServerCore.spectators():
			ServerCore.unspectate(s)