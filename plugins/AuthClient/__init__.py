from cxsbs.Plugin import Plugin

class AuthClient(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		deinit()
		
import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
Players = cxsbs.getResource("Players")
Config = cxsbs.getResource("Config")
Events = cxsbs.getResource("Events")
Logging = cxsbs.getResource("Logging")
MessageFramework = cxsbs.getResource("MessageFramework")
SetMaster = cxsbs.getResource("SetMaster")

from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor, protocol
from twisted.internet.task import LoopingCall

import time, signal 

class AuthRequest(object):
	def __init__(self, id, cn, name):
		self.id = id
		self.cn = cn
		self.name = name

class AuthIdNotFoundError(Exception):
	pass

class ResponseHandler(object):
	def __init__(self, factory):
		self.key_handlers = {
			'succreg':		self.registrationSuccess,
			'failreg':		self.registrationFailure,
			'succauth':		self.AuthenticationSuccess,
			'failauth':		self.AuthenticationFailure,
			'chalauth':		self.AuthenticationChallenge,
			'cleargbans':	self.clearGlobalBans,
			'addgban':		self.addGlobalBan
			}
		self.auth_id_map = {}
		self.factory = factory
		self.last_auth_id = -1
		self.responses_needed = 0
		
	def getAuthRequest(self, auth_id):
		try:
			return self.auth_id_map[auth_id]
		except KeyError:
			raise AuthIdNotFoundError()
		
	def popAuthRequest(self, auth_id):
		try:
			auth = self.auth_id_map[auth_id]
			del self.auth_id_map[auth_id]
			return auth
		except KeyError:
			raise AuthIdNotFoundError()
		
	def handle(self, response):
		key = response.split(' ')[0]
		try:
			self.key_handlers[key](response[len(key)+1:])
		except KeyError:
			Logging.error('Invalid response key: %s' % key)
		except AuthIdNotFoundError:
			Logging.error('Could not find matching auth request for given auth request id')
		if self.responses_needed <= 0:
			#We are going to keep connections open
			#self.factory.client.transport.loseConnection()
			self.responses_needed = 0
			
	def registrationSuccess(self, args):
		self.responses_needed -= 1
		Logging.debug('Master server registration successful')
		Events.triggerServerEvent('master_registration_succeeded', ())
		
	def registrationFailure(self, args):
		self.responses_needed -= 1
		Logging.error('Master server registration failed: %s' % args)
		Events.triggerServerEvent('master_registration_failed', ())
		
	def clearGlobalBans(self, args):
		Events.triggerServerEvent('master_cleargbans', ())
		
	def addGlobalBan(self, args):
		Events.triggerServerEvent('master_addgban', (args,))
		
	def AuthenticationSuccess(self, args):
		self.responses_needed -= 1
		auth_id = int(args.split()[0])
		auth = self.popAuthRequest(auth_id)
		Events.triggerServerEvent('player_auth_succeed', (auth.cn, auth.name))
		
	def AuthenticationFailure(self, args):
		self.responses_needed -= 1
		auth_id = int(args.split()[0])
		auth = self.popAuthRequest(auth_id)
		Events.triggerServerEvent('player_auth_fail', (auth.cn, auth.name))
		
	def AuthenticationChallenge(self, args):
		args = args.split()
		auth_id = int(args[0])
		auth_challenge = args[1]
		auth = self.getAuthRequest(auth_id)
		ServerCore.authChallenge(auth.cn, auth.id, auth_challenge)
		
	def nextAuthId(self):
		self.last_auth_id += 1
		return self.last_auth_id
	
	
class MasterClient(LineReceiver):
	delimiter = '\n'
	def connectionMade(self):
		Logging.debug('Connected to master server')
		self.factory.clientConnected(self)
	def connectionLost(self, reason):
		self.factory.clientDisconnected(self)
	def lineReceived(self, line):
		self.factory.response_handler.handle(line)

class MasterClientFactory(protocol.ClientFactory):
	protocol = MasterClient
	def __init__(self, master_host, master_port):
		
		self.master_host = master_host 
		self.master_port = master_port
		self.response_handler = ResponseHandler(self)
		self.client = None
		self.send_buffer = []
		
	def clientConnected(self, client):
		if self.client != None:
			del self.client
		self.client = client
		for data in self.send_buffer:
			self.client.sendLine(data)
		del self.send_buffer[:]
	def clientDisconnected(self, client):
		self.client = None
		self.response_handler.auth_id_map.clear()
	def send(self, data):
		if self.client == None:
			ip = ServerCore.ip()
			if ip != None:
				reactor.connectTCP(self.master_host, int(self.master_port), self, 30, (ServerCore.ip(), ServerCore.port())) #@UndefinedVariable
			else:
				reactor.connectTCP(self.master_host, int(self.master_port), self) #@UndefinedVariable
			self.send_buffer.append(data)
		else:
			self.client.sendLine(data)

def registerServer():
	factory.response_handler.responses_needed += 1
	factory.send('regserv %i' % ServerCore.port())
		
def init():
	global allow_auth
	
	config = Config.PluginConfig('masterclient')
	master_host = config.getOption('Config', 'master_host', 'sauerbraten.org')
	master_port = config.getOption('Config', 'master_port', '28787')
	allow_auth = config.getBoolOption('Config', 'allow_auth', True)
	register_interval = config.getIntOption('Config', 'register_interval', '3600')
	del config
	
	global messageModule
	messageModule = MessageFramework.MessagingModule()
	messageModule.addMessage('auth_success', '${green}${name}${white} has authenticated as ${magenta}${authname}${white}.', 'AuthClient')
	messageModule.addMessage('admin_present', 'You cannot claim ${magenta}auth${white} here, there is already an ${red}admin${white} present.', 'AuthClient')
	messageModule.finalize()
	
	global factory, registerRepeater
	factory = MasterClientFactory(master_host, master_port)
	registerRepeater = LoopingCall(registerServer)
	registerRepeater.start(register_interval)
	
	@Events.eventHandler('player_auth_succeed')
	def onAuthSuccess(cn, name):
		p = Players.player(cn)
		p.logAction('successful auth', authname=name)
		if Players.currentAdmin() != None:
			messageModule.sendPlayerMessage('admin_present', p)
			return
		messageModule.sendMessage('auth_success', dictionary={'authname': name, 'name':p.name()})
		SetMaster.setSimpleMaster(cn, auth=True)
		
	@Events.eventHandler('player_auth_request')
	def authRequest(cn, name, desc):
		p = Players.player(cn)
		p.logAction('issued auth request', authname=name, keydesc=desc)
		if desc == "" and allow_auth:
			factory.response_handler.responses_needed += 1
			req = AuthRequest(factory.response_handler.nextAuthId(), cn, name)
			factory.response_handler.auth_id_map[req.id] = req
			factory.send('reqauth %i %s' % (req.id, req.name))
	
	@Events.eventHandler('player_auth_challenge_response')
	def authChallengeResponse(cn, id, response):
		factory.send('confauth %i %s' % (id, response))
		
def deinit():
		registerRepeater.stop()
		registerRepeater._reschedule()
		reactor.stop()