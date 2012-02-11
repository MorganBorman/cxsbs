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
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManagerBase.databaseConfigurationFilename, 
												subcategory="Informix", 
												symbolicName="database", 
												displayName="Database", 
												default="cxsbs", 
												doc="Name of the database to connect to.",
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManagerBase.databaseConfigurationFilename, 
												subcategory="Informix",
												symbolicName="user", 
												displayName="User", 
												default="", 
												doc="Name of the user to connect to the database as.",
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManagerBase.databaseConfigurationFilename, 
												subcategory="Informix",
												symbolicName="password", 
												displayName="Password", 
												default="", 
												doc="Password of the user to connect to the database as.",
											))

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool, SingletonThreadPool
import informixdb #@UnresolvedImport
import sys
		
class DatabaseManagerBackend(DatabaseManagerBase.DatabaseManagerBackend):
	def __init__(self):
		DatabaseManagerBase.DatabaseManagerBackend.__init__(self)
		self.readConfiguration()

	def createDatabase(self, name):
		'''create the initial database
		'''
		dbspace = "dbspace0"
		sql = "create database" + name + " in " + dbspace + " with buffered log"
		try:
			session = self.getSession()
			# TODO needs the method to execute a sql statement on a session
			session.execute(sql)
		except Exception as e:
			print type(e)
			print e.args
			print e
			sys.exit(1)
		pass
	def initEngine(self):
		self.engine = create_engine	(
							self.protocol, 
							creator=lambda: informixdb.connect	(
													self.database, 
													self.user, 
													self.password
												), 
							echo=False, 
							poolclass=SingletonThreadPool
						)
	
	def dropDatabase(self):
		'''drop the database
		'''
		pass

	def getSession(self):
		return None

	def readConfiguration(self):
		settings = SettingsManager.getAccessor(category=DatabaseManagerBase.databaseConfigurationFilename, subcategory="Informix")
		
		self.protocol = "informix:///"
		self.database = settings['database']
		self.user = settings['user']
		self.password = settings['password']
