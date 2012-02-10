import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
ServerCore = cxsbs.getResource("ServerCore")
Events = cxsbs.getResource("Events")
Logging = cxsbs.getResource("Logging")
	
import ppwgen

pluginCategory = 'Invisibility'

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="password", 
												displayName="Invisible connect password", 
												default=ppwgen.generatePassword(),
												doc="Password used to allow clients connect as invisible."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="allow", 
												displayName="Allow", 
												default=True,
												doc="Allow clients to connect invisibly if they connect with the password."
											))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

@Events.policyHandler('connect_invisible')
def connectInvisible(cn, pwd):
	if not settings["allow"]:
		return False
	if pwd == ServerCore.hashPassword(cn, settings["password"]):
		cxsbs.AsyncronousExecutor.dispatch(ServerCore.playerMessage, time=1, args=(cn, "You have connected invisibly. Please behave and act responsibly."))
		Logging.info("Client connected invisibly")
		return True
	else:
		return False