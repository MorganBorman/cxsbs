import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
		
import time

import cxsbs
Players = cxsbs.getResource("Players")
Events = cxsbs.getResource("Events")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
ServerCore = cxsbs.getResource("ServerCore")

pluginCategory = 'Auth'

SettingsManager.addSetting(Setting.BoolSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="automatically_request_auth", 
													displayName="Automatically request auth", 
													default=True, 
													doc="Whether or not to automatically request auth from users when they connect."
												))

SettingsManager.addSetting(Setting.Setting		(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="automatic_request_description", 
													displayName="Automatic request description", 
													default="mydomain.com", 
													doc="Description to send when automatically requesting clients auth key."
												))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

@Events.eventHandler("player_connect")
def onConnect(cn):
	if settings["autoAuth"]:
		p = Players.player(cn)
		p.requestAuth(settings["authDesc"])

def genKeyPair(keySeed):
	newSeed = ""
	timestring = str(time.time())
	
	for i in range(len(keySeed)):
			newSeed += keySeed[i]
			newSeed += timestring[i % (len(timestring) - 1)]

	return ServerCore.genAuthKey(newSeed)


