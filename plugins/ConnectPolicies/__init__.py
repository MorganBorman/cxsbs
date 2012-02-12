import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
Players = cxsbs.getResource("Players")
Events = cxsbs.getResource("Events")
ServerCore = cxsbs.getResource("ServerCore")
SettingsManager = cxsbs.getResource("SettingsManager")
Setting = cxsbs.getResource("Setting")
Logging = cxsbs.getResource("Logging")

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

import threading
import sys
import traceback

DISC_NONE = 0
DISC_EOP = 1
DISC_CN = 2
DISC_KICK = 3
DISC_TAGT = 4
DISC_IPBAN = 5
DISC_PRIVATE = 6
DISC_MAXCLIENTS = 7
DISC_TIMEOUT = 8
DISC_OVERFLOW = 9
DISC_NUM = 10

@Events.eventHandler("player_connect_delayed")
def on_delayed_connect(cn):
	pwd = ServerCore.playerConnectPwd(cn)
	p = Players.player(cn)
	
	if ( not Events.triggerPolicyEvent('connect_private', (cn, pwd)) ) and (not p.isPermitted(groupSettings['allow_groups_connect_private'], [])):
		ServerCore.playerDisconnect(cn, DISC_PRIVATE)
		return
		
	if ( not Events.triggerPolicyEvent('connect_kick', (cn, pwd)) ) and (not p.isPermitted(groupSettings['allow_groups_connect_banned'], [])):
		ServerCore.playerDisconnect(cn, DISC_IPBAN)
		return
		
	if ( not Events.triggerPolicyEvent('connect_capacity', (cn, pwd)) ) and (not p.isPermitted(groupSettings['allow_groups_connect_oversize'], [])):
		ServerCore.playerDisconnect(cn, DISC_MAXCLIENTS)
		return
	
	ServerCore.postinitclient(cn)