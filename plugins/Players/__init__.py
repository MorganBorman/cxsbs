import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		#create the circular reference so that Players can be referenced later
		#from inside Events
		Events.bootStrapPlayersModule(cxsbs.getResource("Players"))
		
		global players
		players = {}
		for cn in ServerCore.clients():
			addPlayerForCn(cn)
		
	def unload(self):
		pass
		
import cxsbs
Events = cxsbs.getResource("Events")
UI = cxsbs.getResource("UI")
Timers = cxsbs.getResource("Timers")
ServerCore = cxsbs.getResource("ServerCore")
Logging = cxsbs.getResource("Logging")
Net = cxsbs.getResource("Net")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")

permissionsCategory = 'Permissions'
pluginSubcategory = 'Invisibility'

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="allow_groups_see_invisible",
													displayName="Allow groups see invisible", 
													default=['__admin__', '__invisible__'],
													doc="Groups which are permitted to see messages regarding invisible players.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginSubcategory, 
													symbolicName="deny_groups_see_invisible",
													displayName="Deny groups see invisible", 
													default=[],
													doc="Groups which are not permitted to see messages regarding invisible players.",
												))

settings = SettingsManager.getAccessor(category=permissionsCategory, subcategory=pluginSubcategory)

import math

from groups.DynamicGroup import DynamicGroup
from groups.Group import Group

def logPlayerAction(cn, action, level='info', **kwargs):
	p = player(cn)
	msg = p.name() + "@" + p.ipString() + " " + str(action)
	if kwargs != {}:
		msg += " with args:"
		first = True
		for key, value in kwargs.items():
			if not first:
				msg += ','
			else:
				first = False
			msg += " " + key + ":" + value
	Logging.log(Logging.LEVELS[level], msg)

class Player:
	'''Represents a client on the server'''
	def __init__(self, cn):
		self.cn = cn
		self.gamevars = {}
	def logAction(self, action, level='info', **kwargs):
		logPlayerAction(self.cn, action, level, **kwargs)
	def newGame(self):
		'''Reset game variables'''
		self.gamevars.clear()
	def sessionId(self):
		'''Session ID of client'''
		return ServerCore.playerSessionId(self.cn)
	def requestAuth(self, description):
		'''Request that a player send their auth key with the given description'''
		ServerCore.requestPlayerAuth(self.cn, description)
	def name(self):
		'''Name of client'''
		return ServerCore.playerName(self.cn)
	def ipLong(self):
		'''Ip of client as long'''
		return ServerCore.playerIpLong(self.cn)
	def ipString(self):
		'''Ip of client as decimal octet string'''
		return Net.ipLongToString(self.ipLong())
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
		
	def requestPlayerAuth(self, desc):
		'''Request the players auth entry matching the given description'''
		ServerCore.requestPlayerAuth(self.cn, desc)
	def frags(self):
		'''Frags by client in current game'''
		return ServerCore.playerFrags(self.cn)
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
	def kick(self):
		'''Disconnect client from server'''
		Events.execLater(ServerCore.playerKick, (self.cn,))
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

@Events.eventHandler('map_changed')
def onMapChanged(mapname, mapmode):
	for player in players.values():
		player.newGame();

def all():
	'''Get list of all clients'''
	return players.values()

def seeInvisible():
	'''Get a list of those players who are permitted to see messages concerning invisible players'''
	listing = []
	for p in all():
		denied = False
		allowed = False
		for g in p.groups():
			if g in settings["allow_groups_see_invisible"]:
				allowed = True
			if g in settings["deny_groups_see_invisible"]:
				denied = True
		if allowed and not denied:
			listing.append(p)
	return listing
		
SeeInvisibleGroup = DynamicGroup(Player, seeInvisible)
AllPlayersGroup = DynamicGroup(Player, all)
EmptyPlayersGroup = Group(Player, [])

def cnsToPlayers(cns):
	'''Turn list of cn's into list of Player's'''
	ps = []
	for cn in cns:
		ps.append(players[cn])
	return ps

def clientCount():
	'''Number of clients connected to server'''
	return len(ServerCore.clients())

def spectatorCount():
	'''Number of spectators in server'''
	return len(ServerCore.spectators())

def playerCount():
	'''Number of players in game'''
	return len(ServerCore.players())

def spectators():
	'''Get list of spectators as Player instances'''
	return cnsToPlayers(ServerCore.spectators())

def activePlayers():
	'''Get list of players as Player instances'''
	return cnsToPlayers(ServerCore.players())

def player(cn):
	'''Return player instance of cn'''
	try:
		return players[cn]
	except KeyError:
		raise ValueError('Player does not exist')

def playerByName(name):
	'''Return player instance of player with name'''
	for p in all():
		if p.name() == name:
			return p
	raise ValueError('No player by specified name')

def playerByIpLong(ip):
	'''Return Player instance with matching long (int) ip'''
	for p in all():
		if ip == p.ipLong():
			return p
	raise ValueError('No player found matching ip')

def playerByIpString(ip):
	'''Return Player instance with matching string ip'''
	return playerByIpLong(Net.ipStringToLong(ip))

def triggerConnectDelayed(cn):
	try:
		player(cn)
	except ValueError:
		return
	else:
		Events.triggerServerEvent('player_connect_delayed', (cn,))
		
def triggerBotConnectDelayed(cn):
	try:
		player(cn)
	except ValueError:
		return
	else:
		Events.triggerServerEvent('bot_connect_delayed', (cn,))

def currentMaster():
	for cn in ServerCore.clients():
		if ServerCore.playerPrivilege(cn) == 1:
			return cn
	return None

def currentAdmin():
	for cn in ServerCore.clients():
		if ServerCore.playerPrivilege(cn) == 2:
			return cn
	return None

def addPlayerForCn(cn):
	try:
		del players[cn]
	except KeyError:
		pass
	players[cn] = Player(cn)
	
def updatePlayerObject(pObject):
	'''Update a player's class. Facility primarily used to changing a Player to a User.'''
	if not isinstance(pObject, Player):
		raise Exception("Cannot update player object with an object of a class not derived from Player.")
	cn = pObject.cn
	try:
		p = players[cn]
		players[cn] = pObject
	except IndexError:
		raise Exception("Attempt to update player class for a player who does not exist.")
	
def revertPlayerObject(pObject):
	'''Revert a player's class. Facility primarily used to revert a player back to a regular Player after logging out'''
	if not isinstance(pObject, Player):
		raise Exception("Cannot revert player object from a object of a class not derived from Player.")
	try:
		cn = pObject.cn
		try:
			gamevars = pObject.gamevars
		except:
			gamevars = {}
		players[cn] = Player(players[cn])
		players[cn].gamevars = gamevars
	except (IndexError, KeyError):
		pass
		#raise Exception("Attempt to revert player class for a player who does not exist.")
	
@Events.eventHandler('player_connect')
def onPlayerConnect(cn):
	logPlayerAction(cn, 'connect')
	
@Events.eventHandler('player_disconnect')
def onPlayerDisconnect(cn):
	logPlayerAction(cn, 'disconnect')
	
@Events.eventHandler('player_connect_pre')
def onPlayerConnectPre(cn):
	addPlayerForCn(cn)
	Timers.addTimer(1000, triggerConnectDelayed, (cn,))

@Events.eventHandler('game_bot_added')
def onBotConnect(cn):
	addPlayerForCn(cn)
	Timers.addTimer(1000, triggerConnectDelayed, (cn,))
	
@Events.eventHandler('player_disconnect_post')
@Events.eventHandler('game_bot_removed')
def playerDisconnect(cn):
	try:
		del players[cn]
	except KeyError:
		Logging.error('Player disconnected but does not have player class instance!')
		