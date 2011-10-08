import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass

import cxsbs
MuteCore = cxsbs.getResource("MuteCore")
BanCore = cxsbs.getResource("BanCore")
SpectCore = cxsbs.getResource("SpectCore")
ServerCore = cxsbs.getResource("ServerCore")
Commands = cxsbs.getResource("Commands")
Messages = cxsbs.getResource("Messages")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Logging = cxsbs.getResource("Logging")
Events = cxsbs.getResource("Events")

pluginCategory = 'PunitiveActions'

SettingsManager.addSetting(Setting.IntSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="default_action_interval",
													displayName="Default action interval", 
													default=450,
													doc="Default number of seconds to apply punitive actions.",
												))

SettingsManager.addSetting(Setting.Setting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="default_reason",
													displayName="Default reason", 
													default="unspecified reason",
													doc="Default reason to give punitive actions where a reason is not specified.",
												))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="player_punished", 
						displayName="Player punished", 
						default="${info}${green}${name}${white}@${orange}${ip}${white} has been ${red}${action}${white} for ${time} seconds by ${blue}${responsible}${white} for ${red}${reason}${white}", 
						doc="Message to print when a punitive action is applied to a player."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="punitive_effects_cleared", 
						displayName="Punitive effects cleared", 
						default="${info}All ${blue}bans${white}, ${blue}mutes${white}, and ${blue}force spectates${white} with the reason, ${red}${reason}${white}, have been cleared.", 
						doc="Message to print when a punitive action is applied to a player."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

def extractCommonActionDetails(cn, args):
	if "%" in args:
		sp = args.split('%')
		if len(sp) > 2:
			raise Commands.UsageError()
		try:
			cidr = int(sp[1])
			args = sp[0]
		except:
			raise Commands.UsageError()
	else:
		cidr = 32
	
	args = args.split()
	
	if len(args) < 1:
		raise Commands.UsageError()
	else:
		try:
			tcn = int(args[0])
		except:
			raise Commands.UsageError()
	
	responsible_cn = cn
	
	if len(args) < 2:
		seconds = settings['default_action_interval']
	else:
		try:
			seconds = int(args[1])
		except:
			raise Commands.UsageError()
	
	if len(args) < 3:
		reason = settings['default_reason']
	else:
		try:
			reason = ' '.join(args[2:])
		except:
			raise Commands.UsageError()
		
	Logging.debug("Action details: " + str((tcn, seconds, reason, responsible_cn, cidr)))
		
	return (tcn, seconds, reason, responsible_cn, cidr)

@Commands.commandHandler('mute')
def onMuteCommand(cn, args):
	'''
	@description Mute a player
	@usage <cn> (seconds) (reason)%(cidr)
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Add an ip mute on a player.
	'''
	details = extractCommonActionDetails(cn, args)
	MuteCore.addMute(*details)

@Commands.commandHandler('ban')
def onBanCommand(cn, args):
	'''
	@description Ban a player
	@usage <cn> (seconds) (reason)%(cidr)
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Add an ip ban on a player
	'''
	details = extractCommonActionDetails(cn, args)
	BanCore.addBan(*details)

@Commands.commandHandler('spec')
def onSpecCommand(cn, args):
	'''
	@description force spectate a player
	@usage <cn> (seconds) (reason)%(cidr)
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Add an ip force spectate on a player
	'''
	details = extractCommonActionDetails(cn, args)
	SpectCore.addSpect(*details)

@Commands.commandHandler('disc')
def onDiscCommand(cn, args):
	'''
	@description Silently disconnect a player
	@usage <cn>
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Silently disconnect a player. Please use with caution.
	'''
	args = args.split(' ')
	try:
		tcn = int(args[0])
		ServerCore.playerDisc(tcn)
	except (KeyError):
		raise UsageError()
	
@Commands.commandHandler('mutespectators')
def toggleMuteSpectators(cn, args):
	'''
	@description Toggle muting of spectators
	@usage
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Toggle the status of mute spectators.
	'''
	if MuteCore.settings["mute_spectators"]:
		MuteCore.settings["mute_spectators"] = False
		action = "unmuted"
	else:
		MuteCore.settings["mute_spectators"] = True
		action = "muted"
		
	p = Players.player(cn)
	MuteCore.messager.sendMessage('spectators_muted_toggled', dictionary={'action': action, 'name': p.name()})
	
@Events.eventHandler('server_clear_bans')
def reqClearBans(cn):
	'''
	@commandType
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Command type event triggered when a user issues the \"/clearbans\" command."
	'''
	BanCore.clearByReason(settings['default_reason'])
	MuteCore.clearByReason(settings['default_reason'])
	SpectCore.clearByReason(settings['default_reason'])
	messager.sendMessage('punitive_effects_cleared', dictionary={'reason': settings['default_reason']})
	
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

@Events.eventHandler('player_punished')
def onPlayerPunished(type, ip, seconds, expiration, reason, nick, responsible_ip, responsible_nick, time):
		
	
	dictionary = 	{
						'name': nick,
						'ip': ip,
						'time': createDurationString(seconds),
						'action': type,
						'responsible': responsible_nick,
						'reason': reason,
					}
	
	messager.sendMessage('player_punished', dictionary=dictionary)
	
	logString = str(responsible_nick) + "@" + str(responsible_ip) + " has " + str(type) + " " + str(nick) + "@" + str(ip) 
	Logging.info(logString)
	