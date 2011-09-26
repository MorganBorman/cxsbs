from cxsbs.Plugin import Plugin

class ClanTags(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		global tags, refreshTags
		tags = {}
		refreshTags = False
		
		self.init_config()
		self.init_tables()
		
		tagsUpdater = LoopingCall(updateTags)
		tagsUpdater.start(60)
		
		refreshTags = True
		
	def reload(self):
		self.init_config()
		
	def unload(self):
		pass
		
	def init_tables(self):
		config = Config.PluginConfig('db')
		tableName = config.getOption('ClanTags', 'table_name', 'clantags')
		del config
		
		global ClanTag
		class ClanTag(Base):
			'''Associates a tag with a group, permitting only those in the group to have that in their name'''
			__tablename__ = tableName
			id = Column(Integer, primary_key=True)
			tag = Column(String(16), index=True)
			group = Column(String(16), index=True)
			def __init__(self, tag, group):
				self.tag = tag
				self.group = group
		
		Base.metadata.create_all(DatabaseManager.dbmanager.engine)
		
	def init_config(self):
		config = Config.PluginConfig('ClanTags')
		max_warnings = config.getIntOption('Config', 'max_warnings', 5)
		warning_interval = config.getIntOption('Config', 'warning_interval', 5)
		del config
		
		global messageModule
		messageModule = MessageFramework.MessagingModule()
		messageModule.addMessage("clantag_reserved", "${warning}You're are using a reserved clan tag; ${blue}${tag}${white}. You have ${red}${remaining}${white} seconds to login or be kicked.", "ClanTags")
		messageModule.addMessage("clantags_reserved", "${warning}You're are using reserved clan tags; ${tags}${white}. You have ${red}${remaining}${white} seconds to login or be kicked.", "ClanTags")
		messageModule.finalize()
		
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from twisted.internet.task import LoopingCall

import cxsbs
Players = cxsbs.getResource("Players")
DatabaseManager = cxsbs.getResource("DatabaseManager")
BanCore = cxsbs.getResource("BanCore")
Colors = cxsbs.getResource("Colors")
Events = cxsbs.getResource("Events")
Timers = cxsbs.getResource("Timers")
Config = cxsbs.getResource("Config")
MessageFramework = cxsbs.getResource("MessageFramework")

import string

Base = declarative_base()

def hasWord(word, text):
	return findWord(word, text) != None
	
def findWord(word, text):
	start = text.lower().find(word.lower())
	if start != -1:
		return (start, start+len(word))
	else:
		return None

def stripTags(name):
	for tag in tags.keys():
		name = string.replace(name, tag, '')
	return name
	
def getTags(name):
	nameTags = {}
	for tag in tags.keys():
		if hasWord(tag, name):
			nameTags[tag] = tags[tag]
	return nameTags
	
def updateTags():
	global refreshTags
	if not refreshTags:
		return
	global tags
	tags['[FD]'] = ["__admin__", "__master__"]

def warnTagReserved(cn, count, startTime=None):
	try:
		p = Players.player(cn)
	except ValueError:
		return
	
	if startTime == None:
		startTime = time.time()
		p.tagWarningStartTime = startTime
		
	if startTime != p.tagWarningStartTime:
		return
	
	playerGroups = p.groups()
	playerTags = getTags(p.name())
	
	disallowedTags = []
	
	for tag, tagGroups in playerTags.items():
		allowed = False
		for group in playerGroups:
			if group in tagGroups:
				allowed = True
		if not allowed:
			disallowedTags.append(tag)
	
	if len(disallowTags) < 1:
		return
	
	if count > max_warnings:
		BanCore.addBan(cn, 0, 'Use of reserved clan tag', -1)
		return
	
	remaining = (max_warnings*warning_interval) - (count*warning_interval)
	if len(disallowedTags) > 1:
		messageModule.sendMessage('clantags_reserved', dictionary={'tag':', '.join(disallowedTags), 'remaining':remaining})
	else:
		messageModule.sendMessage('clantag_reserved', dictionary={'tag':disallowedTags[0], 'remaining':remaining})
	Timers.addTimer(warning_interval*1000, warnTagReserved, (cn, count+1, startTime))
	