import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
		
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from twisted.internet.task import LoopingCall

import string, time, gc

#gc.set_debug(gc.DEBUG_LEAK)

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
Commands = cxsbs.getResource("Commands")

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

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="case_sensitive", 
												displayName="Case sensitive", 
												default=False,
												doc="Should reservation of names be case sensitive."
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

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="tag_add_success", 
						displayName="Tag add success", 
						default="${info}Tag-group association added for tag ${blue}${tag}${white} and group ${blue}${groupName}${white}.", 
						doc="Message to print when a player added a tag-group association."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="removed_association_none", 
						displayName="Removed clantag association none", 
						default="${info}No matching clantag-group associations were found to remove.", 
						doc="Message to print when a player tries to remove clantag-group associations that do not exist."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="removed_association_one", 
						displayName="Removed clantag association one", 
						default="${info}Removed one clantag association for tag ${blue}${tag}${white} and group ${blue}${groupName}${white}.", 
						doc="Message to print when a player removes a clantag-group association."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="removed_association_many", 
						displayName="Removed clantag associations", 
						default="${info}Removed the clantag associations for tag ${blue}${tag}${white} and the groups ${blue}${groupNames}${white}.", 
						doc="Message to print when a player removes several clantag-group associations."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="table_name", 
												displayName="Table name", 
												default="usermanager_clantags",
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

import textSearchUtils

def stripTags(name):
	tags = getTags(name)
	for tag in tags.keys():
		name = textSearchUtils.replaceWord(tag, "", name, caseSensitive=settings["case_sensitive"])
	return name

def getTags(name):
	nameTags = {}
	
	session = DatabaseManager.dbmanager.session()
	try:
		if settings["case_sensitive"]:
			tags = session.query("id", "tag", "group").from_statement("SELECT * FROM clantags where :name like '%' || tag || '%'").params(name=name).all()
		else:
			tags = session.query("id", "tag", "group").from_statement("SELECT * FROM clantags where :name like '%' || lower(tag) || '%'").params(name=name.lower()).all()
		
		for tag in tags:
			if not tag.tag in nameTags.keys():
				nameTags[tag.tag] = []
			nameTags[tag.tag].append(tag.group)
	finally:
		session.close()

	return nameTags

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
		messager.sendPlayerMessage('clantags_reserved', p, dictionary={'tags':', '.join(disallowedTags), 'remaining':remaining})
	else:
		messager.sendPlayerMessage('clantag_reserved', p, dictionary={'tag':disallowedTags[0], 'remaining':remaining})
	Timers.addTimer(settings["warning_interval"]*1000, warnTagsReserved, (cn, count+1, startTime))
	
@Events.eventHandler('player_name_changed')	
@Events.eventHandler('player_connect_delayed')
def onPlayerActive(*args):
	"""Trigger checks on tags to see whether the player must validate to use them."""
	if len(args) < 1:
		return
	cn = args[0]
	Timers.addTimer(3*1000, warnTagsReserved, (cn, 0))
	
@Commands.commandHandler('addtag')
def onAddTagCommand(cn, args):
	'''
	@description Add a group tag association
	@usage <tag> <group>
	@allowGroups __admin__
	@denyGroups
	@doc Add a tag entry for a particular group.
	'''
	args = args.split()
	if len(args) != 2:
		raise Commands.UsageError()
	
	tagString = args[0]
	groupName = args[1]
		
	session = DatabaseManager.dbmanager.session()
	try:
		tag = ClanTag(tagString, groupName)
		session.add(tag)
		session.commit()
		messager.sendPlayerMessage('tag_add_success', Players.player(cn), dictionary={'tag': tagString, 'groupName': groupName})
	finally:
		session.close()

@Commands.commandHandler('deltag')
def onDelTagCommand(cn, args):
	'''
	@description Delete a tag-group association
	@usage <tag> (group)
	@allowGroups __admin__
	@denyGroups
	@doc Remove the tag entry for a particular group.
	'''
	args = args.split()
	if len(args) < 1:
		raise Commands.UsageError()
	elif len(args) == 1:
		tagString = args[0]
		groupName = None
	elif len(args) >= 2:
		tagString = args[0]
		groupName = args[1]
		
	removedGroups = []
	
	session = DatabaseManager.dbmanager.session()
	try:
		if groupName == None:
			groupTags = session.query(ClanTag).filter(ClanTag.tag==tagString).all()
		else:
			groupTags = session.query(ClanTag).filter(ClanTag.tag==tagString).filter(ClanTag.group==groupName).all()
			
		for tag in groupTags:
			removedGroups.append(tag.group)
			session.delete(tag)
			session.commit()
		session.commit()
		
		if len(removedGroups) < 1:
			messager.sendPlayerMessage('removed_association_none', Players.player(cn), dictionary={'tag': tagString})
		if len(removedGroups) == 1:
			messager.sendPlayerMessage('removed_association_one', Players.player(cn), dictionary={'tag': tagString, 'groupName': removedGroups[0]})
		else:
			groupNames = ', '.join(removedGroups[:-1]) + ', and ' + removedGroups[-1]
			messager.sendPlayerMessage('removed_association_many', Players.player(cn), dictionary={'tag': tagString, 'groupNames': groupNames})
	finally:
		session.close()