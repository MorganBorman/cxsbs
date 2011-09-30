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
	
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint
	
Base = declarative_base()
	
import ppwgen, time

import cxsbs
UserModelBase = cxsbs.getResource("UserModelBase")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
DatabaseManager = cxsbs.getResource("DatabaseManager")
Auth = cxsbs.getResource("Auth")
Email = cxsbs.getResource('Email')

pluginCategory = 'Users'

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="user_table", 
												displayName="User table", 
												default="usermanager_users",
												doc="Table name for storing the users."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="user_verifications_table", 
												displayName="User verifications table", 
												default="usermanager_user_verifications",
												doc="Table name for storing the pending user verifications."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="linked_names_table", 
												displayName="Linked names table", 
												default="usermanager_nickaccounts",
												doc="Table name for storing the user's linked names."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="groups_table", 
												displayName="Groups table", 
												default="usermanager_groups",
												doc="Table name for storing the user groups."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="group_members_table", 
												displayName="Group members table", 
												default="usermanager_group_members",
												doc="Table name for storing the user-group associations."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

class User(Base):
	__tablename__ = tableSettings["user_table"]
	id = Column(Integer, primary_key=True)
	name = Column(String(16), index=True)
	email = Column(String(64), nullable=False)
	publicToken = Column(String(16), index=True)
	def __init__(self, name, email, publicToken):
		self.name = name
		self.email = email
		self.publicToken = publicToken
		
class Verification(Base):
	__tablename__ = tableSettings["user_verifications_table"]
	id = Column(Integer, primary_key=True)
	name = Column(String(16), index=True)
	verificationCode = Column(String(32), index=True)
	email = Column(String(64), nullable=False)
	type = Column(String(32), nullable=False)
	time = Column(Integer, nullable=False)
	userId = Column(Integer, nullable=True)
	tokenSeed = Column(String(32), nullable=True)
	def __init__(self, name, verificationCode, email, type, time, userId, tokenSeed):
		self.name = name
		self.verificationCode = verificationCode
		self.email = email
		self.type = type
		self.time = time
		self.userId = userId
		self.tokenSeed = tokenSeed

class NickAccount(Base):
	__tablename__ = tableSettings["linked_names_table"]
	id = Column(Integer, primary_key=True)
	name = Column(String(16), index=True)
	userId = Column(Integer, ForeignKey(tableSettings["user_table"] + '.id'))
	user = relation(User, primaryjoin=userId==User.id)
	def __init__(self, name, userId):
		self.name = name
		self.userId = userId
		
class Group(Base):
	__tablename__ = tableSettings["groups_table"]
	id = Column(Integer, primary_key=True)
	name = Column(String(16), index=True)
	def __init__(self, name):
		self.name = name
		
class UserGroup(Base):
	__tablename__ = tableSettings["group_members_table"]
	userId = Column(Integer, ForeignKey(tableSettings["user_table"] + '.id'))
	groupId = Column(Integer, ForeignKey(tableSettings["groups_table"] + '.id'))
	user = relation(User, primaryjoin=userId==User.id)
	UniqueConstraint('ip', 'name', name='uq_user_ip_ip_name')
	__mapper_args__ = {'primary_key':[userId, groupId]}
	def __init__(self, userId, groupId):
		self.userId = userId
		self.groupId = groupId
		
Base.metadata.create_all(DatabaseManager.dbmanager.engine)
	
class Model(UserModelBase.Model):
	def __init__(self, readOnly, usernameValidator, authenticationTokenValidator, groupValidator, maxNicks):
		UserModelBase.Model.__init__(self, readOnly, usernameValidator, authenticationTokenValidator, groupValidator, maxNicks)
		
	def isNickAllowed(self, userName, userId=None):
		"""Check if a name may be used by an individual
		
		userName: username to check
		userId: the unique id of the user (None if not logged in)
		
		Returns whether or not a name is reserved
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			userAccount = session.query(User).filter(User.name==userName).one()
			if userAccount.id != userId:
				return False
		except NoResultFound:
			pass
		finally:
			session.close()
		
		session = DatabaseManager.dbmanager.session()
		try:
			nickAccount = session.query(NickAccount).filter(NickAccount.name==userName).one()
			if nickAccount.userId != userId:
				return False
		except NoResultFound:
			pass
		finally:
			session.close()
			
		return True
	
	def associateNick(self, userName, userId):
		"""associate additional names with a user account
		
		userName: username to associate
		userId: the unique id of the user
		
		raises InvalidUserId if the user does not exist
		raises NameConflict when logical
		raises SingleNickSystem if this model does not support multiple nicks
		raises NickLimitExceeded if the limit on the number of nicks has been exceeded
		raises InvalidUserName if the name is not canonical
		raises ReadOnlyViolation if user model is read only
		
		no return value
		"""
		if self.readOnly:
			raise ReadOnlyViolation()
		
		#validate the userId
		self.isUser(userId)
		
		if self.maxNicks <= 1:
			raise SingleNickSystem()
		
		if not self.isNickAllowed(userName, userId):
			raise NameConflict()
		
		session = DatabaseManager.dbmanager.session()
		try:
			nickAccounts = session.query(NickAccount).filter(NickAccount.id==userId).all()
			if len(nickAccounts)+1 > self.maxNicks:
				raise NickLimitExceeded()
		finally:
			session.close()
			
		if not (self.usernameValidator(userName)):
			raise UserModelBase.InvalidUserName()
		
		session = DatabaseManager.dbmanager.session()
		try:
			session.query(NickAccount).filter(NickAccount.name==userName).one()
			raise NameConflict()
		except NoResultFound:
			nickAccount = NickAccount(userName, userId)
			session.add(nickAccount)
			session.commit()
		except MultipleResultsFound:
			raise NameConflict()
		finally:
			session.close()
	
	def validate(self, userName, verificationCode):
		"""called to finalize an action requiring email verification
		
		actions:
			validate a users account, generate authkeys, and email the private authkey + instructions to the user
			validate account deletion, and send successful deletion email
			validate password change, generate authkeys and email the private authkey + instructions to the user
		
		raises InvalidUserName if the name does not relate to a pending validation
		raises InvalidVerification if the verificationCode was incorrect
		
		no return value
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			verification = session.query(Verification).filter(Verification.name==userName).filter(Verification.verificationCode==verificationCode).one()
		except NoResultFound:
			raise UserModelBase.InvalidVerification()
		except MultipleResultsFound:
			raise InvalidState("duplicate verification entries for userName:" + userName)
		finally:
			session.close()
			
		if verification.type == "createAccount":
			self.__createFinalize(verification)
			
		elif verification.type == "deleteAccount":
			self.__deleteFinalize(verification)
			
		elif verification.type == "changeAccountKey":
			self.__changeFinalize(verification)
			
		else:
			raise InvalidState("unkown verification type: " + verification.type)
		
	def __createFinalize(self, verification):
		session = DatabaseManager.dbmanager.session()
		try:
			keypair = Auth.genKeyPair(verification.tokenSeed)
			try:
				Email.send_templated_email	(
												symbolicName='login_instructions', 
												email=verification.email, 
												domain=Auth.settings["automatic_request_description"], 
												userName=verification.name,
												privateKey=keypair[0],
												publicKey=keypair[1],
												administrativeEmail=Email.settings['administrative_email'],
												serverClusterName="Forgotten Dream",
												initiatedTime=verification.time,
												)
			except:
				pass
			
			user = User(verification.name, verification.email, keypair[1])
			session.delete(verification)
			session.add(user)
			session.commit()
			
		finally:
			session.close()
	
	def __deleteFinalize(self, verification):
		pass
		
	def __changeFinalize(self, verification):
		pass
	
	def login(self, userId, serverId):
		"""to be called when user logs in to a server
		
		userId: the unique id of the user
		serverId: the unique id of the server that this is being called from
		
		raises InvalidUserId if the user does not exist
		does not validate serverId. This is the responsibility of the calling api
		
		returns (loginSuccessfulBoolean, loginMessage)
		"""
		#validate the userId
		self.isUser(userId)
		
		return (True, "Welcome")
		
	def logout(self, userId, serverId):
		"""to be called when user logs out of a server
		
		userId: the unique id of the user
		serverId: the unique id of the server that this is being called from
		
		raises InvalidUserId if the user does not exist
		raises InvalidState if the user is not logged into the given server
		
		returns (logoutSuccessfulBoolean, loginMessage)
		"""
		#validate the userId
		self.isUser(userId)
		
		return (True, "Goodbye")
	
	def isUser(self, userId):
		"""Check whether a userId is valid
		
		userId: the unique user identifier to check
		
		raises InvalidUserId if the user does not exist
		
		no return value
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			session.query(User).filter(User.id==userId).one()
		except:
			raise InvalidUserId(userId)
		finally:
			session.close()
		
	def getUser(self, userName):
		"""Get the user id of a user by primary username
		
		userName: username to check
		
		raises InvalidUserName if the name does not relate to an account
		
		Returns the userId
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			user = session.query(User).filter(User.name==userName).one()
			return user.id
		except:
			raise UserModelBase.InvalidUserName(userName)
		finally:
			session.close()
	
	def getUserPublicKey(self, userId):
		"""Get the users public key
		
		userId: the unique user identifier
		
		raises InvalidUserId if the user does not exist
		
		Returns the public key as a string
		"""
		
		session = DatabaseManager.dbmanager.session()
		try:
			user = session.query(User).filter(User.id==userId).one()
			return user.publicToken
		except:
			raise InvalidUserId(userId)
		finally:
			session.close()
	
	def getUserEmail(self, userId):
		"""Get the users email
		
		userId: the unique user identifier
		
		raises InvalidUserId if the user does not exist
		
		Returns the email address as a string
		"""
		
		session = DatabaseManager.dbmanager.session()
		try:
			user = session.query(User).filter(User.id==userId).one()
			return user.email
		except:
			raise InvalidUserId(userId)
		finally:
			session.close()
	
	def getUserNames(self, userId):
		"""Get the users names
		
		userId: the unique user identifier
		
		raises InvalidUserId if the user does not exist
		
		Returns a list with all the users names in it
		"""
		names = []
		
		session = DatabaseManager.dbmanager.session()
		try:
			user = session.query(User).filter(User.id==userId).one()
			names.append(user.name)
		except:
			raise InvalidUserId(userId)
		finally:
			session.close()
		
		session = DatabaseManager.dbmanager.session()
		try:
			nickAccounts = session.query(NickAccount).filter(NickAccount.id==userId).all()
			for nickAccount in nickAccounts:
				names.append(nickAccount.name)
		finally:
			session.close()
		return names
		
	def createUser(self, userName, email, authenticationTokenSeed):
		"""Queues a createAccountVerification for the given userName
		
		userName: desired user name
		authenticationTokenSeed: desired authentication token
		
		raises NameConflict when logical
		raises InvalidUserName if the name is not canonical
		raises InvalidEmail if the email is not canonical
		raises InvalidAuthenticationToken if the authentication token seed is not canonical
		raises ReadOnlyViolation if user model is read only
		
		no return value
		"""
		if self.readOnly:
			raise ReadOnlyViolation()
		
		verificationCode = ppwgen.generatePassword()
		
		verificationTime = time.time()
		try:
			Email.send_templated_email	(
									symbolicName='create_verification', 
									email=email, 
									userName=userName,
									verificationCode=verificationCode,
									administrativeEmail=Email.settings['administrative_email'],
									serverClusterName="Forgotten Dream",
									initiatedTime=verificationTime,
									)
		except:
			pass
		
		session = DatabaseManager.dbmanager.session()
		try:
			verification = Verification(userName, verificationCode, email, "createAccount", verificationTime, None, authenticationTokenSeed)
			session.add(verification)
			session.commit()
		finally:
			session.close()
	
	def deleteUser(self, userId):
		"""Queues a deleteAccountValidation the given user
		
		userId: the unique id of the user
		
		raises InvalidUserId if the user does not exist
		raises ReadOnlyViolation if the user model is read only
		
		no return value
		"""
		if self.readOnly:
			raise ReadOnlyViolation()
		
		#validate the userId
		self.isUser(userId)
		
		verificationCode = ppwgen.generatePassword()
		email = self.getUserEmail(userId)
		
		session = DatabaseManager.dbmanager.session()
		try:
			verification = Verification(None , verificationCode, email, "deleteAccount", time.time(), userId, None)
			session.add(verification)
			session.commit()
		finally:
			session.close()
	
	def changeUserAuthenticationToken(self, userId, authenticationTokenSeed):
		"""Queues an authenticationTokenChangeVerification for the given user
		
		userId: the unique id of the user
		
		raises InvalidUserId if the user does not exist
		raises InvalidAuthenticationTokenSeed if the authentication token seed is not canonical
		raises ReadOnlyViolation if the user model is read only
		
		no return value
		"""
		if self.readOnly:
			raise ReadOnlyViolation()
		
		#validate the userId
		self.isUser(userId)
		
		verificationCode = ppwgen.generatePassword()
		email = self.getUserEmail(userId)
		
		session = DatabaseManager.dbmanager.session()
		try:
			verification = Verification(None , verificationCode, email, "deleteAccount", time.time(), userId, authenticationTokenSeed)
			session.add(verification)
			session.commit()
		finally:
			session.close()
	
	def users(self, serverId=None, online=False, groupId=None):
		"""get the currently logged in users
		
		serverId: id of server to filter by (None = all servers)
		online: whether to only return online users
		groupId: id of group to filter by (None = all groups)
		
		raises InvalidGroupId if the group does not exist
		
		return the userIds as a list
		"""
		#validate the groupId
		if groupId != None:
			self.isGroup(groupId)
		
	def isGroup(self, groupId):
		"""Check whether a groupId is valid
		
		groupId: the unique group identifier to check
		
		raises InvalidGroupId if the user does not exist
		
		no return value
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			session.query(Group).filter(Group.id==groupId).one()
		except:
			raise InvalidGroupId(groupId)
		finally:
			session.close()
	
	def getGroup(self, groupName):
		"""get the group of the given name
		
		groupName: the name of the group
		
		raises InvalidGroupName if the group does not exist
		
		returns the groupId
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			group = session.query(Group).filter(Group.name==groupName).one()
			return group.id
		except:
			raise InvalidGroupName(groupName)
		finally:
			session.close()
	
	def getGroupName(self, groupId):
		"""Get the group name
		
		groupId: the unique group identifier
		
		raises InvalidGroupId if the group does not exist
		
		Returns the group name corresponding to the given id
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			group = session.query(Group).filter(Group.id==groupId).one()
			return group.name
		except:
			raise InvalidGroupId(groupId)
		finally:
			session.close()
	
	def createGroup(self, groupName):
		"""Create a group of the given name and return the groupId
		
		raises InvalidGroupName if the name is not canonical
		
		returns the groupId
		"""
		
		if self.readOnly:
			raise ReadOnlyViolation()
		
	def deleteGroup(self, groupId):
		"""Delete a group of the given name
		
		raises InvalidGroupId if the group does not exist
		
		no return value
		"""
		
		if self.readOnly:
			raise ReadOnlyViolation()
		
		#validate the groupId
		self.isGroup(groupId)
	
	def groups(self, userId):
		"""Get a users groups
		
		userId: the unique id of the user to filter by (None = list of all groups)
		
		raises InvalidUserId if the user does not exist
		
		Returns the groupIds of a user as a list
		"""
		
		#validate the userId
		self.isUser(userId)
		
		groups = []
		
		session = DatabaseManager.dbmanager.session()
		try:
			userGroups = session.query(UserGroup).filter(UserGroup.userId==userId).all()
			for user_group in userGroups:
				groups.append(self.getGroupName(user_group.groupId))
		finally:
			session.close()
			
		return groups
		
	def addToGroup(self, userId, groupId):
		"""Adds the given user to a particular group
		
		userId: the unique id of the user
		groupId: the unique id of the group
		
		raises InvalidUserId if the user does not exist
		raises ReadOnlyViolation if the user model is read only
		"""
		if self.readOnly:
			raise ReadOnlyViolation()
		
		#validate the userId
		self.isUser(userId)
		
		#validate the groupId
		self.isGroup(groupId)
	
	def removeFromGroup(self, userId, groupId):
		"""Removes the given user from the particular group
		
		userId: the unique id of the user
		groupId: the unique id of the group
		
		raises InvalidUserId if the user does not exist
		raises ReadOnlyViolation if the user model is read only
		raises InvalidGroupId if the group does not exist
		"""
		if self.readOnly:
			raise ReadOnlyViolation()
		
		#validate the userId
		self.isUser(userId)
		
		#validate the groupId
		self.isGroup(groupId)
		