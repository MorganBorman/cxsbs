from cxsbs.Plugin import Plugin

class Users(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass
		
import cxsbs
UserModel = cxsbs.getResource("UserModel")
Players = cxsbs.getResource("Players")

class User(Players.Player):
	def __init__(self, cn, userId):
		Players.Player.__init__(self, cn)
		self.userId = userId
		

def warnNickReserved(cn, count, sessid):
	pass

def init():
	def onRegisterCommand(cn, args):
		'''@description Register account with server
		   @usage email password
		   @public'''
		args = args.split(' ')
		if len(args) != 2:
			raise UsageError()
		session = dbmanager.session()
		try:
			session.query(User).filter(User.email==args[0]).one()
		except NoResultFound:
			if not isValidEmail(args[0]):
				raise ArgumentValueError('Invalid email address')
			user = User(args[0], args[1])
			session.add(user)
			session.commit()
			sbserver.playerMessage(cn, info('Account created'))
			return
		except MultipleResultsFound:
			raise StateError('An account with that email already exists')
		finally:
			session.close()
			
	def onRegisterCommand(cn, args):
		'''@description Register account with server
		   @usage username email password
		   @public'''
		args = args.split(' ')
		if len(args) != 3:
			raise UsageError()
		
	@Commands.commandHandler('verify')
	def onVerifyCommand(cn, args):
		'''@description Supply verification for a pending action
		   @usage username code
		   @public'''
		args = args.split(' ')
		if len(args) != 2:
			raise UsageError()
			
	def onLinkNameCommand(cn, args):
		'''@description Link name to server account, and reserve name.
		   @usage
		   @public'''
		if args != '':
			raise Commands.UsageError()
		if not isLoggedIn(cn):
			raise StateError('You must be logged in to link a name to your account')
	
	def onChangeKeyCommand(cn, args):
		'''@description change account password
		   @usage <current password> <new password>
		   @public'''
		args = args.split(' ')
		if len(args) != 2:
			raise Commands.UsageError()
		if not isLoggedIn(cn):
			raise Commands.StateError('You must be logged in to change your authentication key.')
		
	@Events.eventHandler('player_name_changed')	
	@Events.eventHandler('player_connect')
	def onPlayerActive(*args):
		cn = args[0]
		p = player(cn)
		nick = player.cn
		if isLoggedIn(cn):
			
		else:
			
		warnNickReserved(cn, 0, sbserver.playerSessionId(cn))
			

	if not UserModel.model.readOnly:
		Commands.registerCommandHandler('register', onRegisterCommand)
		Commands.registerCommandHandler('linkname', onLinkNameCommand)
		Commands.registerCommandHandler('changeKey', onChangeKeyCommand)