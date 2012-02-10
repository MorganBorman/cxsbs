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

pluginCategory = 'Capacity'
pluginSubcategory = 'General'

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="pause_when_vacant", 
												displayName="Pause when vacant", 
												default=True,
												doc="Whether or not the server should pause itself when it has no clients."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="resume_on_first_client", 
												displayName="Resume on first client", 
												default=True,
												doc="Whether or not the server should unpause itself when it becomes occupied again."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="resize", 
												displayName="Resize", 
												default=True,
												doc="Resize the server when players spectate and the server is full."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="default_size", 
												displayName="Default size", 
												default=8,
												doc="Default size of the server. This is the size that the server should\
												Initialize with and which it should return to when the server empties."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="max_size", 
												displayName="Max size", 
												default=24,
												doc="Maximum size of the server. This is the max size that the server should resize to."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="resize_by", 
												displayName="resize_by", 
												default=2,
												doc="This is the amount by which the server should resize ."
											))

settings = SettingsManager.getAccessor(pluginCategory, pluginSubcategory)

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
	if Server.clientCount() == 1 and settings["resume_on_first_client"]:
		Server.setPaused(False)

@Events.eventHandler('player_spectated')
@Events.eventHandler('player_connect')
@Events.eventHandler('player_disconnect')
@Events.eventHandler('player_unspectated')
def checkSize(cn):
	if not settings["resize"]:
		return
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