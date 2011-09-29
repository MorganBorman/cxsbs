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
		
from sqlalchemy.exc import InvalidRequestError, OperationalError

class SessionManager:
	def __init__(self, dbmanager):
		self.dbmanager = dbmanager
		self.dbsession = self.dbmanager.dbsession()
		
	def session(self):
		return self.dbsession
		
	def query(self, *args, **kwargs):
		try:
			q = self.dbsession.query(*args, **kwargs)
			
		except (OperationalError, InvalidRequestError):
			self.dbmanager.reconnect()
			self.dbsession = self.dbmanager.dbsession()
			q = self.dbsession.query(*args, **kwargs)
			
		return q
		
	def add(self, *args, **kwargs):
		self.dbsession.add(*args, **kwargs)
		
	def delete(self, *args, **kwargs):
		self.dbsession.delete(*args, **kwargs)
		
	def commit(self, *args, **kwargs):
		self.dbsession.commit(*args, **kwargs)
		
	def close(self, *args, **kwargs):
		self.dbsession.close(*args, **kwargs)
