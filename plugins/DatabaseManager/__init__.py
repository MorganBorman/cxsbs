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
Config = cxsbs.getResource("Config")

import sys
from contextlib import contextmanager

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

def uriBeginsWithQuote(uri):
	if len(uri) < 1:
		return False
	return (uri[0] == "'" or uri[0] == "\"")

def isProtocol(uri, protocolName):
	offset = 0
	if (uriBeginsWithQuote(uri)):
		offset = 1
	delimiterPosition = uri.find("://")
	uriBeginPosition = uri.find(protocolName)
	return uriBeginPosition >= offset and uriBeginPosition < delimiterPosition

def initializeDatabaseManager():
	"""returns the correct DatabaseManager instance"""
	protocol = getProtocol()
	
	if isProtocol(protocol, "sqlite"):
		DatabaseManagerSqlite = cxsbs.getResource("DatabaseManagerSqlite")
		return DatabaseManagerSqlite.SqliteManager()
	elif isProtocol(protocol, "informix"):
		DatabaseManagerInformix = cxsbs.getResource("DatabaseManagerInformix")
		return DatabaseManagerInformix.InformixManager()
	else:
		sys.stderr.write("Unable to create database engine for Protocol: " + protocol + "\n")
		sys.exit(1);

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
