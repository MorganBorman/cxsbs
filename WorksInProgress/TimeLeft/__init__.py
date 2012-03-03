import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
Commands = cxsbs.getResource("Commands")
Messages = cxsbs.getResource("Messages")
ServerCore = cxsbs.getResource("ServerCore")
Players = cxsbs.getResource("Players")

pluginCategory = "TimeLeft"

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='malformed_time_string', 
						displayName='Malformed time string', 
						default="${error}That time string does not seem to be valid.",
						doc="Message to print player provides a strange timestring."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='time_changed', 
						displayName='Time changed', 
						default="${info}The time remaining has been set to ${yellow}${timeleft}${white} by ${green}${name}${white}.",
						doc="Message to print player changes the amount of time left."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
	
import timestring, prettytime
	
@Commands.commandHandler('timeleft')
def onTimeLeft(cn, args):
	'''
	@description Set the amount of time left in the game using a time string.
	@usage 5m
	@usage +5m
	@usage -55s
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Sets the time left in the game.
	'''
	if args == '':
		raise UsageError()

	p = Players.player(cn)

	try:
		timeModification = timestring.parseTimeString(args)
	except timestring.MalformedTimeString:
		messager.sendPlayerMessage('malformed_time_string', p)
		return
	
	if timeModification[0] == '=':
		targetTime = timeModification[1]
	elif timeModification[0] == '+':
		targetTime = ServerCore.secondsRemaining() + timeModification[1]
	else:
		targetTime = ServerCore.secondsRemaining() - timeModification[1]
		
	targetTime = max(0, targetTime)
		
	ServerCore.setSecondsRemaining(targetTime)
	
	displaytime = prettytime.createDurationString(ServerCore.secondsRemaining())
	
	p.logAction('TimeLeft set: ' + displaytime)
	
	messager.sendMessage('time_changed', dictionary={'timeleft':displaytime, 'name':p.name()})