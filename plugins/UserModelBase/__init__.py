import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import abc
	
class Model(object):
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def login(self, userId, serverId):
		"""to be called when user logs in to a server
		
		userId: the unique id of the user
		serverId: the unique id of the server that this is being called from
		
		raises InvalidUserId if the user does not exist
		does not verify serverId. This is the responsibility of the calling api
		
		returns (loginSuccessfulBoolean, loginMessage)
		"""
		pass
		
	@abc.abstractmethod
	def logout(self, userId, serverId):
		"""to be called when user logs out of a server
		
		userId: the unique id of the user
		serverId: the unique id of the server that this is being called from
		
		raises InvalidUserId if the user does not exist
		raises InvalidState if the user is not logged into the given server
		
		returns (logoutSuccessfulBoolean, loginMessage)
		"""
		pass
	
	@abc.abstractmethod
	def __isUser(self, userId):
		"""Check whether a userId is valid
		
		userId: the unique user identifier to check
		
		raises InvalidUserId if the user does not exist
		
		no return value
		"""
		pass
	
	def isUser(self, userId):
		"""Check whether a userId is valid
		
		userId: the unique user identifier to check
		
		returns a boolean
		"""
		try:
			self.__isUser(self, userId)
			return True
		except InvalidUserId:
			return False
		
	@abc.abstractmethod
	def __getUser(self, userId):
		"""Get a user orm object by userId
		
		userId: the unique user identifier to search by
		
		returns an object of class "Users"
		"""
		pass
		
	@abc.abstractmethod
	def getUserId(self, userEmail):
		"""Get a users id by their email
		
		userEmail: email to search by
		
		raises InvalidEmail if the email given does not relate to an account
		
		Returns the userId"""
		pass
	
	@abc.abstractmethod
	def getUserKey(self, userId):
		"""Get the users public key
		
		userId: the unique user identifier
		
		raises InvalidUserId if the user does not exist
		
		Returns the public key as a string
		"""
		pass
	
	@abc.abstractmethod
	def getUserEmail(self, userId):
		"""Get the users email
		
		userId: the unique user identifier
		
		raises InvalidUserId if the user does not exist
		
		Returns the email address as a string
		"""
		pass
	
	@abc.abstractmethod
	def verify(self, userEmail, verificationCode):
		"""called to finalize an action requiring email verification
		
		actions:
			verify a users account, generate authkeys, and email the private authkey + instructions to the user
			verify account deletion, and send successful deletion email
			verify password change, generate authkeys and email the private authkey + instructions to the user
		
		raises InvalidEmail if the email does not relate to a pending validation
		raises InvalidVerification if the verificationCode was incorrect
		
		no return value
		"""
		pass
		
	@abc.abstractmethod
	def createUser(self, userEmail, authenticationTokenSeed):
		"""Queues a createAccountVerification for the given Email
		
		userEmail: email to link to new account and to email verification to
		authenticationTokenSeed: desired authentication token
		
		raises InvalidEmail if the email is not canonical
		
		returns (verificationType, verificationDict)
		"""
		pass
	
	@abc.abstractmethod
	def deleteUser(self, userId):
		"""Queues a deleteAccountValidation the given user
		
		userId: the unique id of the user
		
		raises InvalidUserId if the user does not exist
		
		returns (verificationType, verificationDict)
		"""
		pass
	
	@abc.abstractmethod
	def changeUserKey(self, userId, seed):
		"""Queues an authenticationTokenChangeVerification for the given user
		
		userId: the unique id of the user
		
		raises InvalidUserId if the user does not exist
		
		returns (verificationType, verificationDict)
		"""
		pass
	
	@abc.abstractmethod
	def users(self, serverId=None, online=False, groupId=None):
		"""get the currently logged in users
		
		serverId: id of server to filter by (None = all servers)
		online: whether to only return online users
		groupId: id of group to filter by (None = all groups)
		
		raises InvalidGroupId if the group does not exist
		
		return the userIds as a list
		"""
		pass
		
	@abc.abstractmethod
	def __isGroup(self, groupId):
		"""Check whether a groupId is valid
		
		groupId: the unique group identifier to check
		
		raises InvalidGroupId if the group does not exist
		
		no return value
		"""
		pass
	
	def isGroup(self, groupId):
		"""Check whether a groupId is valid
		
		groupId: the unique group identifier to check
		
		raises InvalidGroupId if the group does not exist
		
		returns a boolean
		"""
		try:
			self.__isGroup(groupId)
			return True
		except InvalidGroupId:
			return False
	
	@abc.abstractmethod
	def __getGroup(self, groupId):
		"""Get the Group orm object
		
		raises InvalidGroupId if the group does not exist
		
		returns Group orm object
		"""
		pass
	
	@abc.abstractmethod
	def getGroupId(self, groupName):
		"""get the group of the given name
		
		groupName: the name of the group
		
		raises InvalidGroupName if the group does not exist
		
		returns the groupId
		"""
		pass
	
	@abc.abstractmethod
	def getGroupName(self, groupId):
		"""Get the group name
		
		groupId: the unique group identifier
		
		raises InvalidGroupId if the group does not exist
		
		Returns the group name corresponding to the given id
		"""
		pass
	
	@abc.abstractmethod
	def createGroup(self, groupName):
		"""Create a group of the given name and return the groupId
		
		raises InvalidGroupName if the name is not canonical
		
		returns the groupId
		"""
		pass
		
	@abc.abstractmethod
	def deleteGroup(self, groupId):
		"""Delete a group of the given name
		
		raises InvalidGroupId if the group does not exist
		
		no return value
		"""
		pass
	
	@abc.abstractmethod
	def groups(self, userId):
		"""Get a users groups
		
		userId: the unique id of the user to filter by (None = list of all groups)
		
		raises InvalidUserId if the user does not exist
		
		Returns the groupIds of a user as a list
		"""
		pass
		
	@abc.abstractmethod
	def addToGroup(self, userId, groupId):
		"""Adds the given user to a particular group
		
		userId: the unique id of the user
		groupId: the unique id of the group
		
		raises InvalidUserId if the user does not exist
		raises ReadOnlyViolation if the user model is read only
		"""
		pass
	
	@abc.abstractmethod
	def removeFromGroup(self, userId, groupId):
		"""Removes the given user from the particular group
		
		userId: the unique id of the user
		groupId: the unique id of the group
		
		raises InvalidUserId if the user does not exist
		raises ReadOnlyViolation if the user model is read only
		raises InvalidGroupId if the group does not exist
		"""
		pass
	
class InvalidState(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
	
class ReadOnlyViolation(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
	
class InvalidUserId(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidUserName(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidEmail(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidAuthenticationToken(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidVerification(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class NameConflict(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class NickLimitExceeded(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class SingleNickSystem(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidGroupId(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidGroupName(Exception):
	'''...'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
