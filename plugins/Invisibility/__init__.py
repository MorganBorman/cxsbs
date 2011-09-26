import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass
	
import cxsbs
Config = cxsbs.getResource("Config")
ServerCore = cxsbs.getResource("ServerCore")
Events = cxsbs.getResource("Events")
	
		
def init():
	config = Config.PluginConfig('Invisibility')
	allow_invisible_connect = config.getBoolOption('Config', 'allow', 'no')
	invisible_connect_password = config.getOption('Config', 'password', 'ObscuraOptimus')
	del config

	@Events.policyHandler('connect_invisible')
	def connectInvisible(cn, pwd):
		if not allow_invisible_connect:
			return False
		
		return pwd == ServerCore.hashPassword(cn, invisible_connect_password)