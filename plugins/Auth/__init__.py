import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		self.init_config()
		self.init_handlers()
		
	def reload(self):
		self.init_config()
		self.init_handlers()
		
	def unload(self):
		deinit()
	
	def init_config(self):
		global autoAuth, authDesc
		config = Config.PluginConfig('Auth')
		autoAuth = config.getBoolOption('Config', 'automatically_request_auth', True)
		authDesc = config.getOption('Config', 'automatic_request_description', 'mydomain.com')
		del config
		
	def init_handlers(self):
		@Events.eventHandler("player_connect")
		def onConnect(cn):
			if autoAuth:
				p = Players.player(cn)
				p.requestAuth(authDesc)
		
import time
import cxsbs
Players = cxsbs.getResource("Players")
Events = cxsbs.getResource("Events")
Config = cxsbs.getResource("Config")
ServerCore = cxsbs.getResource("ServerCore")

def genKeyPair(keySeed):
	newSeed = ""
	timestring = str(time.time())
	
	for i in range(len(keySeed)):
			newSeed += keySeed[i]
			newSeed += timestring[i % (len(timestring) - 1)]

	return ServerCore.genAuthKey(newSeed)


