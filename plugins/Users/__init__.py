import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global nextRequestId
		nextRequestId = int(time.time())
		
		global requestIdTable
		requestIdTable = {}
		
	def unload(self):
		pass
		
import time
		
import cxsbs
UserModel = cxsbs.getResource("UserModel")
Players = cxsbs.getResource("Players")
UserModelBase = cxsbs.getResource("UserModelBase")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Messages = cxsbs.getResource("Messages")
Commands = cxsbs.getResource("Commands")
Events = cxsbs.getResource("Events")
Timers = cxsbs.getResource("Timers")
Auth = cxsbs.getResource("Auth")
ServerCore = cxsbs.getResource("ServerCore")
Email = cxsbs.getResource("Email")
CommandInformation = cxsbs.getResource("CommandInformation")

pluginCategory = 'Users'
pluginSubcategory = 'General'

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="protect_system_groups", 
												displayName="Protect system groups", 
												default=True,
												doc="Prevent users who have not claimed admin using the admin password from adding users to the built in system groups."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="allow_self_propagating_groups", 
												displayName="Allow self propagating groups", 
												default=False,
												doc="Prevent users who have not claimed admin from adding users to groups which in turn have permissions to add users to groups."
											))

settings = SettingsManager.getAccessor(pluginCategory, pluginSubcategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="logged_in", 
						displayName="Logged in", 
						default="${info}${green}${name}${white} is verified.",
						doc="Message to print when a player has successfully logged in."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="authlogin_unsuccessful", 
						displayName="Authlogin unsuccessful", 
						default="${denied}Invalid credentials.",
						doc="Message to print when a player fails logging in."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="already_logged_in", 
						displayName="Already logged in", 
						default="${denied}Already logged in.",
						doc="Message to print when a player fails logging in due to already being logged in."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='registration_successful', 
						displayName='Registration successful', 
						default="${info}Successfully initiated ${blue}registration${white} check your email for verification details.",
						doc="Message to print when a player initiates registration."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='keychange_successful', 
						displayName='Key change successful', 
						default="${info}Successfully initiated ${blue}key change${white} check your email for verification details.",
						doc="Message to print when a player initiates a key change."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='unregistration_successful', 
						displayName='unregistration successful', 
						default="${info}Successfully initiated ${blue}unregistration${white} check your email for verification details.",
						doc="Message to print when a player initiates unregistration."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='verification_successful', 
						displayName='Verification successful', 
						default="${info}${blue}verification${white} success! Check your email for more information.",
						doc="Message to print when a player's verification succeeds."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='verification_unsuccessful', 
						displayName='Verification unsuccessful', 
						default="${error}${blue}verification${white} failed check that your email and verification code are correct.",
						doc="Message to print when a player's verification fails."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='group_add_success', 
						displayName='Group add success', 
						default="${info}${green}${name}${white} has been added to the group ${blue}${groupName}${white}.'",
						doc="Message to print player is added to a group."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='group_removed_success', 
						displayName='Group removed success', 
						default="${info}${green}${name}${white} has been removed from the group ${blue}${groupName}${white}.",
						doc="Message to print player is removed from a group."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

class User(Players.Player):
	def __init__(self, cn, userId):
		Players.Player.__init__(self, cn)
		self.gamevars = Players.player(cn).gamevars
		self.userId = userId
		Players.updatePlayerObject(self)
		
	def groups(self):
		return UserModel.model.groups(self.userId) + Players.Player.groups(self) + ['__user__']
		
	def __del__(self):
		Players.revertPlayerObject(self)
		
def isLoggedIn(cn):
	try:
		return isinstance(Players.player(cn), User)
	except:
		return False 
		
@Commands.commandHandler('register')
def onRegisterCommand(cn, args):
	'''
	@description Register account with server
	@usage <email> <token seed>
	@allowGroups __all__
	@denyGroups __user__
	@doc
	'''
	args = args.split()
	if len(args) != 2:
		raise Commands.UsageError()
	
	email = args[0]
	if not Email.isValidEmail(email):
		raise Commands.ArgumentValueError('The email you provided is not valid.')
	
	authenticationTokenSeed = args[1]
	
	if len(authenticationTokenSeed) < 5:
		raise Commands.ArgumentValueError("Please provide a tokenSeed with a length greater than 5.")
	
	try:
		verificationDict = UserModel.model.createUser(email, authenticationTokenSeed)
		
		cxsbs.AsyncronousExecutor.dispatch(Email.send_templated_email, (verificationDict['verificationType'], verificationDict['userEmail']), verificationDict)
		
		p = Players.player(cn)
		messager.sendPlayerMessage('registration_successful', p)
		
	except UserModelBase.InvalidEmail:
		raise Commands.ArgumentValueError('The email you provided is not valid.')
	
@Commands.commandHandler('unregister')
def onUnregisterCommand(cn, args):
	'''
	@description Unregister this account with server
	@usage
	@allowGroups __user__
	@denyGroups
	@doc 
	'''
	user = Players.player(cn)
	try:
		verificationDict = UserModel.model.deleteUser(user.userId)
		
		cxsbs.AsyncronousExecutor.dispatch(Email.send_templated_email, (verificationDict['verificationType'], verificationDict['userEmail']), verificationDict)
		
		p = Players.player(cn)
		messager.sendPlayerMessage('unregistration_successful', p)
		
	except UserModelBase.InvalidUserId:
		raise Commands.StateError('You must be logged in to link a name to your account.')
	
@Commands.commandHandler('verify')
def onVerifyCommand(cn, args):
	'''
	@description Supply verification for a pending action
	@usage <username> <code>
	@allowGroups __all__
	@denyGroups
	@doc 
	'''
	args = args.split()
	if len(args) != 2:
		raise Commands.UsageError()
	
	p = Players.player(cn)
	
	try:
		verificationDict = UserModel.model.verify(args[0], args[1])

		cxsbs.AsyncronousExecutor.dispatch(Email.send_templated_email, (verificationDict['verificationType'], verificationDict['userEmail']), verificationDict)
		
		messager.sendPlayerMessage('verification_successful', p)

	except (UserModelBase.InvalidUserName, UserModelBase.InvalidVerification):
		messager.sendPlayerMessage('verification_unsuccessful', p)

@Commands.commandHandler('changekey')
def onChangeKeyCommand(cn, args):
	'''
	@description change account password
	@usage <token seed>
	@allowGroups __user__
	@denyGroups
	@doc 
	'''
	if len(args) < 5:
		raise Commands.ArgumentValueError("Please provide a tokenSeed with a length greater than 5.")
	if not isLoggedIn(cn):
		raise Commands.StateError('You must be logged in to change your authentication key.')
	user = Players.player(cn)
	try:
		verificationDict = UserModel.model.changeUserKey(user.userId, args)
		
		cxsbs.AsyncronousExecutor.dispatch(Email.send_templated_email, (verificationDict['verificationType'], verificationDict['userEmail']), verificationDict)
		
		p = Players.player(cn)
		messager.sendPlayerMessage('keychange_successful', p)
		
	except UserModelBase.InvalidUserId:
		raise Commands.StateError('You must be logged in to change your authentication key.')
	
@Events.eventHandler('player_auth_request')
def authRequest(cn, name, desc):
	p = Players.player(cn)
	if desc == Auth.settings["automatic_request_description"]:
		if isLoggedIn(cn):
			messager.sendPlayerMessage('already_logged_in', p)
			return
		
		try:
			if p.pendingAuthLogin:
				return
		except AttributeError:
			pass
		
		try:
			userId = UserModel.model.getUserId(name)
			publicKey = UserModel.model.getUserKey(userId)
			
			p.pendingAuthLogin = True
			p.userId = userId
			
			global nextRequestId
			requestId = nextRequestId
			
			nextRequestId -= 1
			
			requestIdTable[cn] = requestId
			
			#use the memory location of the Player object as the request id
			p.challengeAnswer = ServerCore.sendAuthChallenge(cn, Auth.settings["automatic_request_description"], requestId, publicKey)
			
		except UserModelBase.InvalidEmail:
			messager.sendPlayerMessage('authlogin_unsuccessful', p)
			
@Events.eventHandler('player_auth_challenge_response')
def authChallengeResponse(cn, reqid, response):
	p = Players.player(cn)
	try:
		requestId = requestIdTable[cn]
	except KeyError:
		#Challenge must not have been issued by the auth login functionality
		#otherwise there would be a requestId in the table.
		return
	
	if not reqid == requestId:
		print "returned because request id did not match that in table."
		messager.sendPlayerMessage('authlogin_unsuccessful', p)
		return
	else:
		del requestIdTable[cn]
	
	serverId = 0
	
	if response == p.challengeAnswer:
		login = UserModel.model.login(p.userId, serverId)
		if login[0]:
			p.message(login[1])
			User(cn, p.userId)
			messager.sendMessage('logged_in', dictionary={'name':p.name()})
		else:
			print "login from integrated user model returned false"
			messager.sendPlayerMessage('authlogin_unsuccessful', p)
	else:
		p.challengeAnswer = None
		print "Auth challenge failed"
		messager.sendPlayerMessage('authlogin_unsuccessful', p)
	
@Commands.commandHandler('addtogroup')
def addToGroupCommand(cn, args):
	'''
	@description Add a user to a group
	@usage <email or tcn> <group name>
	@allowGroups __admin__
	@denyGroups
	@doc Adds a user to a specified group, creating said group if necessary.
	'''
	args = args.split()
	if len(args) != 2:
		raise Commands.UsageError()
	
	if Email.isValidEmail(args[0]):
		email = args[0]
		
		try:
			userId = UserModel.model.getUserId(email)
		except UserModelBase.InvalidEmail:
			raise Commands.StateError("That email does not correspond to an account.")
	else:
		tcn = int(args[0])
		
		if isLoggedIn(tcn):
			user = Players.player(tcn)
			userId = user.userId
		else:
			raise Commands.StateError("That player does not seem to be logged in.")
	
	groupName = args[1]
	
	if groupName in UserModelBase.protectedGroups and ServerCore.playerPrivilege(cn) != 2 and settings['protect_system_groups']:
		raise Commands.StateError("That is a protected group, only admins may add users to this group.")
	
	if groupName in CommandInformation.getCommandInfo('addtogroup').getAllowedGroups() and ServerCore.playerPrivilege(cn) != 2 and not settings['allow_self_propagating_groups']:
		raise Commands.StateError("That group is protected because it can add users to groups, only admins may add users to this group.")
		
	try:
		groupId = UserModel.model.getGroupId(groupName)
	except UserModelBase.InvalidGroupName:
		groupId = UserModel.model.createGroup(groupName)
		
	try:
		UserModel.model.addToGroup(userId, groupId)
	except UserModelBase.DuplicateAssociation:
		raise Commands.StateError("That player already is in that group.")
	
	messager.sendPlayerMessage('group_add_success', Players.player(cn), dictionary={'name': UserModel.model.getUserEmail(userId), 'groupName': groupName})
	
@Commands.commandHandler('removefromgroup')
def removeFromGroupCommand(cn, args):
	'''
	@description Remove a user from a group
	@usage <email> <group name>
	@allowGroups __admin__
	@denyGroups
	@doc Removes a user from a specified group.
	'''
	args = args.split()
	if len(args) != 2:
		raise Commands.UsageError()

	try:
		tcn = int(args[0])
	except ValueError:
		tcn = None
		
	if tcn != None:
		if isLoggedIn(tcn):
			user = Players.player(tcn)
			userId = user.userId
		else:
			raise Commands.StateError("That player does not seem to be logged in.")
	else:
		email = args[0]
		
		try:
			userId = UserModel.model.getUserId(email)
		except UserModelBase.InvalidEmail:
			raise Commands.StateError("That email does not correspond to an account.")
	
	try:
		groupName = args[1]
		groupId = UserModel.model.getGroupId(groupName)
		UserModel.model.removeFromGroup(userId, groupId)
		messager.sendPlayerMessage('group_removed_success', Players.player(cn), dictionary={'name': UserModel.model.getUserEmail(userId), 'groupName': groupName})
	except UserModelBase.InvalidGroupId:
		raise Commands.StateError("That user is not a member of the specified group.")
	except UserModelBase.InvalidAssociation:
		raise Commands.StateError("That user is not a member of the specified group.")