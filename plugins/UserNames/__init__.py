import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
		
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql.expression import func

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
Commands = cxsbs.getResource("Commands")
ClanTags = cxsbs.getResource("ClanTags")
Users = cxsbs.getResource("Users")
UserModel = cxsbs.getResource("UserModel")

pluginCategory = 'UserNames'

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="max_warnings", 
												displayName="Maximum warnings", 
												default=5,
												doc="Number of warnings to give before kicking a player using a reserved name."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="warning_interval", 
												displayName="Warning interval", 
												default=5,
												doc="Amount of time between warnings about using a reserved name."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="max_names", 
												displayName="Max names", 
												default=2,
												doc="Maximum number of names a user may reserve."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="case_sensitive", 
												displayName="Case sensitive", 
												default=False,
												doc="Should reservation of names be case sensitive."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="reserve_superstrings", 
												displayName="Reserve superstrings", 
												default=True,
												doc="Should reservation of names also reserve all names containing that name. Be careful about having this enabled with a small minimum name length."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="minimum_length", 
												displayName="Minimum length", 
												default=5,
												doc="What should be the minimum name length which is permitted to be registered."
											))

settings = SettingsManager.getAccessor(pluginCategory, "General")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="name_reserved", 
						displayName="name reserved", 
						default="${warning}You're are using a reserved name, ${blue}${name}${white}. You have ${red}${remaining}${white} seconds to login or be kicked.", 
						doc="Message to print when a player has violated the sanctity of another's name without proper credentials."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="substring_reserved", 
						displayName="Substring reserved", 
						default="${warning}Your name contains a reserved name, ${blue}${name}${white}. You have ${red}${remaining}${white} seconds to login or be kicked.", 
						doc="Message to print when a player has violated the sanctity of several clantags without proper credentials."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="name_add_success", 
						displayName="name add success", 
						default="${info}The name ${blue}${name}${white} is now associated with your account, ${blue}${email}${white}.", 
						doc="Message to print when a player added a name reservation."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="name_add_failure_taken", 
						displayName="name add failure taken", 
						default="${error}The name ${blue}${name}${white} or a substring thereof is already reserved by another user.", 
						doc="Message to print when a name reservation fails due to the name or a substring of the name already being reserved."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="name_add_failure_short", 
						displayName="name add failure short", 
						default="${error}The name ${blue}${name}${white} is too short, reserved names must be at least ${yellow}${length}${white} characters.", 
						doc="Message to print when a name reservation fails due to the name being too short."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="name_remove_success", 
						displayName="Name remove success", 
						default="${info}The name ${blue}${name}${white} has been disassociated with your account, ${blue}${email}${white}.", 
						doc="Message to print when a player removes a name reservation."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="name_remove_failure", 
						displayName="Name remove failure", 
						default="${error}Failed to disassociate the name ${blue}${name}${white} from your account.", 
						doc="Message to print when a player fails to remove a name reservation."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="set_primary_success", 
						displayName="set primary success", 
						default="${info}Your primary user name is now set to ${name}.", 
						doc="Message to when a players primary user name changes."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="table_name", 
												displayName="Table name", 
												default="usermanager_names",
												doc="Table name for storing the user name reservations."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

class UserName(Base):
	'''Associates a tag with a group, permitting only those in the group to have the clantag in their name'''
	__tablename__ = tableSettings["table_name"]
	id = Column(Integer, primary_key=True)
	name = Column(String(16), index=True)
	userId = Column(Integer, index=True)
	primary = Column(Boolean, nullable=False)
	def __init__(self, name, userId, primary=False):
		self.name = name
		self.userId = userId
		self.primary = primary

Base.metadata.create_all(DatabaseManager.dbmanager.engine)

def getDisplayName(userId):
	if not hasName(userId):
		return "Unidentified"
	if not hasPrimaryName(userId):
		session = DatabaseManager.dbmanager.session()
		try:
			name = session.query(UserName).filter(UserName.userId==userId).first()
			return name.name
		finally:
			session.close()
	else:
		session = DatabaseManager.dbmanager.session()
		try:
			name = session.query(UserName).filter(UserName.userId==userId).filter(UserName.primary==True).one()
			return name.name
		finally:
			session.close()
		
def hasName(userId):
	session = DatabaseManager.dbmanager.session()
	try:
		session.query(UserName).filter(UserName.userId==userId).one()
		return True
	except MultipleResultsFound:
		return True
	except NoResultFound:
		return False
	finally:
		session.close()
		
def hasPrimaryName(userId):
	session = DatabaseManager.dbmanager.session()
	try:
		session.query(UserName).filter(UserName.userId==userId).filter(UserName.primary==True).one()
		return True
	except MultipleResultsFound:
		return True
	except NoResultFound:
		return False
	finally:
		session.close()
		
def setNonePrimary(userId):
	session = DatabaseManager.dbmanager.session()
	try:
		names = session.query(UserName).filter(UserName.userId==userId).filter(UserName.primary==True).all()
		for name in names:
			name.primary = False
			session.add(name)
		session.commit()
	finally:
		session.close()
		
def isNamePermitted(name, userId=None):
	session = DatabaseManager.dbmanager.session()
	try:
		if settings['reserve_superstrings']:
			if settings["case_sensitive"]:
				userNames = session.query("id", "name", "userId", "primary").from_statement("SELECT * FROM " + tableSettings["table_name"] + " where :name like '%' || name || '%'").params(name=name).all()
			else:
				userNames = session.query("id", "name", "userId", "primary").from_statement("SELECT * FROM " + tableSettings["table_name"] + " where :name like '%' || lower(name) || '%'").params(name=name.lower()).all()
		else:
			query = session.query(UserName)
			if settings["case_sensitive"]:
				query = query.filter(func.lower(UserName.name).like(name.lower()))
			else:
				query = query.filter(UserName.name==name)
				
			userNames = query.all()
			
		permitted = False
		for userName in userNames:
			if userId == userName.userId:
				permitted = True
		return permitted
	finally:
		session.close()

def warnNameReserved(cn, count, startTime=None):
	try:
		p = Players.player(cn)
	except ValueError:
		return
	
	if startTime == None:
		startTime = time.time()
		p.gamevars['nickWarningStartTime'] = startTime
	elif not 'nickWarningStartTime' in p.gamevars.keys():
		p.gamevars['nickWarningStartTime'] = startTime
		
	if startTime != p.gamevars['nickWarningStartTime']:
		return
	
	try:
		userId = p.userId
	except:
		userId = None
	
	playerNick = ClanTags.stripTags(p.name())
	
	if isNamePermitted(playerNick, userId=userId):
		return
	
	if count > settings["max_warnings"]:
		BanCore.addBan(cn, 0, 'Use of reserved name', -1)
		return
	
	remaining = (settings["max_warnings"]*settings["warning_interval"]) - (count*settings["warning_interval"])
	messager.sendPlayerMessage('name_reserved', p, dictionary={'name':playerNick, 'remaining':remaining})
	Timers.addTimer(settings["warning_interval"]*1000, warnNameReserved, (cn, count+1, startTime))
	
@Events.eventHandler('player_name_changed')	
@Events.eventHandler('player_connect')
def onPlayerActive(*args):
	"""Trigger checks on tags to see whether the player must validate to use them."""
	if len(args) < 1:
		return
	cn = args[0]
	Timers.addTimer(3*1000, warnNameReserved, (cn, 0))
	
@Commands.commandHandler('reservename')
def onReserveNameCommand(cn, args):
	'''
	@threaded
	@description Stake a name reservation
	@usage <name>
	@allowGroups __user__
	@denyGroups
	@doc Stake a name reservation
	'''
	args = args.split()
	if len(args) != 1:
		raise Commands.UsageError()
	
	if not Users.isLoggedIn(cn):
		raise Commands.UsageError("You must be logged in to use this command.")
	
	u = Players.player(cn)
	
	userId = u.userId
	nameString = args[0]
	
	if not UserModel.model.isUser(userId):
		raise Commands.StateError("You're caught in limbo... you have a user object but no valid user entry in the user model. Tell an administrator about this.")
	
	if not isNamePermitted(nameString, userId):
		messager.sendPlayerMessage('name_add_failure_taken', u, dictionary={'name': nameString})
		return
		
	if len(nameString) < settings['minimum_length']:
		messager.sendPlayerMessage('name_add_failure_short', u, dictionary={'name': nameString, 'length': settings['minimum_length']})
		return
	
	primary = not hasPrimaryName(userId)

	session = DatabaseManager.dbmanager.session()
	try:
		userName = UserName(nameString, userId, primary=primary)
		session.add(userName)
		session.commit()
		messager.sendPlayerMessage('name_add_success', u, dictionary={'name': nameString, 'email': UserModel.model.getUserEmail(userId)})
	finally:
		session.close()

@Commands.commandHandler('releasename')
def onReleaseNameCommand(cn, args):
	'''
	@threaded
	@description Relinquish a name reservation
	@usage <name>
	@allowGroups __user__
	@denyGroups
	@doc Relinquish a name reservation
	'''
	args = args.split()
	if len(args) < 1:
		raise Commands.UsageError()
	
	if not Users.isLoggedIn(cn):
		raise Commands.StateError("You must be logged in to use this command.")
	
	u = Players.player(cn)
	
	userId = u.userId
	nameString = args[0]
	
	if not UserModel.model.isUser(userId):
		raise Commands.StateError("You're caught in limbo... you have a user object but no valid user entry in the user model. Tell an administrator about this.")
	
	session = DatabaseManager.dbmanager.session()
	try:
		names = session.query(UserName).filter(UserName.userId==userId).filter(UserName.name==nameString).all()
		removedName = ""
		for name in names:
			removedName = name.name
			session.delete(name)
		session.commit()
		messager.sendPlayerMessage('name_remove_success', u, dictionary={'name': removedName, 'email': UserModel.model.getUserEmail(userId)})
	finally:
		session.close()
		
@Commands.commandHandler('displayname')
def onDisplayNameCommand(cn, args):
	'''
	@threaded
	@description Set the primary display name to the specified name
	@usage <name>
	@allowGroups __user__
	@denyGroups
	@doc Set the primary display name to the specified name. Will add the name as a user name if it is not found.
	'''
	args = args.split()
	if len(args) != 1:
		raise Commands.UsageError()
	
	if not Users.isLoggedIn(cn):
		raise Commands.StateError("You must be logged in to use this command.")
	
	u = Players.player(cn)
	
	userId = u.userId
	nameString = args[0]
	
	if not UserModel.model.isUser(userId):
		raise Commands.StateError("You're caught in limbo... you have a user object but no valid user entry in the user model. Tell an administrator about this.")
	
	setNonePrimary(userId)
	
	session = DatabaseManager.dbmanager.session()
	try:
		name = session.query(UserName).filter(UserName.userId==userId).filter(UserName.name==nameString).one()
		name.primary = True
		session.add(name)
		session.commit()
		messager.sendPlayerMessage('set_primary_success', u, dictionary={'name': nameString})
	except NoResultFound:
		raise Commands.StateError("That name does not seem to be reserved by your account.")
	finally:
		session.close()