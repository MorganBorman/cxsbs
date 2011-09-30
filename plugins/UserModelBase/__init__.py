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
	
	def __init__(self, readOnly, usernameValidator, authenticationTokenValidator, groupValidator, maxNicks):
		#whether or not this model is read only
		self.readOnly = readOnly
		#boolean function to validate username naming rules
		self.usernameValidator = usernameValidator
		#boolean function to validate authentication token strength rules
		self.authenticationTokenValidator = authenticationTokenValidator
		#boolean function to validate group naming rules
		self.groupValidator = groupValidator
		#max number of nicks including primary nick
		self.maxNicks = maxNicks
		
	@abc.abstractmethod
	def isNickAllowed(self, userName, userId=None):
		"""Check if a name may be used by an individual
		
		userName: username to check
		userId: the unique id of the user (None if not logged in)
		
		Returns whether or not a name is reserved
		"""
		pass
	
	@abc.abstractmethod
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
		pass
	
	@abc.abstractmethod
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
		pass
	
	@abc.abstractmethod
	def login(self, userId, serverId):
		"""to be called when user logs in to a server
		
		userId: the unique id of the user
		serverId: the unique id of the server that this is being called from
		
		raises InvalidUserId if the user does not exist
		does not validate serverId. This is the responsibility of the calling api
		
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
	def isUser(self, userId):
		"""Check whether a userId is valid
		
		userId: the unique user identifier to check
		
		raises InvalidUserId if the user does not exist
		
		no return value
		"""
		pass
		
	@abc.abstractmethod
	def getUser(self, userName):
		"""Get the user id of a user
		
		userName: username to check
		
		raises InvalidUserName if the name does not relate to an account
		
		Returns the userId"""
		pass
	
	@abc.abstractmethod
	def getUserPublicKey(self, userId):
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
	def getUserNames(self, userId):
		"""Get the users names
		
		userId: the unique user identifier
		
		raises InvalidUserId if the user does not exist
		
		Returns a list with all the users names in it
		"""
		pass
		
	@abc.abstractmethod
	def createUser(self, userName, email, authenticationTokenSeed):
		"""Queues a createAccountVerification for the given userName
		
		userName: desired user name
		authenticationTokenSeed: desired authentication token
		
		raises NameConflict when logical
		raises InvalidUserName if the name is not canonical
		raises InvalidEmail if the email is not canonical
		raises InvalidAuthenticationToken if the authentication token seed is not canonical
		raises ReadOnlyViolation if user model is read only
		
		returns (verificationType, verificationDict)
		"""
		pass
	
	@abc.abstractmethod
	def deleteUser(self, userId):
		"""Queues a deleteAccountValidation the given user
		
		userId: the unique id of the user
		
		raises InvalidUserId if the user does not exist
		raises ReadOnlyViolation if the user model is read only
		
		returns (verificationType, verificationDict)
		"""
		pass
	
	@abc.abstractmethod
	def changeUserAuthenticationToken(self, userId, authenticationTokenSeed):
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
	def isGroup(self, groupId):
		"""Check whether a groupId is valid
		
		groupId: the unique group identifier to check
		
		raises InvalidGroupId if the user does not exist
		
		no return value
		"""
		pass
	
	@abc.abstractmethod
	def getGroup(self, groupName):
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
