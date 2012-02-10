import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
Server = cxsbs.getResource("Server")
Commands = cxsbs.getResource("Commands")
Events = cxsbs.getResource("Events")
Messages = cxsbs.getResource("Messages")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Timers = cxsbs.getResource("Timers")
	
pluginCategory = 'Pause'
pluginSubcategory = 'General'
	
SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="default_resume_count", 
												displayName="Default resume count", 
												default=5,
												doc="Default number of seconds to count down before resuming."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="max_count", 
												displayName="Max count time", 
												default=10,
												doc="Max number of seconds to count down."
											))

settings = SettingsManager.getAccessor(pluginCategory, pluginSubcategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='resuming', 
						displayName='Resuming', 
						default="${info}Resuming in ${green}${seconds}${white}",
						doc="Message to print player is removed from a group."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
	
@Events.eventHandler('player_pause')
def onPlayerPause(cn, val):
	'''
	@commandType
	@allowGroups __admin__ __master__
	@denyGroups
	@doc This command type event occurs when a player issues "/pausegame <value>" from their client. Will pause or resume the game instantly.
	'''
	Server.setPaused(val, cn)
	
@Commands.commandHandler('pause')
def onPause(cn, args):
	'''
	@description Pause the game
	@usage
	@allowGroups __admin__ __master__
	@denyGroups
	@doc pause the game
	'''
	Server.setPaused(True, cn)
	
def resumeTimer(count, cn):
	if count > 0:
		messager.sendMessage('resuming', dictionary={'seconds': count})
		Timers.addTimer(1000, resumeTimer, (count-1, cn))
	else:
		Server.setPaused(False, cn)

@Commands.commandHandler('resume')
def onResume(cn, args):
	'''
	@description Resume the game
	@usage (count)
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Resume the game with a counter.
	'''
	try:
		count = int(args)
		if count > settings['max_count']:
			count = settings['max_count']
	except:
		count = settings['default_resume_count']
		
	resumeTimer(count, cn)