from cxsbs.Plugin import Plugin

class DatabaseManagerBase(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass

import cxsbs
DatabaseSession = cxsbs.getResource("DatabaseSession")

from sqlalchemy.orm import sessionmaker

import abc
	
class DatabaseManager(object):
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
		return sessionmaker(bind=self.engine, autocommit=False, autoflush=False)()
		
	def session(self):
		return DatabaseSession.SessionManager(self)
			
	@abc.abstractmethod
	def readConfiguration(self):
		pass
