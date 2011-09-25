from cxsbs.Plugin import Plugin

class Capacity(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass
		
import cxsbs
Config = cxsbs.getResource("Config")
Server = cxsbs.getResource("Server")
Events = cxsbs.getResource("Events")
Logging = cxsbs.getResource("Logging")
ServerCore = cxsbs.getResource("ServerCore")

def nearestGreaterMultiple(number, factor):
	n = 0
	while n < number:
		n += factor
	return n
		
def init():
	global resize, default_size, resize_by, pause_when_empty
	config = Config.PluginConfig('Capacity')
	resize = config.getBoolOption('Config', 'resize', True)
	pause_when_empty = config.getBoolOption('Config', 'pause_when_empty', True)
	default_size = config.getIntOption('Config', 'default_size', 8)
	max_size = config.getIntOption('Config', 'max_size', 24)
	resize_by = config.getIntOption('Config', 'resize_by', 2)
	del config
	
	if default_size % 2 == 1:
		Logging.warn("Even server sizes are recommended for consistent capacity scaling behavior.")
	
	@Events.eventHandler('no_clients')
	@Events.eventHandler('server_start')
	def onServerStart():
		if pause_when_empty:
			Server.setPaused(True)
		Server.setMaxClients(default_size)
	
	@Events.eventHandler('player_connect')
	def onConnect(cn):
		if Server.clientCount() == 1:
			Server.setPaused(False)
	
	@Events.eventHandler('player_spectated')
	@Events.eventHandler('player_connect')
	@Events.eventHandler('player_disconnect')
	@Events.eventHandler('player_unspectated')
	def checkSize(cn):
		newsize = 0
		clientCount = Server.clientCount()
		#print "maxClients - clientCount: " + str(Server.maxClients() - clientCount)
		if (Server.maxClients() - clientCount) >= resize_by:
			#print "try here"
			#check if we should downsize the server
			downsize = nearestGreaterMultiple(clientCount, resize_by)
			#print "or here"
			#print map(type, (default_size, downsize))
			newsize = max(default_size, downsize)
			#print "mayvbe here"
		elif clientCount == Server.maxClients():
			#check if we should increase size
			#print "foo"
			if (clientCount - Server.spectatorCount()) <= default_size:
				#print "boo"
				newsize = min(clientCount + resize_by, max_size)
		else:
			return
		Logging.debug('Adjusting server size to %i', newsize)
		Server.setMaxClients(newsize)