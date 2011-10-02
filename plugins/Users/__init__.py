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
ClanTags = cxsbs.getResource("ClanTags")
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

pluginCategory = 'Users'
pluginSubcategory = 'Reserved Name'

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="max_warnings", 
												displayName="Maximum warnings", 
												default=5,
												doc="Number of warnings to give before kicking a player using a reserved nickname."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="warning_interval", 
												displayName="Warning interval", 
												default=5,
												doc="Amount of time between warnings about using a reserved nickname."
											))

settings = SettingsManager.getAccessor(pluginCategory, pluginSubcategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="name_reserved", 
						displayName="Name reserved", 
						default="${warning}You're are using a reserved name; ${blue}${name}${white}. You have ${red}${remaining}${white} seconds to login or be kicked.", 
						doc="Message to print when a player has violated the sanctity of another's name without proper credentials."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="logged_in", 
						displayName="Logged in", 
						default="${info}${green}${name}${white} is verified.",
						doc="Message to print when a player has successfully logged in."
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

"""
def warnNickReserved(cn, count, startTime=None):
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
	
	if UserModel.model.isNickAllowed(playerNick, userId):
		return
	
	if count > settings["max_warnings"]:
		BanCore.addBan(cn, 0, 'Use of reserved name', -1)
		return
	
	remaining = (settings["max_warnings"]*settings["warning_interval"]) - (count*settings["warning_interval"])
	messager.sendMessage('name_reserved', dictionary={'name':playerNick, 'remaining':remaining})
	Timers.addTimer(settings["warning_interval"]*1000, warnNickReserved, (cn, count+1, startTime))
"""
		
@Commands.commandHandler('register')
def onRegisterCommand(cn, args):
	'''
	@description Register account with server
	@usage <email> <token seed>
	@allowGroups __all__
	@denyGroups __user__
	@doc
	'''
	args = args.split(' ')
	if len(args) != 2:
		raise Commands.UsageError()
	
	email = args[0]
	authenticationTokenSeed = args[1]
	
	if len(authenticationTokenSeed) < 5:
		raise Commands.UsageError("Please provide a tokenSeed with a length greater than 5")
	
	try:
		verificationDict = UserModel.model.createUser(email, authenticationTokenSeed)
		
		Email.send_templated_email(verificationDict['verificationType'], verificationDict['userEmail'], **verificationDict)
		
		p = Players.player(cn)
		#messager.sendPlayerMessage('registration_successfull', p)
		p.message("registration successful")
		
	except UserModelBase.InvalidEmail:
		raise Commands.StateError('The email you provided is not valid.')
	
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
		
		Email.send_templated_email(verificationDict['verificationType'], verificationDict['userEmail'], **verificationDict)
		
		p = Players.player(cn)
		#messager.sendPlayerMessage('unregistration_successfull', p)
		p.message("unregistration successful")
		
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
	args = args.split(' ')
	if len(args) != 2:
		raise Commands.UsageError()
	try:
		verificationDict = UserModel.model.verify(args[0], args[1])

		Email.send_templated_email(verificationDict['verificationType'], verificationDict['userEmail'], **verificationDict)
		
		p = Players.player(cn)
		#messager.sendPlayerMessage('verification_successfull', p)
		p.message("verification successful")

	except (UserModelBase.InvalidUserName, UserModelBase.InvalidVerification):
		raise Commands.StateError('Verification unsuccessful.')
		
"""
def onLinkNameCommand(cn, args):
	'''
	@description Link name to server account, and reserve name.
	@usage
	@allowGroups __user__
	@denyGroups
	@doc 
	'''
	if args != '':
		raise Commands.UsageError()
	if not isLoggedIn(cn):
		raise Commands.StateError('You must be logged in to link a name to your account')
	user = Players.player(cn)
	name = ClanTags.stripTags(user.name())
	try:
		UserModel.model.associateNick(name, user.userId)
	except UserModelBase.InvalidUserId:
		raise Commands.StateError('You must be logged in to link a name to your account.')
	except UserModelBase.NameConflict:
		raise Commands.StateError('That name is not available.')
	except UserModelBase.SingleNickSystem:
		raise Commands.StateError('This system does not permit multiple names.')
	except UserModelBase.NickLimitExceeded:
		raise Commands.StateError('You have exceeded the permissible number of linked names.')
	except UserModelBase.InvalidUserName:
		raise Commands.StateError('That name is not permitted.')
	except UserModelBase.ReadOnlyViolation:
		raise Commands.StateError('Linking of names is not permitted.')
	#except UserModelBase.:
"""

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
		raise Commands.UsageError("Please provide a tokenSeed with a length greater than 5")
	if not isLoggedIn(cn):
		raise Commands.StateError('You must be logged in to change your authentication key.')
	user = Players.player(cn)
	try:
		verificationDict = UserModel.model.changeUserKey(user.userId, args)
		
		Email.send_templated_email(verificationDict['verificationType'], verificationDict['userEmail'], **verificationDict)
		
		p = Players.player(cn)
		#messager.sendPlayerMessage('keychange_successfull', p)
		p.message("keychange successful")
		
	except UserModelBase.InvalidUserId:
		raise Commands.StateError('You must be logged in to change your authentication key.')
	
@Events.eventHandler('player_auth_request')
def authRequest(cn, name, desc):
	p = Players.player(cn)
	if Auth.settings["automatic_request_description"]:
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
	#print "Request id from table:", type(requestIdTable[cn]), requestIdTable[cn]
	#print "Request id from event:", type(reqid), reqid
	p = Players.player(cn)
	if not reqid == requestIdTable[cn]:
		print "returned because request id did not match that in table."
		return
	else:
		del requestIdTable[cn]
	
	serverId = "wooooh"
	
	if response == p.challengeAnswer:
		login = UserModel.model.login(p.userId, serverId)
		if login[0]:
			p.message(login[1])
			User(cn, p.userId)
			messager.sendMessage('logged_in', dictionary={'name':p.name()})
		else:
			print "login from integrated user model returned false"
	else:
		p.challengeAnswer = None
		print "Auth challenge failed"
	
@Commands.commandHandler('addtogroup')
def addToGroupCommand(cn, args):
	'''
	@description Add a user to a group
	@usage <email> <group name>
	@allowGroups __admin__
	@denyGroups
	@doc Adds a user to a specified group, creating said group if necessary.
	'''
	args = args.split()
	if len(args) != 2:
		raise Commands.UsageError()
	email = args[0]
	groupName = args[1]
	
	userId = UserModel.model.getUserId(email)
	try:
		groupId = UserModel.model.getGroupId(groupName)
	except UserModelBase.InvalidGroupName:
		groupId = UserModel.model.createGroup(groupName)
		
	#try:
	UserModel.model.addToGroup(userId, groupId)
	#except:
	#	pass
	
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
	email = args[0]
	groupName = args[1]
	
	userId = UserModel.model.getUserId(email)
	groupId = UserModel.model.getGroupId(groupName)
	
	UserModel.model.removeFromGroup(userId, groupId)