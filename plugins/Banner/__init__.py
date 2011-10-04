import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		displayBanner()
		
	def unload(self):
		pass
	
import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Players = cxsbs.getResource("Players")
Timers = cxsbs.getResource("Timers")
Commands = cxsbs.getResource("Commands")
Messages = cxsbs.getResource("Messages")
ServerCore = cxsbs.getResource("ServerCore")

pluginCategory="Banner"

SettingsManager.addSetting(Setting.IntSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="banner_interval",
													displayName="Banner interval", 
													default=3600,
													doc="Number of seconds in between banner messages.",
												))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

Messages.addMessage	(
						category=pluginCategory,
						subcategory="General", 
						symbolicName="banner_message", 
						displayName="map_changed", 
						default="${info}CXSBS - The Canonical eXtensible SauerBraten Server. Online for: ${green}${uptime}${white}.", 
						doc="Message to print once every banner interval."
					)

messager = Messages.getAccessor(category=pluginCategory, subcategory="General")

import datetime

def getComponent(value, identifier):
	if value <= 0:
		return ""
	returnValue = str(value) + " " + str(identifier)
	if value == 1:
		return returnValue
	else:
		return returnValue + "s"

def createDurationString(seconds):
	timeObject = datetime.timedelta(seconds=seconds)
	
	years = int(timeObject.days/365)
	days = int(timeObject.days % 365)
	hours = int(timeObject.seconds/3600)
	minutes = int(int(timeObject.seconds % 3600) / 60)
	seconds = int(int(timeObject.seconds % 3600) % 60)
	
	timeList = []
	
	component = getComponent(years, "year")
	if component != "":
		timeList.append(component)
		
	component = getComponent(days, "day")
	if component != "":
		timeList.append(component)
		
	component = getComponent(hours, "hour")
	if component != "":
		timeList.append(component)
		
	component = getComponent(minutes, "minute")
	if component != "":
		timeList.append(component)
		
	component = getComponent(seconds, "second")
	if component != "":
		timeList.append(component)
		
	if len(timeList) == 0:
		return "0 seconds"
		
	if len(timeList) == 1:
		return timeList[0]
	
	if len(timeList) > 2:
		timeList = [', '.join(timeList[:-1]), timeList[-1]]
		
	return ', and '.join(timeList)

def displayBanner():
	messager.sendMessage('banner_message', dictionary={'uptime': createDurationString(int(ServerCore.uptime()/1000))})
	Timers.addTimer(settings['banner_interval']*1000, displayBanner, ())

@Commands.commandHandler('info')
def infoCmd(cn, args):
	'''
	@description Get the banner info message
	@usage
	@allowGroups __all__
	@denyGroups
	@doc Get the banner info message.
	'''
	p = Players.player(cn)
	messager.sendPlayerMessage('banner_message', p, dictionary={'uptime': createDurationString(int(ServerCore.uptime()/1000))})

