import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		if not UserModel.model.readOnly:
			Commands.registerCommandHandler('register', onRegisterCommand)
			Commands.registerCommandHandler('linkname', onLinkNameCommand)
			Commands.registerCommandHandler('changeKey', onChangeKeyCommand)
		
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
		
def onRegisterCommand(cn, args):
	'''
	@description Register account with server
	@usage <username> <email> <token seed>
	@allowGroups __all__
	@denyGroups 
	@doc
	'''
	args = args.split(' ')
	if len(args) != 3:
		raise Commands.UsageError()
	
	userName = args[0]
	email = args[1]
	authenticationTokenSeed = args[2]
	
	try:
		UserModel.model.createUser(userName, email, authenticationTokenSeed)
	except UserModelBase.NameConflict:
		raise Commands.StateError('That name is not available.')
	except UserModelBase.InvalidUserName:
		raise Commands.StateError('The name you provided is not valid.')
	except UserModelBase.InvalidEmail:
		raise Commands.StateError('The email you provided is not valid.')
	except UserModelBase.InvalidAuthenticationToken:
		raise Commands.StateError('The token seed you provided is not valid.')
	except UserModelBase.ReadOnlyViolation:
		raise Commands.StateError('Registration is not permitted.')
	
def onUnregisterCommand(cn, args):
	'''
	@description Unregister this account with server
	@usage
	@allowGroups __user__
	@denyGroups
	@doc 
	'''
	user = Players.player(cn)
	name = ClanTags.stripTags(user.name())
	try:
		UserModel.model.deleteUser(user.userId)
	except UserModelBase.InvalidUserId:
		raise Commands.StateError('You must be logged in to link a name to your account.')
	except UserModelBase.ReadOnlyViolation:
		raise Commands.StateError('Unregistering is not permitted.')
	
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
		UserModel.model.validate(args[0], args[1])
		p = Players.player(cn)
		p.message("Verification successful.")
	except (UserModelBase.InvalidUserName, UserModelBase.InvalidVerification):
		raise Commands.StateError('Verification unsuccessful.')
		
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
		UserModel.model.changeUserAuthenticationToken(user.userId, args)
	except UserModelBase.InvalidUserId:
		raise Commands.StateError('You must be logged in to change your authentication key.')
		
	
@Events.eventHandler('player_name_changed')	
@Events.eventHandler('player_connect_delayed')
def onPlayerActive(*args):
	"""Trigger checks on both names and tags to see whether the player must validate to use them."""
	if len(args) < 1:
		return
	cn = args[0]
	Timers.addTimer(2*1000, warnNickReserved, (cn, 0))
	Timers.addTimer(2*1000, ClanTags.warnTagsReserved, (cn, 0))
	
@Events.eventHandler('player_auth_request')
def authRequest(cn, name, desc):
	p = Players.player(cn)
	if Auth.settings["automatic_request_description"]:
		try:
			userId = UserModel.model.getUser(name)
			publicKey = UserModel.model.getUserPublicKey(userId)
			
		except UserModelBase.InvalidUserName:
			p.message("Unknown username")
			
		p.pendingAuthLogin = True
		p.userId = userId
		
		#use the memory location of the Player object as the request id
		p.challengeAnswer = ServerCore.sendAuthChallenge(cn, Auth.settings["automatic_request_description"], id(p), publicKey)
			
@Events.eventHandler('player_auth_challenge_response')
def authChallengeResponse(cn, reqid, response):
	p = Players.player(cn)
	if not id(p) == reqid:
		print "returned because id(p) != reqid"
		return
	try:
		if not p.pendingAuthLogin:
			print "returned because p is not pending auth login"
			return
	except:
		print "some other exception"
		return
	
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
		print "Auth challenge failed"
	
		