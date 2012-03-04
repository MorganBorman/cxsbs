class clients(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		self.client_manager = ClientManager()
		
		Interfaces = {}
		Resources = {'client_manager': self.client_manager, 'get_client': self.client_manager.get_client}
		
		org.cxsbs.core.events.manager.event_manager.register_handler('client_init', self.client_manager.on_client_init)
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		self.client_manager.disconnect_all("")
	
import sbserver

class ClientManager:
	_clients = {}
	_game_vars_template = {}
	_session_vars_template = {}
	
	def __init__(self):
		self._clients = {}
		self._game_vars_template = {}
		self._session_vars_template = {}
		
	@property
	def session_vars_template(self):
		return self._session_vars_template
	
	@property
	def game_vars_template(self):
		return self._game_vars_template
		
	def get_client(self, cn):
		return self._clients[cn]
	
	def on_client_init(self, event):
		cn = event.args[0]
		self._clients[cn] = Client(self, cn)
		
	def disconnect_all(self, reason):
		for client in self._clients.values():
			client.disconnect(0)

def log_client_action(client, action, level):
	log_function = pyTensible.plugin_loader.logger.__getattribute__(level)
	log_function("clients: %s@%u: %s" %(client.name, client.ip, action))

import copy

class Client:
	'''Represents a client on the server'''
	def __init__(self, manager, cn):
		self._manager = manager
		self._cn = cn
		self._ip = sbserver.clientIpLong(self.cn)
		self._sessionid = sbserver.clientSessionId(cn)
		
		print self._sessionid
		
		self._gamevars = copy.deepcopy(manager.game_vars_template)
		self._sessionvars = copy.deepcopy(manager.session_vars_template)
		
		self.logAction("init", 'info')
	
	@property
	def cn(self):
		'''get the cn of the client'''
		return self._cn
	
	@property
	def ip(self):
		'''get the ip of the client'''
		return self._ip
	
	@property
	def sessionid(self):
		'''get the ip of the client'''
		return self._sessionid

	@property
	def gamevars(self):
		'''get the gamevars dictionary for this client'''
		return self._gamevars
		
	@property
	def sessionvars(self):
		'''get the sessionvars dictionary for this client'''
		return self._sessionvars
	
	def newGame(self):
		'''Reset game variables'''
		self.gamevars = copy.deepcopy(self.manager.game_vars_template)
	def logAction(self, action, level='info'):
		'''Log an action this client has taken'''
		log_client_action(self, action, level)
	def mapCrc(self):
		'''Map CRC of the client'''
		return sbserver.clientMapCrc(self.cn)
	def mapName(self):
		'''Map name of the client'''
		return sbserver.clientMapName(self.cn)
	def requestAuth(self, description):
		'''Request that a client send their auth key with the given description'''
		sbserver.clientRequestAuth(self.cn, description)
	def name(self):
		'''Name of client'''
		return sbserver.clientName(self.cn)
	def ipLong(self):
		'''Ip of client as long'''
		return self.ip
	def ipString(self):
		'''Ip of client as decimal octet string'''
		return Net.ipLongToString(self.ip)
	def groups(self):
		'''Returns the groups which are based on server state'''
		clientPriv = sbserver.clientPrivilege(self.cn)
		groups = []
		groups.append("__all__")
		
		if clientPriv == 1:
			groups.append("__master__")
		elif clientPriv == 2:
			groups.append("__admin__")
		else:
			groups.append("__norm__")
			
		if self.isSpectator():
			groups.append("__spectator__")
		elif self.isInvisible():
			groups.append("__invisible__")
		else:
			groups.append("__playing__")
			
		return groups
	
	def isPermitted(self, allowGroups, denyGroups):
		'''Check whether this client is permitted based on the given allowGroups and denyGroups'''
		permitted = False
		for group in self.groups():
			if group in denyGroups:
				return False
			if group in allowGroups:
				permitted = True
		return permitted
		
	def requestAuth(self, desc):
		'''Request the clients auth entry matching the given description'''
		sbserver.clientRequestAuth(self.cn, desc)
	def frags(self):
		'''Frags by client in current game'''
		return sbserver.clientFrags(self.cn)
	def say(self, tcn, message):
		'''Send a message as this client to another client'''
		sbserver.clientMessageAll(self.cn, tcn, message)
	def sayteam(self, tcn, message):
		'''Send a team message as this client to another client'''
		sbserver.clientMessageTeam(self.cn, tcn, message)
	def teamkills(self):
		'''Team kills by client in current game'''
		return sbserver.clientTeamkills(self.cn)
	def deaths(self):
		'''Deaths by client in current game'''
		return sbserver.clientDeaths(self.cn)
	def ping(self):
		'''Last reported ping of client'''
		return sbserver.clientPing(self.cn)
	def team(self):
		'''Name of team client belongs to'''
		return sbserver.clientTeam(self.cn)
	def isSpectator(self):
		'''Is client a spectator'''
		return sbserver.clientState(self.cn) >= CS_SPECTATOR
	def isInvisible(self):
		'''Is client invisible'''
		return sbserver.clientState(self.cn) == CS_INVISIBLE
	def message(self, msg):
		'''Send message to client'''
		sbserver.clientMessage(self.cn, msg)
	def disconnect(self, reason=0):
		'''Disconnect client from server'''
		sbserver.clientDisconnect(self.cn, reason)
	def spectate(self):
		'''Make client spectator'''
		sbserver.spectate(self.cn)
	def unspectate(self):
		'''Make client not a spectator'''
		sbserver.unspectate(self.cn)
	def setTeam(self, team):
		'''Set team client belongs to'''
		sbserver.setTeam(self.cn, team)
	def suicide(self):
		'''Force client to commit suicide'''
		sbserver.suicide(self.cn)
	def shots(self):
		'''Shots the client has fired'''
		return sbserver.clientShots(self.cn)
	def hits(self):
		'''Number of hits the client has dealt'''
		return sbserver.clientHits(self.cn)
	def accuracy(self):
		'''Accuracy of client'''
		shots = self.shots()
		accuracy = 0
		if shots != 0:
			accuracy = self.hits() / float(shots)
			accuracy = math.floor(accuracy * 100)
		return accuracy
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
	def score(self):
		'''Flags the client has scored'''
		return sbserver.clientScore(self.cn)