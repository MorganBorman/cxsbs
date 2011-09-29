import cxsbs.Plugin
from orca.settings_manager import SettingsManager

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
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
ServerCore = cxsbs.getResource("ServerCore")
Messages = cxsbs.getResource("Messages")

import ppwgen

pluginCategory = 'SetMaster'

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="admin_password", 
												displayName="Admin password", 
												default=ppwgen.generatePassword(),
												doc="Password used to allow clients to use \"/setmaster <password>\" to claim admin."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="public_server", 
												displayName="Public server", 
												default=True,
												doc="Allow clients to claim master using \"/setmaster 1\" when no admin or other master is present."
											))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="not_open_server", 
						displayName="Server not open", 
						default="This is not an open server, you need ${magenta}auth${white} to gain ${orange}master${white}.", 
						doc="Message to print when a user tries to use \"/setmaster <password\" but does not use the correct password."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="already_master", 
						displayName="Already master", 
						default="You cannot claim ${orange}master${white}, there is already a ${orange}master${white} here.", 
						doc="Message to print when a user could claim master successfully but there is already a master present."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="already_admin", 
						displayName="Already admin", 
						default="You cannot claim ${orange}master${white}, there is already a ${red}admin${white} here.", 
						doc="Message to print when a user could claim master successfully but there is already an admin present."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="claimed_master", 
						displayName="Claimed master", 
						default="${green}${name}${white} claimed ${orange}master${white}.", 
						doc="Message to print when a user successfully claimed master."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="claimed_admin", 
						displayName="Claimed admin", 
						default="${green}${name}${white} claimed ${red}admin${white}.", 
						doc="Message to print when a user successfully claimed admin."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="relinquished_master", 
						displayName="Relinquished master", 
						default="${green}${name}${white} relinquished ${orange}master${white}.", 
						doc="Message to print when a user relinquished master."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="relinquished_admin", 
						displayName="Relinquished admin", 
						default="${green}${name}${white} relinquished ${red}admin${white}.", 
						doc="Message to print when a user relinquished admin."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

def setSimpleMaster(cn, auth=False):
	p = Players.player(cn)
	if not settings["publicServer"] and not auth:
		messager.sendPlayerMessage('not_open_server', p)
		
		return
	elif Players.currentMaster() != None and not auth:
		messager.sendPlayerMessage('already_master', p)
		return
	elif Players.currentAdmin() != None:
		messager.sendPlayerMessage('already_admin', p)
		return
	else:
		messager.sendMessage('claimed_master', dictionary={"name": p.name()})
		p.logAction('claimed master')
		ServerCore.setMaster(cn)
	
@Events.eventHandler('player_setmaster')
def onSetMaster(cn, givenhash):
	'''
	@commandType
	@allowGroups __all__
	@denyGroups
	@doc Command type event triggered when a user issues the \"/setmaster 0\" command."
	'''
	p = Players.player(cn)
	p.logAction('issued setmaster')
	p = Players.player(cn)
	adminhash = ServerCore.hashPassword(cn, settings["admin_password"])
	if givenhash == adminhash:
		messager.sendMessage('claimed_admin', dictionary={"name": p.name()})
		p.logAction('claimed admin')
		ServerCore.setAdmin(cn)
	else:
		setSimpleMaster(cn)
		
@Events.eventHandler('player_setmaster_off')
def onSetMasterOff(cn):
	'''
	@commandType
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Command type event triggered when a user issues the \"/setmaster <password>\" command."
	'''
	p = Players.player(cn)
	groups = p.groups()
	if "__admin__" in groups:
		messager.sendMessage('relinquished_admin', dictionary={"name": p.name()})
		p.logAction('relinquished admin')
	elif "__master__" in groups:
		messager.sendMessage('relinquished_master', dictionary={"name": p.name()})
		p.logAction('relinquished master')
	else:
		return
	ServerCore.resetPrivilege(cn)