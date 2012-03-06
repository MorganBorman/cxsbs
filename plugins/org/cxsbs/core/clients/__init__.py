class clients(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		self.client_manager = ClientManager()
		
		Interfaces = {}
		Resources = {'client_manager': self.client_manager, 'get_client': self.client_manager.get_client}
		
		org.cxsbs.core.events.manager.event_manager.register_handler('client_init', self.client_manager.on_client_init)
		org.cxsbs.core.events.manager.event_manager.register_handler('client_reinit', self.client_manager.on_client_init)
		org.cxsbs.core.events.manager.event_manager.register_handler('client_disc', self.client_manager.on_client_disc)
		org.cxsbs.core.events.manager.event_manager.register_handler('server_shutdown', self.client_manager.on_server_shutdown)
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
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
		
	def on_client_disc(self, event):
		cn = event.args[0]
		if cn in self._clients.keys():
			del self._clients[cn]
			
	def on_server_shutdown(self, event):
		self.disconnect_all("Server going down.")
		
	def disconnect_all(self, reason):
		for client in self._clients.values():
			client.message(reason)
			client.setDisconnect(0)

def log_client_action(client, action, level):
	log_function = pyTensible.plugin_loader.logger.__getattribute__(level)
	log_function("clients: %s@%u: %s" %(client.name, client.ip, action))

import copy

class Client:
	'''Represents a client on the server'''
	def __init__(self, manager, cn):
		self.__manager = manager
		self.__cn = cn
		self.__ip = sbserver.clientIpLong(self.cn)
		self.__sessionid = sbserver.clientSessionId(cn)
		
		self.__gamevars = copy.deepcopy(self.__manager.game_vars_template)
		self.__sessionvars = copy.deepcopy(self.__manager.session_vars_template)
		
		self.logAction("init", 'info')
	
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
	def gamevars(self):
		'''get the gamevars dictionary for this client'''
		return self.__gamevars
		
	@property
	def sessionvars(self):
		'''get the sessionvars dictionary for this client'''
		return self.__sessionvars
	
	@property
	def mapCrc(self):
		'''Map CRC of the client'''
		return sbserver.clientMapCrc(self.cn)

	@property
	def mapName(self):
		'''Map name of the client'''
		return sbserver.clientMapName(self.cn)
	
	@property
	def name(self):
		'''Name of client'''
		return sbserver.clientName(self.cn)
	
	@property
	def ipLong(self):
		'''Ip of client as long'''
		return self.ip
	
	@property
	def ipString(self):
		'''Ip of client as decimal octet string'''
		return Net.ipLongToString(self.ip)
	
	@property
	def frags(self):
		'''Frags by client in current game'''
		return sbserver.clientFrags(self.cn)
	
	@property
	def deaths(self):
		'''Deaths by client in current game'''
		return sbserver.clientDeaths(self.cn)
	
	@property
	def teamkills(self):
		'''Team kills by client in current game'''
		return sbserver.clientTeamkills(self.cn)
	
	@property
	def ping(self):
		'''Last reported ping of client'''
		return sbserver.clientPing(self.cn)
	
	@property
	def shots(self):
		'''Shots the client has fired'''
		return sbserver.clientShots(self.cn)
	
	@property
	def hits(self):
		'''Number of hits the client has dealt'''
		return sbserver.clientHits(self.cn)
	
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
	def score(self):
		'''Flags the client has scored'''
		return sbserver.clientScore(self.cn)
	
	@property
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
			
		if self.spectator:
			groups.append("__spectator__")
		elif self.invisible:
			groups.append("__invisible__")
		else:
			groups.append("__playing__")
			
		return groups
	
	#read write properties
	
	@property
	def team(self):
		'''Name of team client belongs to'''
		return sbserver.clientTeam(self.cn)
	
	@team.setter
	def __set_team(self, team):
		'''Set the team that this client is on'''
		sbserver.clientSetTeam(self.cn, team)
	
	@property
	def spectator(self):
		'''Is client a spectator'''
		return sbserver.clientState(self.cn) >= CS_SPECTATOR
	
	@spectator.setter
	def __set_spectator(self, value):
		if not type(value) == boolean:
			raise ValueError("Client spectator state must be boolean.")
		sbserver.clientSetSpectator(self.cn, value)
	
	@property
	def invisible(self):
		'''Is client invisible'''
		return sbserver.clientState(self.cn) == CS_INVISIBLE
	
	@invisible.setter
	def __set_invisible(self, value):
		if not type(value) == boolean:
			raise ValueError("Client invisible state must be boolean.")
		sbserver.clientSetSpectator(self.cn, value)
	
	#normal methods
	
	def newGame(self):
		'''Reset game variables'''
		self.__gamevars = copy.deepcopy(self.manager.game_vars_template)
	def logAction(self, action, level='info'):
		'''Log an action this client has taken'''
		log_client_action(self, action, level)
	def isPermitted(self, allowGroups, denyGroups):
		'''Check whether this client is permitted based on the given allowGroups and denyGroups'''
		permitted = False
		for group in self.groups():
			if group in denyGroups:
				return False
			if group in allowGroups:
				permitted = True
		return permitted
	def requestAuth(self, description):
		'''Request that a client send their auth key with the given description'''
		sbserver.clientRequestAuth(self.cn, description)
	def say(self, tcn, message):
		'''Send a message as this client to another client'''
		sbserver.clientMessageAll(self.cn, tcn, message)
	def sayteam(self, tcn, message):
		'''Send a team message as this client to another client'''
		sbserver.clientMessageTeam(self.cn, tcn, message)
	def message(self, msg):
		'''Send message to client'''
		sbserver.clientMessage(self.cn, msg)
	def disconnect(self, reason=0):
		'''Disconnect client from server'''
		sbserver.clientDisconnect(self.cn, reason)
	def setDisconnect(self, reason=0):
		'''Disconnect client from server'''
		sbserver.clientSetDisconnect(self.cn, reason)
	def suicide(self):
		'''Force client to commit suicide'''
		sbserver.suicide(self.cn)