import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global shotDict
		shotDict = {}
		
	def unload(self):
		pass
	
import cxsbs
Events = cxsbs.getResource("Events")
BanCore = cxsbs.getResource("BanCore")
MuteCore = cxsbs.getResource("MuteCore")
SpectCore = cxsbs.getResource("SpectCore")
Logging = cxsbs.getResource("Logging")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")

import time
from collections import deque

pluginCategory = "CheatDection"

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="action", 
												displayName="Action", 
												default="spectate",
												doc="What action should be taken when cheating is detected. Valid actions are; ban, mute, and spectate. Leave blank to disable taking action."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="reason", 
												displayName="Reason", 
												default="Cheating",
												doc="What reason should be given when action is taken against a cheater. Valid actions are; ban, mute, and spectate. Leave blank to disable taking action."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="action_duration", 
												displayName="Action duration", 
												default=4500,
												doc="Duration for which an action should persist. ie how long should a player be banned muted or spectated."
											))

settings = SettingsManager.getAccessor(pluginCategory, "General")

weaponReloadTimes = 	{
							0:250,
							1:1400,
							2:100,
							3:800,
							4:1500,
							5:500,
							6:500,
						}

weapons = 	{
				0: "fist",
				1: "shotgun",
				2: "chaingun",
				3: "rocket",
				4: "rifle",
				5: "grenade launcher",
				6: "pistol",
			}

def takeAction(cn):
	action = settings['action']
	reason = settings['reason']
	duration = settings['action_duration']
	
	if action == "ban":
		BanCore.addBan(cn, duration, reason)
	elif action == "spectate":
		SpectCore.addSpect(cn, duration, reason)
	elif action == "mute":
		MuteCore.addMute(cn, duration, reason)
	elif action == "":
		pass
	else:
		Logging.error("Failed take action against player regarding cheating of type: " + self.settings['type_name'] + ". reason: invalid configured action: " + str(action))

@Events.eventHandler('player_shot')
def onPlayerShot(cn, millis, gun):
	if cn in shotDict.keys():
		while len(shotDict[cn]) > 1:
			shotDict[cn].pop()
			
		shotDict[cn].appendleft((gun, millis))
		
		if len(shotDict[cn]) > 1:
			firstShot = shotDict[cn][1]
			secondShot = shotDict[cn][0]
			
			validWeaponReloadTime = weaponReloadTimes[firstShot[0]]
			timeBetweenShots = (secondShot[1] - firstShot[1])
			Logging.debug("CheatDetection: " + weapons[firstShot[0]] + " reload time: " + str(timeBetweenShots) + " normal time: " + str(validWeaponReloadTime))
			if timeBetweenShots < 0:
				return
			if (validWeaponReloadTime-timeBetweenShots) > 0:
				takeAction(cn)
			
@Events.eventHandler('player_disconnect')
def onPlayerDisconnect(cn):
	if cn in shotDict.keys():
		del shotDict[cn]
		
@Events.eventHandler('player_connect')
def onPlayerConnect(cn):
	if cn in shotDict.keys():
		onPlayerDisconnect(cn)
	shotDict[cn] = deque()
	
@Events.eventHandler('player_shot_hit')
def onPlayerShotHit(cn, tcn, lifeseq, dist, rays):
	print cn, tcn, lifeseq, dist, rays