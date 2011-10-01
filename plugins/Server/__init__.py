import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global server_frozen
		server_frozen = False
		
	def unload(self):
		pass
		
import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Commands = cxsbs.getResource("Commands")
Messages = cxsbs.getResource("Messages")
Logging = cxsbs.getResource("Logging")
	
Messages.addMessage	(
						subcategory="Pause", 
						symbolicName="set_paused", 
						displayName="Set paused", 
						default="The game has been ${blue}${action}${white} by ${green}${name}${white}.", 
						doc="Message to print on pause and unpause."
					)

messager = Messages.getAccessor(subcategory="Pause")

import string

def isPaused():
	'''Is the game currently paused'''
	return ServerCore.isPaused()

def setPaused(val, cn=-1):
	'''Pause or unpause the game'''
	if isFrozen():
		raise Commands.StateError('Server is currently frozen')
	if val == ServerCore.isPaused():
		return
	if val:
		action = 'paused'
	else:
		action = 'unpaused'

	try:
		p = Players.player(cn)
		name = p.name()
		p.logAction(action)
	except ValueError:
		name = 'the server'
		Logging.info('The server has ' + action + ' itself.')

	messager.sendMessage('set_paused', dictionary={'action':action, 'name':name})
	Events.triggerServerEvent(action, (cn, ))
	ServerCore.setPaused(val)

def adminPassword():
	'''Administrator password of server.'''
	return ServerCore.adminPassword()

def ip():
	'''Ip address server is bound to.'''
	return ServerCore.ip()

def port():
	'''Port server is bound to.'''
	return ServerCore.port()

def reload():
	'''Reload python system.'''
	return ServerCore.reload()

def setBotLimit(limit):
	'''Set maximum number of bots.'''
	return ServerCore.setBotLimit(limit)

def uptime():
	'''Server uptime in miliseconds.'''
	return ServerCore.uptime()

def message(string):
	'''Send message to server.'''
	ServerCore.message(string)

def setMasterMode(mm_number):
	'''Set server master mode.
	   0 - open
	   1 - veto
	   2 - locked
	   3 - private'''
	ServerCore.setMasterMode(mm_number)

def clientCount():
	'''Number of clients currently on the server.'''
	return len(ServerCore.clients())

def playerCount():
	'''Number of players currently on the server.'''
	return len(ServerCore.players())

def spectatorCount():
	'''Number of spectators currently on the server.'''
	return len(ServerCore.spectators())

def maxClients():
	'''Maximum clients allowed in server.'''
	return ServerCore.maxClients()

def setMaxClients(num_clients):
	'''Set the maximum clients allowed in server.'''
	return ServerCore.setMaxClients(num_clients)

def setFrozen(val):
	'''Sets whether the server state is frozen.
	   This value is recognized by many of the server
	   commands (such as pause/unpause) and setting this
	   to true will keep them from functioning.'''
	global server_frozen
	server_frozen = val

def isFrozen():
	'''Is the currently frozen. See setFrozen(val).'''
	return server_frozen
	
@Events.eventHandler('player_pause')
def onPlayerPause(cn, val):
	'''
	@commandType
	@allowGroups __admin__ __master__
	@doc This command type event occurs when a player issues "/pausegame <value>" from their client.
	'''
	setPaused(val, cn)