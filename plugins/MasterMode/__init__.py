from cxsbs.Plugin import Plugin

class MasterMode(Plugin):
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
Logging = cxsbs.getResource("Logging")
ServerCore = cxsbs.getResource("ServerCore")
MessageFramework = cxsbs.getResource("MessageFramework")

MMNAMES = ['open',
	'veto',
	'locked',
	'private']

def init():
	config = Config.PluginConfig('MasterMode')
	default_mastermode = config.getIntOption('Config', 'default_mastermode', 0)
	resetWhenEmpty = config.getBoolOption('Config', 'reset_when_empty', True)
	del config
	
	global messageModule
	messageModule = MessageFramework.MessagingModule()
	messageModule.addMessage("set_mastermode", "${green}${name}${white} set the master mode to ${blue}${mastermode}${white}.", "MasterMode")
	messageModule.finalize()
	
	
	@Events.eventHandler('player_set_mastermode')
	def onSetMM(cn, mm):
		'''
		@commandType
		@allowGroups __master__ __admin__
		@denyGroups
		'''
		p = Players.player(cn)
		p.logAction('set mastermode', mastermode=MMNAMES[mm])
		messageModule.sendMessage('set_mastermode', dictionary={'name':p.name(), 'mastermode':MMNAMES[mm]})
		ServerCore.setMasterMode(mm)
	
	@Events.eventHandler('no_clients')
	def onNoClients():
		if ServerCore.masterMode() != default_mastermode:
			ServerCore.setMasterMode(default_mastermode)
			Logging.info("Server empty: resetting mastermode to: " + MMNAMES[default_mastermode])