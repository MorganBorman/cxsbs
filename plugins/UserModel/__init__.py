from cxsbs.Plugin import Plugin

class UserModel(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
import cxsbs
Config = cxsbs.getResource("Config")
		
def init():
	config = Config.PluginConfig('dbtables')
	modelName = config.getOption('User Manager', 'users_model', 'IntegratedUserModel')
	del config
	
	global model
	modelModule = cxsbs.getResource("modelName")