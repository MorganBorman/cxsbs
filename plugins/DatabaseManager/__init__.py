from cxsbs.Plugin import Plugin

class DatabaseManager(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass

import cxsbs
DatabaseManagerBase = cxsbs.getResource("DatabaseManagerBase")

import sys
from contextlib import contextmanager

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

def init():
	global dbmanager
	dbmanager = initializeDatabaseManager()
	dbmanager.connect()
