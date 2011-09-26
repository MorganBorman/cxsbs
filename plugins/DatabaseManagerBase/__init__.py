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
DatabaseSession = cxsbs.getResource("DatabaseSession")
Config = cxsbs.getResource("Config")

databaseConfigurationFilename = 'db'
		
def getBackendName():
	try:
		config = Config.PluginConfig(databaseConfigurationFilename)
		backend = config.getOption('Config', 'backend', 'DatabaseManagerSqlite')
		return backend
	except:
		raise #probably should have something better here. just rethrow for now.
	finally:
		del config

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
	
	def reconnect(self):
		self.isConnected = False
		del self.engine
		self.connect()
	
	def dbsession(self):
		return sqlalchemy.orm.sessionmaker(bind=self.engine, autocommit=False, autoflush=False)()
		
	def session(self):
		return DatabaseSession.SessionManager(self)
			
	@abc.abstractmethod
	def readConfiguration(self):
		pass
