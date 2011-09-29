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

import cxsbs
DatabaseManagerBase = cxsbs.getResource("DatabaseManagerBase")
ServerCore = cxsbs.getResource("ServerCore")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManagerBase.databaseConfigurationFilename, 
												subcategory="Sqlite", 
												symbolicName="database", 
												displayName="Database", 
												default="cxsbs.db", 
												doc="Path of the database to connect to.",
											))

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

class DatabaseManagerBackend(DatabaseManagerBase.DatabaseManagerBackend):
	def __init__(self):
		DatabaseManagerBase.DatabaseManagerBackend.__init__(self)
		self.readConfiguration()

	def initEngine(self):
		self.engine = create_engine(self.protocol + self.database, echo=False, poolclass=NullPool)
		
	def readConfiguration(self):
		settings = SettingsManager.getAccessor(DatabaseManagerBase.databaseConfigurationFilename, subcategory="Sqlite")
		
		self.protocol = "sqlite:///"
		self.database = ServerCore.instanceRoot() + "/" + settings['database']
