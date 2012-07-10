import pyTensible, org, cube2server, copy, random
from groups.DynamicGroup import DynamicGroup
from groups.Group import Group

class clients(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		self.client_manager = ClientManager()
		
		AllClientsGroup = DynamicGroup(Client, self.client_manager._clients.values)
		EmptyClientsGroup = Group(Client, [])
		
		Interfaces = {}
		Resources = 	{
							'client_manager': self.client_manager, 
							'get_client': self.client_manager.get_client, 
							'Client': Client,
							'AllClientsGroup': AllClientsGroup,
							'EmptyClientsGroup': EmptyClientsGroup
						}
		
		event_manager = org.cxsbs.core.events.manager.event_manager
		
		event_manager.register_handler('client_init', self.client_manager.on_client_init)
		event_manager.register_handler('client_reinit', self.client_manager.on_client_init)
		event_manager.register_handler('client_disc', self.client_manager.on_client_disc)
		event_manager.register_handler('server_shutdown', self.client_manager.on_server_shutdown)
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.clients')
	
class enum(object):
	def __init__(self, items):
		i = 0
		for item in items:
			self.__setattr__(item, i)
			i += 1

class ClientConstants(object):
	disconnect_reasons = enum(['DISC_NONE', 'DISC_EOP', 'DISC_CN', 'DISC_KICK', 'DISC_TAGT', 'DISC_IPBAN', 'DISC_PRIVATE', 'DISC_MAXCLIENTS', 'DISC_TIMEOUT', 'DISC_OVERFLOW', 'DISC_NUM'])
	client_states = enum(['CS_ALIVE', 'CS_DEAD', 'CS_SPAWNING', 'CS_LAGGED', 'CS_EDITING', 'CS_SPECTATOR', 'CS_INVISIBLE'])

class ClientManager:
	_clients = {}
	_pseudoclients = {}
	_available_pcns = list(range(128, 256))
	_game_vars_template = {}
	_session_vars_template = {}
	
	def __init__(self):
		self._clients = {}
		self._game_vars_template = {}
		self._session_vars_template = {}
		
	@property
	def clients(self):
		#return a shallow copy of the clients dictionary
		return copy.copy(self._clients)
	
	@property
	def pseudoclients(self):
		return self._pseudoclients
		
	@property
	def session_vars_template(self):
		return self._session_vars_template
	
	@property
	def game_vars_template(self):
		return self._game_vars_template
	
	def connect_pseudoclient(self, client):
		"Connects a new pseudoclient and returns the client number"
		if len(self._available_pcns) <= 0:
			return None
		
		cn = random.choice(self._available_pcns)
		self._available_pcns.remove(cn)
		self._pseudoclients[cn] = client
		return cn
		
	def get_client(self, cn):
		if cn >= -128 and cn <= 127:
			return self._clients[cn]
		else:
			return self._pseudoclients[cn]
	
	def on_client_init(self, event):
		'''
		@thread policy_events
		'''
		cn = event.args[0]
		self._clients[cn] = Client(self, cn)
		org.cxsbs.core.logger.log.debug("Added client instance to client_manager.")
		
	def on_client_disc(self, event):
		cn = event.args[0]
		if cn in self._clients.keys():
			del self._clients[cn]
		elif cn in self._pseudoclients.keys():
			del self._pseudoclients[cn]
			self._available_pcns.append(cn)
			
	def on_server_shutdown(self, event):
		self.disconnect_all("Server going down.")
		
	def disconnect_all(self, reason):
		for client in self._clients.values():
			client.message(reason)
			client.setDisconnect(0)

def log_client_action(client, action, level):
	log_function = org.cxsbs.core.logger.log.__getattribute__(level)
	log_function("clients: %s@%u: %s" %(client.name, client.ip, action))

import copy

class Variables(object):
	def __init__(self, cn):
		self.cn = cn
	
	def __setitem__(self, key, value):
		if type(value) == int:
			valtype = 0
		elif type(value) == float:
			valtype = 1
		elif type(value) == str:
			valtype = 2
		else:
			raise ValueError("Must be set to a integer, float, or string") 
		
		print "Setting client variable %s to %s." %(key, str(value))
		
		cube2server.clientSetVariable(self.cn, self.cn, valtype, key, value)

class Client(object):
	'''Represents a client on the server'''
	def __init__(self, manager, cn):
		self.__manager = manager
		self.__cn = cn
		self.__ip = cube2server.clientIpLong(self.cn)
		self.__sessionid = cube2server.clientSessionId(cn)
		
		self.__gamevars = copy.deepcopy(self.__manager.game_vars_template)
		self.__sessionvars = copy.deepcopy(self.__manager.session_vars_template)
		
		self.logAction("init", 'info')
		
		self.uid = 1
	
	@property
	def cn(self):
		'''get the cn of the client'''
		return self.__cn
	
	@property
	def ip(self):
		'''get the ip of the client'''
		return self.__ip
	
	@property
	def sessionid(self):
		'''get the ip of the client'''
		return self.__sessionid
	
	@property
	def connect_password(self):
		'''Get the hash of the password this client used to connect.'''
		return cube2server.clientConnectPassword(self.cn)

	@property
	def gamevars(self):
		'''get the gamevars dictionary for this client'''
		return self.__gamevars
		
	@property
	def sessionvars(self):
		'''get the sessionvars dictionary for this client'''
		return self.__sessionvars
	
	@property
	def map_crc(self):
		'''Map CRC of the client'''
		return cube2server.clientMapCrc(self.cn)

	@property
	def map_name(self):
		'''Map name of the client'''
		return cube2server.clientMapName(self.cn)
	
	@property
	def name(self):
		'''Name of client'''
		return cube2server.clientName(self.cn)
	
	@property
	def variables(self):
		return Variables(self.cn)
	
	@property
	def ip_long(self):
		'''Ip of client as long'''
		return self.ip
	
	@property
	def ip_string(self):
		'''Ip of client as decimal octet string'''
		return org.cxsbs.core.net.ipLongToString(self.ip)
	
	@property
	def frags(self):
		'''Frags by client in current game'''
		return cube2server.clientFrags(self.cn)
	
	@property
	def deaths(self):
		'''Deaths by client in current game'''
		return cube2server.clientDeaths(self.cn)
	
	@property
	def teamkills(self):
		'''Team kills by client in current game'''
		return cube2server.clientTeamkills(self.cn)
	
	@property
	def suicides(self):
		'''Suicides by client in current game'''
		return cube2server.clientSuicides(self.cn)
	
	@property
	def damage_spent(self):
		'''Shots the client has fired'''
		return cube2server.clientDamageSpent(self.cn)
	
	@property
	def damage_dealt(self):
		'''Number of hits the client has dealt'''
		return cube2server.clientDamageDealt(self.cn)
	
	@property
	def damage_received(self):
		'''Amount of damage the client has received'''
		return cube2server.clientDamageReceived(self.cn)
	
	@property
	def ping(self):
		'''Last reported ping of client'''
		return cube2server.clientPing(self.cn)
	
	@property
	def accuracy(self):
		'''Accuracy of client'''
		shots = self.shots()
		accuracy = 0
		if shots != 0:
			accuracy = self.hits() / float(shots)
			accuracy = math.floor(accuracy * 100)
		return accuracy
	
	@property
	def kpd(self):
		'''Kills Per Death'''
		deaths = self.deaths()
		frags = self.frags()
		if deaths == 0:
			kpd = frags
		else:
			kpd = frags / float(deaths)
			kpd *= float(100)
			kpd = math.floor(kpd)
			kpd = kpd / 100
		return kpd
	
	@property
	def flags_scored(self):
		'''Flags the client has scored'''
		return cube2server.clientFlagsScored(self.cn)
	
	@property
	def groups(self):
		'''Returns the groups which are based on server state'''
		clientPriv = cube2server.clientPrivilege(self.cn)
		groups = []
		groups.append("__all__")
		
		if clientPriv == 1:
			groups.append("__master__")
		elif clientPriv == 2:
			groups.append("__admin__")
		else:
			groups.append("__norm__")
			
		try:
			for domain, credential in self.sessionvars['credentials'].items():
				for group in credential.groups:
					groups.append(group)
		except KeyError:
			pass
			
		if self.spectator:
			groups.append("__spectator__")
		elif self.invisible:
			groups.append("__invisible__")
		else:
			groups.append("__playing__")
			
		return groups
	
	#read write properties
	
	@property
	def uid(self):
		'''get the user id for this client'''
		return cube2server.clientUid(self.cn)
	
	@uid.setter
	def uid(self, uid):
		'''set the user id for this client'''
		cube2server.clientSetUid(self.cn, uid)
	
	@property
	def team(self):
		'''Name of team client belongs to'''
		return cube2server.clientTeam(self.cn)
	
	@team.setter
	def team(self, team):
		'''Set the team that this client is on'''
		cube2server.clientSetTeam(self.cn, team)
	
	@property
	def spectator(self):
		'''Is client a spectator'''
		return cube2server.clientState(self.cn) >= ClientConstants.client_states.CS_SPECTATOR
	
	@spectator.setter
	def spectator(self, value):
		if not type(value) == bool:
			raise ValueError("Client spectator state must be boolean.")
		cube2server.clientSetSpectator(self.cn, value)
	
	@property
	def invisible(self):
		'''Is client invisible'''
		return cube2server.clientState(self.cn) == ClientConstants.client_states.CS_INVISIBLE
	
	@invisible.setter
	def invisible(self, value):
		if not type(value) == bool:
			raise ValueError("Client invisible state must be boolean.")
		cube2server.clientSetInvisible(self.cn, value)
	
	#normal methods
	
	def newGame(self):
		'''Reset game variables'''
		self.__gamevars = copy.deepcopy(self.__manager.game_vars_template)
	def logAction(self, action, level='info'):
		'''Log an action this client has taken'''
		log_client_action(self, action, level)
	def isPermitted(self, allowGroups, denyGroups):
		'''Check whether this client is permitted based on the given allowGroups and denyGroups'''
		permitted = False
		for group in self.groups:
			if group in denyGroups:
				return False
			if group in allowGroups:
				permitted = True
		return permitted
	def isActionPermitted(self, action):
		'''Retreive a list of allowGroups and denyGroups for a particular action and check this client using isPermitted.'''
		allow_groups = settings[action + '_allowed']
		deny_groups = settings[action + '_denied']
		return self.isPermitted(allow_groups, deny_groups)
	def requestAuth(self, domain):
		'''Request that a client send their auth key with the given domain'''
		cube2server.clientRequestAuth(self.cn, domain)
	def challengeAuth(self, id, domain, challenge):
		'''Send an auth challenge to the client'''
		cube2server.clientChallengeAuth(self.cn, id, domain, challenge)
	def say(self, tcn, message):
		'''Send a message as this client to another client'''
		cube2server.clientMessageAll(self.cn, tcn, message)
	def sayteam(self, tcn, message):
		'''Send a team message as this client to another client'''
		cube2server.clientMessageTeam(self.cn, tcn, message)
	def message(self, msg):
		'''Send message to client'''
		cube2server.clientServerMessage(self.cn, msg)
	def disconnect(self, reason=0):
		'''Disconnect client from server'''
		cube2server.clientDisconnect(self.cn, reason)
	def setDisconnect(self, reason=0):
		'''Disconnect client from server'''
		cube2server.clientSetDisconnect(self.cn, reason)
	def suicide(self):
		'''Force client to commit suicide'''
		cube2server.suicide(self.cn)