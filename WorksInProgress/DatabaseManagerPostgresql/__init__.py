import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
		
import cxsbs
DatabaseManagerBase = cxsbs.getResource("DatabaseManagerBase")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManagerBase.databaseConfigurationFilename, 
												subcategory="Postgresql", 
												symbolicName="host", 
												displayName="Host", 
												default="localhost", 
												doc="Database host to connect to.",
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManagerBase.databaseConfigurationFilename, 
												subcategory="Postgresql", 
												symbolicName="port", 
												displayName="Port", 
												default="5432", 
												doc="Database port to connect to.",
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManagerBase.databaseConfigurationFilename, 
												subcategory="Postgresql", 
												symbolicName="database", 
												displayName="Database", 
												default="cxsbs", 
												doc="Name of the database to connect to.",
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManagerBase.databaseConfigurationFilename, 
												subcategory="Postgresql",
												symbolicName="user", 
												displayName="User", 
												default="", 
												doc="Name of the user to connect to the database as.",
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManagerBase.databaseConfigurationFilename, 
												subcategory="Postgresql",
												symbolicName="password", 
												displayName="Password", 
												default="", 
												doc="Password of the user to connect to the database as.",
											))

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool, SingletonThreadPool, QueuePool
import sys
	
class DatabaseManagerBackend(DatabaseManagerBase.DatabaseManagerBackend):
	def __init__(self):
		DatabaseManagerBase.DatabaseManagerBackend.__init__(self)
		self.readConfiguration()

	def initEngine(self):
		uri = self.protocol + self.user + ":" + self.password + "@" + self.host + ":" + self.port + "/" + self.database
		self.engine = create_engine(uri, echo=False, poolclass=QueuePool, pool_size=20, max_overflow=0)
		self.sessionFactory = sqlalchemy.orm.sessionmaker(bind=self.engine, autocommit=False, autoflush=False)

	def readConfiguration(self):
		settings = SettingsManager.getAccessor(DatabaseManagerBase.databaseConfigurationFilename, subcategory="Postgresql")
		
		self.protocol = "postgresql://"
		self.host = settings['host']
		self.port = settings['port']
		self.database = settings['database']
		self.user = settings['user']
		self.password = settings['password']
