import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass

import cxsbs
DatabaseSession = cxsbs.getResource("DatabaseSession")
SettingsManager = cxsbs.getResource("SettingsManager")
Setting = cxsbs.getResource("Setting")

databaseConfigurationFilename = 'db'

SettingsManager.addSetting(Setting.Setting	(
												category=databaseConfigurationFilename, 
												subcategory="General", 
												symbolicName="backend", 
												displayName="Backend Manager Name", 
												default="DatabaseManagerSqlite", 
												doc="Name of the plugin providing the backend to the database manager."
											))

settings = SettingsManager.getAccessor(category=databaseConfigurationFilename, subcategory="General")
		
def getBackendName():
	return settings["backend"]

def uriBeginsWithQuote(uri):
	if len(uri) < 1:
		return False
	return (uri[0] == "'" or uri[0] == "\"")

def isProtocol(uri, protocolName):
	offset = 0
	if (uriBeginsWithQuote(uri)):
		offset = 1
	delimiterPosition = uri.find(":///")
	uriBeginPosition = uri.find(protocolName)
	return uriBeginPosition >= offset and uriBeginPosition < delimiterPosition

import sqlalchemy.orm
import abc
	
class DatabaseManagerBackend(object):
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def __init__(self):
		self.isConnected = False
	
	def connect(self):
		if not self.isConnected:
			self.initEngine()
			self.isConnected = True
	
	@abc.abstractmethod
	def initEngine(self):
		self.engine = None
		self.sessionFactory = sqlalchemy.orm.sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
	
	def reconnect(self):
		self.isConnected = False
		del self.engine
		self.connect()
	
	def dbsession(self):
		#sqlalchemy.orm.sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
		return self.sessionFactory()
		
	def session(self):
		return DatabaseSession.SessionManager(self)
			
	@abc.abstractmethod
	def readConfiguration(self):
		pass
