import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global dbmanager
		dbmanager = initializeDatabaseManager()
		dbmanager.connect()
		
	def unload(self):
		pass

import cxsbs
DatabaseManagerBase = cxsbs.getResource("DatabaseManagerBase")

import sys
from contextlib import contextmanager

def getDbSettingsCategory():
	return DatabaseManagerBase.databaseConfigurationFilename

def initializeDatabaseManager():
	"""returns the correct DatabaseManager instance"""
	backendName = DatabaseManagerBase.getBackendName()
	
	DatabaseManagerBackendModule = cxsbs.getResource(backendName)
	try:
		DatabaseManagerBackendClass = DatabaseManagerBackendModule.__getattribute__("DatabaseManagerBackend")
	except AttributeError:
		raise MissingResourceComponent(backendName, "DatabaseManagerBackend", "class")
	
	if not issubclass(DatabaseManagerBackendClass, DatabaseManagerBase.DatabaseManagerBackend):
		raise InvalidResourceComponent(backendName, "DatabaseManagerBackend", "class")
		
	return DatabaseManagerBackendClass()

@contextmanager
def dbsession():
	session = dbmanager.session()
	try:
		yield session
	finally:
		session.close()
