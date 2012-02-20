import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		Events.registerServerEventHandler('player_connect_delayed', on_connect_delayed_sync)
		
	def unload(self):
		pass
	
import cxsbs
Players = cxsbs.getResource("Players")
Events = cxsbs.getResource("Events")
ServerCore = cxsbs.getResource("ServerCore")
SettingsManager = cxsbs.getResource("SettingsManager")
Setting = cxsbs.getResource("Setting")
Logging = cxsbs.getResource("Logging")
ProcessingThread = cxsbs.getResource("ProcessingThread")
PlayerDisconnect = cxsbs.getResource("PlayerDisconnect")

pluginCategory = 'ConnectPolicies'
permissionsCategory = 'Permissions'

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_connect_oversize",
													displayName="Allow groups connect oversize", 
													default=['__admin__'],
													doc="Groups which are permitted to connect even when the server is at capacity.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_connect_private",
													displayName="Allow groups connect private", 
													default=['__admin__'],
													doc="Groups which are permitted to connect even when the server is in private.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_connect_banned",
													displayName="Allow groups connect banned", 
													default=['__admin__'],
													doc="Groups which are permitted to connect even their ips are banned.",
												))

groupSettings = SettingsManager.getAccessor(category=permissionsCategory, subcategory=pluginCategory)

def on_connect_delayed_sync(cn):
	ProcessingThread.queue(on_connect_delayed, (cn,))

def on_connect_delayed(cn):
	pwd = ServerCore.playerConnectPwd(cn)
	p = Players.player(cn)
	
	if ( not Events.triggerPolicyEvent('connect_private', (cn, pwd)) ) and (not p.isPermitted(groupSettings['allow_groups_connect_private'], [])):
		Events.execLater(PlayerDisconnect.disconnect, (cn, PlayerDisconnect.DISC_PRIVATE))
		return
		
	if ( not Events.triggerPolicyEvent('connect_kick', (cn, pwd)) ) and (not p.isPermitted(groupSettings['allow_groups_connect_banned'], [])):
		Events.execLater(PlayerDisconnect.disconnect, (cn, PlayerDisconnect.DISC_IPBAN))
		return
		
	if ( not Events.triggerPolicyEvent('connect_capacity', (cn, pwd)) ) and (not p.isPermitted(groupSettings['allow_groups_connect_oversize'], [])):
		Events.execLater(PlayerDisconnect.disconnect, (cn, PlayerDisconnect.DISC_MAXCLIENTS))
		return
	
	if Events.triggerPolicyEvent('player_unspectate', (cn, cn)) and ServerCore.masterMode() < 2:
		ServerCore.setStateDead(cn)
	
	Events.execLater(ServerCore.sendClientInitialization, (cn,))