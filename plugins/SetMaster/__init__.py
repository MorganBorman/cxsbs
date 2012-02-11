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
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
ServerCore = cxsbs.getResource("ServerCore")
Messages = cxsbs.getResource("Messages")
Commands = cxsbs.getResource("Commands")

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

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="connect_password", 
												displayName="Connect password", 
												default=ppwgen.generatePassword(),
												doc="Password used to allow clients to connect if kicked or server is in private."
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

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="master_given", 
						displayName="Master given", 
						default="${info}${orange}master${white} has been given to ${green}${name}${white}.", 
						doc="Message to show a user when they give master to a player."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

@Events.eventHandler('server_start')
def onServerStart():
	if settings["public_server"]:
		ServerCore.setMasterMask(3)
	else:
		ServerCore.setMasterMask(2)

def setSimpleMaster(cn, auth=False):
	p = Players.player(cn)
	if not settings["public_server"] and not auth:
		messager.sendPlayerMessage('not_open_server', p)
		return
	elif Players.currentMaster() != None and not auth:
		messager.sendPlayerMessage('already_master', p)
		return
	elif Players.currentAdmin() != None:
		messager.sendPlayerMessage('already_admin', p)
		return
	else:
		if not p.isInvisible():
			messager.sendMessage('claimed_master', dictionary={"name": p.name()})
		else:
			messager.sendMessage('claimed_master', group=Players.SeeInvisibleGroup, dictionary={"name": p.name()})
		p.logAction('claimed master')
		ServerCore.setMaster(cn)
		
def setSimpleAdmin(cn):
	p = Players.player(cn)
	if not p.isInvisible():
		messager.sendMessage('claimed_admin', dictionary={"name": p.name()})
	else:
		messager.sendMessage('claimed_admin', group=Players.SeeInvisibleGroup, dictionary={"name": p.name()})
	p.logAction('claimed admin')
	ServerCore.setAdmin(cn)
	
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
		setSimpleAdmin(cn)
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
		if not p.isInvisible():
			messager.sendMessage('relinquished_admin', dictionary={"name": p.name()})
		else:
			messager.sendMessage('relinquished_admin', group=Players.SeeInvisibleGroup, dictionary={"name": p.name()})
		p.logAction('relinquished admin')
	elif "__master__" in groups:
		if not p.isInvisible():
			messager.sendMessage('relinquished_master', dictionary={"name": p.name()})
		else:
			messager.sendMessage('relinquished_master', group=Players.SeeInvisibleGroup, dictionary={"name": p.name()})
		p.logAction('relinquished master')
	else:
		return
	ServerCore.resetPrivilege(cn)
	
@Commands.commandHandler('master')
def masterCmd(cn, args):
	'''
	@description claim master
	@usage
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Allows a player who is in the appropriate groups to claim master.
	'''
	if Players.currentAdmin() != None:
		messager.sendPlayerMessage('already_admin', p)
		return
	p = Players.player(cn)
	if not p.isInvisible():
		messager.sendMessage('claimed_master', dictionary={"name": p.name()})
	else:
		messager.sendMessage('claimed_master', group=Players.SeeInvisibleGroup, dictionary={"name": p.name()})
	p.logAction('claimed master')
	ServerCore.setMaster(cn)

@Commands.commandHandler('admin')
def adminCmd(cn, args):
	'''
	@description claim admin
	@usage
	@allowGroups __admin__
	@denyGroups
	@doc Allows a player who is in the appropriate groups to claim admin.
	'''
	setSimpleAdmin(cn)
		
@Commands.commandHandler('givemaster')
def onGiveMaster(cn, args):
	'''
	@description give master to a player
	@usage <cn>
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Allows a player who is in the appropriate groups to give master to another.
	'''
	if args == '':
		raise Commands.UsageError()
		return
	try:
		tcn = int(args)
	except TypeError:
		raise Commands.UsageError()
		return
	
	p = Players.player(cn)
	t = Players.player(tcn)
	
	messager.sendPlayerMessage('master_given', p, dictionary={'name': t.name()})
	ServerCore.setMaster(tcn)