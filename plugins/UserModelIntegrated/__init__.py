import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
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
												symbolicName="verification_table", 
												displayName="Verification table", 
												default="usermanager_verifications",
												doc="Table name for storing the pending user verifications."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="group_table", 
												displayName="Group table", 
												default="usermanager_groups",
												doc="Table name for storing the user groups."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="group_membership_table", 
												displayName="Group membership table", 
												default="usermanager_group_membership",
												doc="Table name for storing the user-group associations."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

class User(Base):
	__tablename__ = tableSettings["user_table"]
	id = Column(Integer, primary_key=True)
	email = Column(String(64), nullable=False)
	publicKey = Column(String(49), index=True)
	serverId = Column(Integer, nullable=True)
	def __init__(self, email, publicKey):
		self.email = email
		self.publicKey = publicKey
		
class Verification(Base):
	__tablename__ = tableSettings["verification_table"]
	id = Column(Integer, primary_key=True)
	type = Column(String(32), nullable=False)
	email = Column(String(64), index=True)
	verificationCode = Column(String(32), index=True)
	time = Column(Integer, nullable=False)
	userId = Column(Integer, nullable=True)
	tokenSeed = Column(String(32), nullable=True)
	def __init__(self, email, verificationCode, type, time, userId, tokenSeed):
		self.type = type
		self.email = email
		self.verificationCode = verificationCode
		self.time = time
		self.userId = userId
		self.tokenSeed = tokenSeed
		
class Group(Base):
	__tablename__ = tableSettings["group_table"]
	id = Column(Integer, primary_key=True)
	name = Column(String(16), index=True)
	def __init__(self, name):
		self.name = name
		
class GroupMembership(Base):
	__tablename__ = tableSettings["group_membership_table"]
	userId = Column(Integer, ForeignKey(tableSettings["user_table"] + '.id'))
	groupId = Column(Integer, ForeignKey(tableSettings["group_table"] + '.id'))
	user = relation(User, primaryjoin=userId==User.id)
	group = relation(Group, primaryjoin=groupId==Group.id)
	UniqueConstraint('ip', 'name', name='uq_user_ip_ip_name')
	__mapper_args__ = {'primary_key':[userId, groupId]}
	def __init__(self, userId, groupId):
		self.userId = userId
		self.groupId = groupId
		
Base.metadata.create_all(DatabaseManager.dbmanager.engine)

class Model(UserModelBase.Model):
	def __init__(self):
		UserModelBase.Model.__init__(self)
	
	def login(self, userId, serverId):
		"""to be called when user logs in to a server
		
		userId: the unique id of the user
		serverId: the unique id of the server that this is being called from
		
		raises InvalidUserId if the user does not exist
		does not verify serverId. This is the responsibility of the calling api
		
		returns (loginSuccessfulBoolean, loginMessage)
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			user = self.__getUser(userId)
			user.serverId = serverId
			session.add(user)
			session.commit()
		finally:
			session.close()
		
		return (True, "Welcome.")
	
	def logout(self, userId, serverId):
		"""to be called when user logs out of a server
		
		userId: the unique id of the user
		serverId: the unique id of the server that this is being called from
		
		raises InvalidUserId if the user does not exist
		raises InvalidState if the user is not logged into the given server
		
		returns (logoutSuccessfulBoolean, loginMessage)
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			user = self.__getUser(userId)
			user.serverId = None
			session.add(user)
			session.commit()
		finally:
			session.close()
			
		return (True, "Goodbye.")
	
	def __isUser(self, userId):
		"""Check whether a userId is valid
		
		userId: the unique user identifier to check
		
		raises InvalidUserId if the user does not exist
		
		no return value
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			session.query(User).filter(User.id==userId).one()
		except:
			raise UserModelBase.InvalidUserId(userId)
		finally:
			session.close()
	
	def isUser(self, userId):
		"""Check whether a userId is valid
		
		userId: the unique user identifier to check
		
		returns a boolean
		"""
		try:
			self.__isUser(userId)
			return True
		except UserModelBase.InvalidUserId:
			return False
	
	def __getUser(self, userId):
		"""Get a user orm object by userId
		
		userId: the unique user identifier to search by
		
		returns an object of class "Users"
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			return session.query(User).filter(User.id==userId).one()
		except:
			raise UserModelBase.InvalidUserId(userId)
		finally:
			session.close()
	
	def getUserId(self, userEmail):
		"""Get a users id by their email
		
		userEmail: email to search by
		
		raises InvalidEmail if the email given does not relate to an account
		
		Returns the userId
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			user = session.query(User).filter(User.email==userEmail).one()
			return user.id
		except:
			raise UserModelBase.InvalidEmail(userEmail)
		finally:
			session.close()
	
	def getUserKey(self, userId):
		"""Get the users public key
		
		userId: the unique user identifier
		
		raises InvalidUserId if the user does not exist
		
		Returns the public key as a string
		"""
		user = self.__getUser(userId)
		return user.publicKey
	
	def getUserEmail(self, userId):
		"""Get the users email
		
		userId: the unique user identifier
		
		raises InvalidUserId if the user does not exist
		
		Returns the email address as a string
		"""
		user = self.__getUser(userId)
		return user.email
	
	def verify(self, userEmail, verificationCode):
		"""called to finalize an action requiring email verification
		
		actions:
			verify a users account, generate authkeys, and email the private authkey + instructions to the user
			verify account deletion, and send successful deletion email
			verify password change, generate authkeys and email the private authkey + instructions to the user
		
		raises InvalidEmail if the email does not relate to a pending validation
		raises InvalidVerification if the verificationCode was incorrect
		
		returns verificationFeedbackDict
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			verification = session.query(Verification).filter(Verification.email==userEmail).filter(Verification.verificationCode==verificationCode).one()
		except NoResultFound:
			raise UserModelBase.InvalidVerification()
		except MultipleResultsFound:
			raise UserModelBase.InvalidState("duplicate verification entries for userEmail:" + userEmail)
		finally:
			session.close()
			
		verificationFeedbackDict = {
										'verificationType': verification.type + "_feedback",
										'userId': verification.userId,
										'userEmail': verification.email,
										'verificatioTime': verification.time,
										'domain': Auth.settings["automatic_request_description"],
									}
			
		if verification.type == "createAccount":
			ammendDict = self.__createFinalize(verification)
			
		elif verification.type == "deleteAccount":
			ammendDict = self.__deleteFinalize(verification)
			
		elif verification.type == "changeAccountKey":
			ammendDict = self.__changeFinalize(verification)
		else:
			raise UserModelBase.InvalidState("unkown verification type: " + verification.type)
		
		verificationFeedbackDict.update(ammendDict)
		
		return verificationFeedbackDict
	
	def __createFinalize(self, verification):
		session = DatabaseManager.dbmanager.session()
		try:
			keypair = Auth.genKeyPair(verification.tokenSeed)
			user = User(verification.email, keypair[1])
			session.delete(verification)
			session.add(user)
			session.commit()
			
			return {'privateKey': keypair[0],'publicKey': keypair[1]}
			
		finally:
			session.close()
	
	def __deleteFinalize(self, verification):
		session = DatabaseManager.dbmanager.session()
		try:
			user = self.__getUser(verification.userId)
			session.delete(user)
			session.commit()
			
			return {}
			
		finally:
			session.close()
		
	def __changeFinalize(self, verification):
		session = DatabaseManager.dbmanager.session()
		try:
			keypair = Auth.genKeyPair(verification.tokenSeed)
			user = self.__getUser(verification.userId)
			user.publicKey = keypair[1]
			session.add(user)
			session.commit()
			
			return {'privateKey': keypair[0],'publicKey': keypair[1]}
			
		finally:
			session.close()
		
	def createUser(self, userEmail, seed):
		"""Queues a createAccountVerification for the given Email
		
		userEmail: email to link to new account and to email verification to
		authenticationTokenSeed: desired authentication token
		
		raises InvalidEmail if the email is not canonical
		
		returns verificationDict
		"""
		
		verificationType = "createAccount"
		verificationCode = ppwgen.generatePassword()
		verificationTime = time.time()
		userId = None
		
		session = DatabaseManager.dbmanager.session()
		try:
			verification = Verification(userEmail, verificationCode, verificationType, verificationTime, userId, seed)
			session.add(verification)
			session.commit()
		finally:
			session.close()
			
		verificationDict = {
								'verificationType':verificationType, 
								'userEmail':userEmail, 
								'verificationCode':verificationCode, 
								'verificationTime':verificationTime
							}
			
		return verificationDict
	
	def deleteUser(self, userId):
		"""Queues a deleteAccountValidation the given user
		
		userId: the unique id of the user
		
		raises InvalidUserId if the user does not exist
		
		returns verificationDict
		"""
		verificationType = "deleteAccount"
		verificationCode = ppwgen.generatePassword()
		verificationTime = time.time()
		userId = userId
		userEmail = self.getUserEmail(userId)
		
		session = DatabaseManager.dbmanager.session()
		try:
			verification = Verification(userEmail, verificationCode, verificationType, verificationTime, userId, None)
			session.add(verification)
			session.commit()
		finally:
			session.close()
			
		verificationDict = {
								'verificationType':verificationType, 
								'userEmail':userEmail, 
								'verificationCode':verificationCode, 
								'verificationTime':verificationTime
							}
			
		return verificationDict
	
	def changeUserKey(self, userId, seed):
		"""Queues an authenticationTokenChangeVerification for the given user
		
		userId: the unique id of the user
		
		raises InvalidUserId if the user does not exist
		
		returns verificationDict
		"""
		verificationType = "changeAccountKey"
		verificationCode = ppwgen.generatePassword()
		verificationTime = time.time()
		userId = userId
		userEmail = self.getUserEmail(userId)
		
		session = DatabaseManager.dbmanager.session()
		try:
			verification = Verification(userEmail, verificationCode, verificationType, verificationTime, userId, seed)
			session.add(verification)
			session.commit()
		finally:
			session.close()
			
		verificationDict = {
								'verificationType':verificationType, 
								'userEmail':userEmail, 
								'verificationCode':verificationCode, 
								'verificationTime':verificationTime
							}
			
		return verificationDict
	
	
	def users(self, serverId=None, online=False, groupId=None):
		"""get the currently logged in users
		
		serverId: id of server to filter by (None = all servers)
		online: whether to only return online users
		groupId: id of group to filter by (None = all groups)
		
		raises InvalidGroupId if the group does not exist
		
		return the userIds as a list
		"""
		pass
	
	def __isGroup(self, groupId):
		"""Check whether a groupId is valid
		
		groupId: the unique group identifier to check
		
		raises InvalidGroupId if the group does not exist
		
		no return value
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			session.query(Group).filter(Group.id==groupId).one()
		except:
			raise UserModelBase.InvalidGroupId(groupId)
		finally:
			session.close()
	
	def isGroup(self, groupId):
		"""Check whether a groupId is valid
		
		groupId: the unique group identifier to check
		
		raises InvalidGroupId if the group does not exist
		
		returns a boolean
		"""
		try:
			self.__isGroup(groupId)
			return True
		except UserModelBase.InvalidGroupId:
			return False
	
	
	def __getGroup(self, groupId):
		"""Get the Group orm object
		
		raises InvalidGroupId if the group does not exist
		
		returns Group orm object
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			return session.query(Group).filter(Group.id==groupId).one()
		except:
			raise UserModelBase.InvalidGroupId(groupId)
		finally:
			session.close()
	
	def getGroupId(self, groupName):
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
			raise UserModelBase.InvalidGroupName(groupName)
		finally:
			session.close()
	
	def getGroupName(self, groupId):
		"""Get the group name
		
		groupId: the unique group identifier
		
		raises InvalidGroupId if the group does not exist
		
		Returns the group name corresponding to the given id
		"""
		group = self.__getGroup(groupId)
		return group.name
	
	def createGroup(self, groupName):
		"""Create a group of the given name and return the groupId
		
		raises InvalidGroupName if the name is not canonical
		
		returns the groupId
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			group = Group(groupName)
			session.add(group)
			session.commit()
			return self.getGroupId(groupName)
		except:
			raise UserModelBase.InvalidGroupName(groupName)
		finally:
			session.close()
	
	def deleteGroup(self, groupId):
		"""Delete a group of the given name
		
		raises InvalidGroupId if the group does not exist
		
		no return value
		"""
		session = DatabaseManager.dbmanager.session()
		try:
			group = self.__getGroup(groupId)
			session.delete(group)
			session.commit()
		finally:
			session.close()
	
	def groups(self, userId):
		"""Get a users groups
		
		userId: the unique id of the user to filter by (None = list of all groups)
		
		raises InvalidUserId if the user does not exist
		
		Returns the groupNames of a user as a list
		"""
		groupNames = []
		session = DatabaseManager.dbmanager.session()
		try:
			if userId == None:
				groups = session.query(Group).all()
				for group in groups:
					groupNames.append(group.name)
			else:
				groupMemberships = session.query(GroupMembership).filter(GroupMembership.userId==userId).all()
				for groupMembership in groupMemberships:
					groupNames.append(str(groupMembership.group.name))
					
			return groupNames
		finally:
			session.close()
	
	def addToGroup(self, userId, groupId):
		"""Adds the given user to a particular group
		
		userId: the unique id of the user
		groupId: the unique id of the group
		
		raises InvalidUserId if the user does not exist
		raises InvalidGroupId if the group does not exist
		raises DuplicateAssociation if the association already exists
		"""
		#validate the userId
		self.isUser(userId)
		
		#validate the groupId
		self.isGroup(groupId)
		
		#check whether the association already exists
		session = DatabaseManager.dbmanager.session()
		try:
			groupMembership = session.query(GroupMembership).filter(GroupMembership.userId==userId).one()
			raise UserModelBase.DuplicateAssociation()
		except NoResultFound:
			pass
		except MultipleResultsFound:
			pass
		finally:
			session.close()
		
		#actually add the association
		session = DatabaseManager.dbmanager.session()
		try:
			groupMembership = GroupMembership(userId, groupId)
			session.add(groupMembership)
			session.commit()
		finally:
			session.close()
	
	def removeFromGroup(self, userId, groupId):
		"""Removes the given user from the particular group
		
		userId: the unique id of the user
		groupId: the unique id of the group
		
		raises InvalidUserId if the user does not exist
		raises InvalidGroupId if the group does not exist
		raise InvalidAssociation if the association does not exist
		"""
		#validate the userId
		self.isUser(userId)
		
		#validate the groupId
		self.isGroup(groupId)
		
		#check whether the association already exists
		session = DatabaseManager.dbmanager.session()
		try:
			groupMembership = session.query(GroupMembership).filter(GroupMembership.userId==userId).one()
			pass
		except NoResultFound:
			raise UserModelBase.InvalidAssociation
		except MultipleResultsFound:
			pass
		finally:
			session.close()
		
		#actually remove the associations
		session = DatabaseManager.dbmanager.session()
		try:
			groupMemberships = session.query(GroupMembership).filter(GroupMembership.userId==userId).filter(GroupMembership.groupId==groupId).all()
			for groupMembership in groupMemberships:
				session.delete(groupMembership)
			session.commit()
		except NoResultFound:
			raise UserModelBase.InvalidGroupId
		finally:
			session.close()