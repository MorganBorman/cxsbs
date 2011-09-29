import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		if settings["default_size"] % 2 == 1:
			Logging.warn("Even server sizes are recommended for consistent capacity scaling behavior.")
		
	def unload(self):
		pass
		
import cxsbs
Server = cxsbs.getResource("Server")
Events = cxsbs.getResource("Events")
Logging = cxsbs.getResource("Logging")
Setting = cxsbs.getResource("Setting")
ServerCore = cxsbs.getResource("ServerCore")
SettingsManager = cxsbs.getResource("SettingsManager")

SettingsManager.addSetting(Setting.BoolSetting('Capacity', 'General', 'pause_when_vacant', 'Pause when vacant', True))
SettingsManager.addSetting(Setting.BoolSetting('Capacity', 'General', 'resize', 'Resize server', True))
SettingsManager.addSetting(Setting.IntSetting('Capacity', 'General', 'default_size', 'Default server size', 8))
SettingsManager.addSetting(Setting.IntSetting('Capacity', 'General', 'max_size', 'Max server size', 24))
SettingsManager.addSetting(Setting.IntSetting('Capacity', 'General', 'resize_by', 'Resize server by', 2))

settings = SettingsManager.getAccessor('Capacity', 'General')

def nearestGreaterMultiple(number, factor):
	n = 0
	while n < number:
		n += factor
	return n
		
@Events.eventHandler('no_clients')
@Events.eventHandler('server_start')
def onServerStart():
	if settings["pause_when_vacant"]:
		Server.setPaused(True)
	Server.setMaxClients(settings["default_size"])

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
	if (Server.maxClients() - clientCount) >= settings["resize_by"]:
		#check if we should downsize the server
		downsize = nearestGreaterMultiple(clientCount, settings["resize_by"])
		newsize = max(settings["default_size"], downsize)
	elif clientCount == Server.maxClients():
		#check if we should increase size
		if (clientCount - Server.spectatorCount()) <= settings["default_size"]:
			newsize = min(clientCount + settings["resize_by"], settings["max_size"])
	else:
		return
	Logging.debug('Adjusting server size to %i', newsize)
	Server.setMaxClients(newsize)