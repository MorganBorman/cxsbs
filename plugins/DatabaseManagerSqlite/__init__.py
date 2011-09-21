from cxsbs.Plugin import Plugin

class DatabaseManagerSqlite(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
databaseConfigurationFilename = 'db'

def getProtocol():
	try:
		config = Config.PluginConfig(databaseConfigurationFilename)
		protocol = config.getOption('Config', 'protocol', 'sqlite://')
		return protocol
	except:
		raise #probably should have something better here. just rethrow for now.
	finally:
		del config

import cxsbs
DatabaseManagerBase = cxsbs.getResource("DatabaseManagerBase")
Config = cxsbs.getResource("Config")

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

class SqliteManager(DatabaseManagerBase.DatabaseManager):
	def __init__(self):
		DatabaseManagerBase.DatabaseManager.__init__(self)
		self.readConfiguration()

	def initEngine(self):
		self.engine = create_engine(self.protocol + self.database, echo=False, poolclass=NullPool)
		
	def readConfiguration(self):
		config = Config.PluginConfig(databaseConfigurationFilename)
		self.protocol = getProtocol()
		self.database = config.getOption('Config', 'database', 'cxsbs.db')
		del config
