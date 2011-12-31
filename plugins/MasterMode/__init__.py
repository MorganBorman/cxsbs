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
Logging = cxsbs.getResource("Logging")
ServerCore = cxsbs.getResource("ServerCore")
Messages = cxsbs.getResource("Messages")
SetMaster = cxsbs.getResource("SetMaster")

pluginCategory = 'MasterMode'

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="reset_when_empty", 
												displayName="Reset when empty", 
												default=True, 
												doc="Whether or not to reset mastermode when the server becomes empty."
											))
SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="default_mastermode", 
												displayName="Default mastermode", 
												default=0, 
												doc="The mastermode to start the server with and to return to if the setting reset_when_empty is True."
											))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="set_mastermode", 
						displayName="Mastermode set", 
						default="${green}${name}${white} set the master mode to ${blue}${mastermode}${white}.", 
						doc="Message to print when a user has set the mastermode on the server."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

MMNAMES = ['open',
	'veto',
	'locked',
	'private']
	
@Events.eventHandler('player_set_mastermode')
def onSetMM(cn, mm):
	'''
	@commandType
	@allowGroups __master__ __admin__
	@denyGroups
	@doc Command type event which is called when a client types \"/mastermode <number>\" and which sets the mastermode of the server.
	'''
	p = Players.player(cn)
	p.logAction('set mastermode', mastermode=MMNAMES[mm])
	messager.sendMessage('set_mastermode', dictionary={'name':p.name(), 'mastermode':MMNAMES[mm]})
	ServerCore.setMasterMode(mm)
	
@Events.policyHandler('connect_private')
def allowClient(cn, pwd):
	connecthash = ServerCore.hashPassword(cn, SetMaster.settings["connect_password"])
	if pwd == connecthash:
		return True
	
	return False

@Events.eventHandler('server_start')
def onServerStart():
	if ServerCore.masterMode() != settings["default_mastermode"]:
		ServerCore.setMasterMode(settings["default_mastermode"])
		Logging.info("Server start: setting mastermode to: " + MMNAMES[settings["default_mastermode"]])

@Events.eventHandler('no_clients')
def onNoClients():
	if settings["reset_when_empty"]:
		if ServerCore.masterMode() != settings["default_mastermode"]:
			ServerCore.setMasterMode(settings["default_mastermode"])
			Logging.info("Server empty: resetting mastermode to: " + MMNAMES[settings["default_mastermode"]])