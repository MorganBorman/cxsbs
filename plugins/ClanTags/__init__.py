import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global tags, refreshTags
		tags = {}
		refreshTags = False
		
		tagsUpdater = LoopingCall(updateTags)
		tagsUpdater.start(1)
		
		refreshTags = True
		
	def unload(self):
		pass
		
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from twisted.internet.task import LoopingCall

import string, time

Base = declarative_base()

import cxsbs
Players = cxsbs.getResource("Players")
DatabaseManager = cxsbs.getResource("DatabaseManager")
BanCore = cxsbs.getResource("BanCore")
Colors = cxsbs.getResource("Colors")
Events = cxsbs.getResource("Events")
Timers = cxsbs.getResource("Timers")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Messages = cxsbs.getResource("Messages")

pluginCategory = 'ClanTags'

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="max_warnings", 
												displayName="Maximum warnings", 
												default=5,
												doc="Number of warnings to give before kicking a player using a reserved clantag."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="warning_interval", 
												displayName="Warning interval", 
												default=5,
												doc="Amount of time between warnings about using a reserved clantag."
											))

settings = SettingsManager.getAccessor(pluginCategory, "General")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="clantag_reserved", 
						displayName="Clantag reserved", 
						default="${warning}You're are using a reserved clan tag; ${blue}${tag}${white}. You have ${red}${remaining}${white} seconds to login or be kicked.", 
						doc="Message to print when a player has violated the sanctity of a clantag without proper credentials."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="clantags_reserved", 
						displayName="Clantag reserved", 
						default="${warning}You're are using reserved clan tags; ${tags}${white}. You have ${red}${remaining}${white} seconds to login or be kicked.", 
						doc="Message to print when a player has violated the sanctity of several clantags without proper credentials."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="table_name", 
												displayName="Table name", 
												default="clantags",
												doc="Table name for storing the clantag-group associations."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

class ClanTag(Base):
	'''Associates a tag with a group, permitting only those in the group to have the clantag in their name'''
	__tablename__ = tableSettings["table_name"]
	id = Column(Integer, primary_key=True)
	tag = Column(String(16), index=True)
	group = Column(String(16), index=True)
	def __init__(self, tag, group):
		self.tag = tag
		self.group = group

Base.metadata.create_all(DatabaseManager.dbmanager.engine)

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
	tags.clear()
	session = DatabaseManager.dbmanager.session()
	try:
		groupTags = session.query(ClanTag).all()
		for tag in groupTags:
			if not tag.tag in tags.keys():
				tags[tag.tag] = []
			tags[tag.tag].append(tag.group)
	finally:
		session.close()

def warnTagsReserved(cn, count, startTime=None):
	try:
		p = Players.player(cn)
	except ValueError:
		return
	
	if startTime == None:
		startTime = time.time()
		p.gamevars['tagWarningStartTime'] = startTime
	elif not 'tagWarningStartTime' in p.gamevars.keys():
		p.gamevars['tagWarningStartTime'] = startTime
		
	if startTime != p.gamevars['tagWarningStartTime']:
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
	
	if len(disallowedTags) < 1:
		return
	
	if count >= settings["max_warnings"]:
		BanCore.addBan(cn, 30, 'Use of reserved clan tag', -1)
		return
	
	remaining = (settings["max_warnings"]*settings["warning_interval"]) - (count*settings["warning_interval"])
	if len(disallowedTags) > 1:
		messager.sendMessage('clantags_reserved', dictionary={'tag':', '.join(disallowedTags), 'remaining':remaining})
	else:
		messager.sendMessage('clantag_reserved', dictionary={'tag':disallowedTags[0], 'remaining':remaining})
	Timers.addTimer(settings["warning_interval"]*1000, warnTagsReserved, (cn, count+1, startTime))
	
@Events.eventHandler('player_name_changed')	
@Events.eventHandler('player_connect_delayed')
def onPlayerActive(*args):
	"""Trigger checks on tags to see whether the player must validate to use them."""
	if len(args) < 1:
		return
	cn = args[0]
	Timers.addTimer(2*1000, warnTagsReserved, (cn, 0))
	