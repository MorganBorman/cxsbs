class players(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
org = pyTensible.plugin_loader.get_resource("org")

@org.cxsbs.core.events.event_handler('client_connect_pre')
def client_connect_pre(cn):
	pass

class IClient:
	'''Represents a client on the server'''
	def __init__(self, cn):
		self._cn = cn
		self._ip = sbserver.playerIpLong(self.cn)
		self._sessionid = sbserver.playerSessionId(cn)
		self._gamevars = copy.deepcopy(game_vars_template)
		self._sessionvars = copy.deepcopy(session_vars_template)
	
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
		
	def logAction(self, action, level='info', **kwargs):
		'''Log an action this client has taken'''
		
	def newGame(self):
		'''Reset game variables'''
		self.gamevars = copy.deepcopy(game_vars_template)

	def mapCrc(self):
		'''Map CRC of the client'''
	def mapName(self):
		'''Map name of the client'''
	def requestAuth(self, description):
		'''Request that a player send their auth key with the given description'''
	def name(self):
		'''Name of client'''
	def ipLong(self):
		'''Ip of client as long'''
	def ipString(self):
		'''Ip of client as decimal octet string'''
	def groups(self):
		'''Returns the groups which are based on server state'''
	def isPermitted(self, allowGroups, denyGroups):
		'''Check whether this player is permitted based on the given allowGroups and denyGroups'''
	def requestPlayerAuth(self, desc):
		'''Request the players auth entry matching the given description'''
	def frags(self):
		'''Frags by client in current game'''
	def say(self, tcn, message):
		'''Send a message as this player to another player'''
	def sayteam(self, tcn, message):
		'''Send a team message as this player to another player'''
	def teamkills(self):
		'''Team kills by client in current game'''
	def deaths(self):
		'''Deaths by client in current game'''
	def ping(self):
		'''Last reported ping of client'''
	def team(self):
		'''Name of team client belongs to'''
	def isSpectator(self):
		'''Is client a spectator'''
	def isInvisible(self):
		'''Is client invisible'''
	def message(self, msg):
		'''Send message to client'''
	def disconnect(self, reason):
		'''Disconnect client from server'''
	def spectate(self):
		'''Make client spectator'''
	def unspectate(self):
		'''Make client not a spectator'''
	def setTeam(self, team):
		'''Set team client belongs to'''
	def suicide(self):
		'''Force client to commit suicide'''
	def shots(self):
		'''Shots the player has fired'''
	def hits(self):
		'''Number of hits the player has dealt'''
	def accuracy(self):
		'''Accuracy of player'''
	def kpd(self):
		'''Kills Per Death'''
	def score(self):
		'''Flags the player has scored'''

class Player(IClient):
	'''Represents a client on the server'''
	def __init__(self, cn):
		IClient.__init__(self, cn)
	def logAction(self, action, level='info', **kwargs):
		logPlayerAction(self.cn, action, level, **kwargs)

	def mapCrc(self):
		'''Map CRC of the client'''
		return ServerCore.playerMapCrc(self.cn)
	def mapName(self):
		'''Map name of the client'''
		return ServerCore.playerMapName(self.cn)
	def requestAuth(self, description):
		'''Request that a player send their auth key with the given description'''
		ServerCore.requestPlayerAuth(self.cn, description)
	def name(self):
		'''Name of client'''
		return ServerCore.playerName(self.cn)
	def ipLong(self):
		'''Ip of client as long'''
		return self.ip
	def ipString(self):
		'''Ip of client as decimal octet string'''
		return Net.ipLongToString(self.ip)
	def groups(self):
		'''Returns the groups which are based on server state'''
		playerPriv = ServerCore.playerPrivilege(self.cn)
		groups = []
		groups.append("__all__")
		
		if self.isInvisible():
			groups.append("__invisible__")
		
		if playerPriv == 1:
			groups.append("__master__")
		elif playerPriv == 2:
			groups.append("__admin__")
		else:
			groups.append("__norm__")
			
		if self.isSpectator():
			groups.append("__spectator__")
		else:
			groups.append("__player__")
			
		return groups
	
	def isPermitted(self, allowGroups, denyGroups):
		'''Check whether this player is permitted based on the given allowGroups and denyGroups'''
		permitted = False
		for group in self.groups():
			if group in denyGroups:
				return False
			if group in allowGroups:
				permitted = True
		return permitted
		
	def requestPlayerAuth(self, desc):
		'''Request the players auth entry matching the given description'''
		ServerCore.requestPlayerAuth(self.cn, desc)
	def frags(self):
		'''Frags by client in current game'''
		return ServerCore.playerFrags(self.cn)
	def say(self, tcn, message):
		'''Send a message as this player to another player'''
		ServerCore.playerMessageAll(self.cn, tcn, message)
	def sayteam(self, tcn, message):
		'''Send a team message as this player to another player'''
		ServerCore.playerMessageTeam(self.cn, tcn, message)
	def teamkills(self):
		'''Team kills by client in current game'''
		return ServerCore.playerTeamkills(self.cn)
	def deaths(self):
		'''Deaths by client in current game'''
		return ServerCore.playerDeaths(self.cn)
	def ping(self):
		'''Last reported ping of client'''
		return ServerCore.playerPing(self.cn)
	def team(self):
		'''Name of team client belongs to'''
		return ServerCore.playerTeam(self.cn)
	def isSpectator(self):
		'''Is client a spectator'''
		return ServerCore.playerIsSpectator(self.cn)
	def isInvisible(self):
		'''Is client invisible'''
		return ServerCore.playerIsInvisible(self.cn)
	def message(self, msg):
		'''Send message to client'''
		ServerCore.playerMessage(self.cn, msg)
	def disconnect(self, reason=PlayerDisconnect.DISC_NONE):
		'''Disconnect client from server'''
		Events.execLater(PlayerDisconnect.disconnect, (self.cn, reason))
	def spectate(self):
		'''Make client spectator'''
		ServerCore.spectate(self.cn)
	def unspectate(self):
		'''Make client not a spectator'''
		ServerCore.unspectate(self.cn)
	def setTeam(self, team):
		'''Set team client belongs to'''
		ServerCore.setTeam(self.cn, team)
	def suicide(self):
		'''Force client to commit suicide'''
		ServerCore.suicide(self.cn)
	def shots(self):
		'''Shots the player has fired'''
		return ServerCore.playerShots(self.cn)
	def hits(self):
		'''Number of hits the player has dealt'''
		return ServerCore.playerHits(self.cn)
	def accuracy(self):
		'''Accuracy of player'''
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
		'''Flags the player has scored'''
		return ServerCore.playerScore(self.cn)