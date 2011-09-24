from cxsbs.Plugin import Plugin

class SetMaster(Plugin):
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
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
ServerCore = cxsbs.getResource("ServerCore")
MessageFramework = cxsbs.getResource("MessageFramework")

import ppwgen

def setSimpleMaster(cn, auth=False):
	p = Players.player(cn)
	if not publicServer and not auth:
		messageModule.sendPlayerMessage('not_open_server', p)
		
		return
	elif Players.currentMaster() != None and not auth:
		messageModule.sendPlayerMessage('already_master', p)
		return
	elif Players.currentAdmin() != None:
		messageModule.sendPlayerMessage('already_admin', p)
		return
	else:
		messageModule.sendMessage('claimed_master', dictionary={"name": p.name()})
		p.logAction('claimed master')
		ServerCore.setMaster(cn)

def init():
	global admin_password, publicServer
	config = Config.PluginConfig('SetMaster')
	admin_password = config.getOption('Admin', 'password', ppwgen.generatePassword())
	publicServer = config.getBoolOption('Admin', 'publicServer', True)
	del config
	
	global messageModule
	messageModule = MessageFramework.MessagingModule()
	messageModule.addMessage("not_open_server", "This is not an open server, you need ${magenta}auth${white} to gain ${orange}master${white}.", "SetMaster")
	messageModule.addMessage("already_master", "You cannot claim ${orange}master${white}, there is already a ${orange}master${white} here.", "SetMaster")
	messageModule.addMessage("already_admin", "You cannot claim ${orange}master${white}, there is already a ${red}admin${white} here.", "SetMaster")
	messageModule.addMessage("claimed_master", "${green}${name}${white} claimed ${orange}master${white}.", "SetMaster")
	messageModule.addMessage("claimed_admin", "${green}${name}${white} claimed ${red}admin${white}.", "SetMaster")
	messageModule.addMessage("relinquished_master", "${green}${name}${white} relinquished ${orange}master${white}.", "SetMaster")
	messageModule.addMessage("relinquished_admin", "${green}${name}${white} relinquished ${red}admin${white}.", "SetMaster")
	messageModule.finalize()
	
	@Events.eventHandler('player_setmaster')
	def onSetMaster(cn, givenhash):
		p = Players.player(cn)
		p.logAction('issued setmaster')
		p = Players.player(cn)
		adminhash = ServerCore.hashPassword(cn, admin_password)
		if givenhash == adminhash:
			messageModule.sendMessage('claimed_admin', dictionary={"name": p.name()})
			p.logAction('claimed admin')
			ServerCore.setAdmin(cn)
		else:
			setSimpleMaster(cn)
			
	@Events.eventHandler('player_setmaster_off')
	def onSetMasterOff(cn):
		'''
		@commandType
		@allowGroups = __admin__ __master__
		@denyGroups =
		'''
		p = Players.player(cn)
		groups = p.groups()
		if "__admin__" in groups:
			messageModule.sendMessage('relinquished_admin', dictionary={"name": p.name()})
			p.logAction('relinquished admin')
		elif "__master__" in groups:
			messageModule.sendMessage('relinquished_master', dictionary={"name": p.name()})
			p.logAction('relinquished master')
		else:
			return
		ServerCore.resetPrivilege(cn)