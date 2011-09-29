import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
def setConfigurationFilename(filename):
	global databaseConfigurationFilename
	databaseConfigurationFilename = 'db'

import cxsbs
DatabaseManagerBase = cxsbs.getResource("DatabaseManagerBase")
ServerCore = cxsbs.getResource("ServerCore")
Config = cxsbs.getResource("Config")

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

class DatabaseManagerBackend(DatabaseManagerBase.DatabaseManagerBackend):
	def __init__(self):
		DatabaseManagerBase.DatabaseManagerBackend.__init__(self)
		self.readConfiguration()

	def initEngine(self):
		self.engine = create_engine(self.protocol + self.database, echo=False, poolclass=NullPool)
		
	def readConfiguration(self):
		config = Config.PluginConfig(DatabaseManagerBase.databaseConfigurationFilename)
		self.protocol = "sqlite:///"
		self.database = ServerCore.instanceRoot() + "/" + config.getOption('Config', 'database', 'cxsbs.db')
		del config
