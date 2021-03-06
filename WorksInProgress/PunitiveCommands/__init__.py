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
Players = cxsbs.getResource("Players")
PlayerDisconnect = cxsbs.getResource("PlayerDisconnect")

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
						symbolicName="player_smited", 
						displayName="Player smited", 
						default="${info}${green}${smited}${white} has been smited by ${orange}${smiter}", 
						doc="Message to print when a player is smited."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="punitive_effects_cleared", 
						displayName="Punitive effects cleared", 
						default="${info}All ${blue}bans${white}, ${blue}mutes${white}, and ${blue}force spectates${white} with the reason, ${red}${reason}${white}, have been cleared.", 
						doc="Message to print when a punitive action is applied to a player."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

import timestring

def extractCommonActionDetails(cn, args):
	args = args.split()
	
	if len(args) < 1:
		raise Commands.UsageError()
	else:
		
		if ":" in args[0]:
			sp = args[0].split(':')
			
			if len(sp) != 2:
				raise Commands.ArgumentValueError("Extra ':' found when determining command target.")
			
			args[0] = sp[0]
			
			mask = sp[1]
		else:
			mask = "255.255.255.255"
			
		try:
			tcn = int(args[0])
		except:
			raise Commands.ArgumentValueError("You must supply a valid player cn.")
	
	responsible_cn = cn
	
	if len(args) < 2:
		seconds = settings['default_action_interval']
	else:
		try:
			seconds = timestring.parseTimeString(args[1])[1]
		except timestring.MalformedTimeString:
			raise Commands.ArgumentValueError("That time string does not seem to be valid.")
	
	if len(args) < 3:
		reason = settings['default_reason']
	else:
		try:
			reason = ' '.join(args[2:])
		except:
			raise Commands.UsageError()
		
	Logging.debug("Action details: " + str((tcn, seconds, reason, responsible_cn, mask)))
		
	return (tcn, seconds, reason, responsible_cn, mask)

@Commands.commandHandler('mute')
def onMuteCommand(cn, args):
	'''
	@threaded
	@description Mute a player
	@usage <cn>(:mask) (time string) (reason)
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Add an ip mute on a player.
	'''
	details = extractCommonActionDetails(cn, args)
	MuteCore.addMute(*details)

@Commands.commandHandler('ban')
def onBanCommand(cn, args):
	'''
	@threaded
	@description Ban a player
	@usage <cn>(:mask) (time string) (reason)
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Add an ip ban on a player
	'''
	details = extractCommonActionDetails(cn, args)
	BanCore.addBan(*details)
	
@Events.eventHandler('player_kick')
def onKick(cn, tcn):
	'''
	@threaded
	@commandType
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Command type event triggered when a user issues the \"/kick\" command."
	'''
	BanCore.addBan(tcn, settings['default_action_interval'], settings['default_reason'], cn)

@Commands.commandHandler('spec')
def onSpecCommand(cn, args):
	'''
	@threaded
	@description force spectate a player
	@usage <cn>(:mask) (time string) (reason)
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Add an ip force spectate on a player
	'''
	details = extractCommonActionDetails(cn, args)
	SpectCore.addSpect(*details)

@Commands.commandHandler('disc')
def onDiscCommand(cn, args):
	'''
	@threaded
	@description Silently disconnect a player
	@usage <cn>
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Silently disconnect a player. Please use with caution.
	'''
	args = args.split(' ')
	try:
		tcn = int(args[0])
		
		p = Players.player(cn)
		t = Players.player(tcn)
		p.logAction('Silently disconnected: ' + t.name() + '@' + t.ipString())
		Events.execLater(PlayerDisconnect.disconnect, (tcn, PlayerDisconnect.DISC_NONE))
	except (KeyError):
		raise UsageError()
	
@Commands.commandHandler('smite')
def onSmiteCommand(cn, args):
	'''
	@threaded
	@description Cause a player to suicide
	@usage <cn>
	@allowGroups __admin__
	@denyGroups
	@doc Cause a player to suicide.
	'''
	if args == '':
		raise UsageError()
	p = Players.player(cn)
	t = Players.player(int(args))
	p.logAction('Smited: ' + t.name() + '@' + t.ipString())
	messager.sendMessage('player_smited', dictionary={'smiter':p.name(), 'smited':t.name()})
	Events.execLater(t.suicide, ())
	
@Commands.commandHandler('mutespectators')
def toggleMuteSpectators(cn, args):
	'''
	@threaded
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
	p.logAction('MuteSpectators: ' + action)
	MuteCore.messager.sendMessage('spectators_muted_toggled', dictionary={'action': action, 'name': p.name()})
	
@Events.eventHandler('server_clear_bans')
def reqClearBans(cn):
	'''
	@threaded
	@commandType
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Command type event triggered when a user issues the \"/clearbans\" command."
	'''
	BanCore.clearByReason(settings['default_reason'])
	MuteCore.clearByReason(settings['default_reason'])
	SpectCore.clearByReason(settings['default_reason'])
	p = Players.player(cn)
	p.logAction('Executed clear punitive measures.')
	messager.sendMessage('punitive_effects_cleared', dictionary={'reason': settings['default_reason']})
	
import prettytime

@Events.eventHandler('player_punished')
def onPlayerPunished(type, ip, seconds, expiration, reason, nick, responsible_ip, responsible_nick, time):
	dictionary = 	{
						'name': nick,
						'ip': ip,
						'time': prettytime.createDurationString(seconds),
						'action': type,
						'responsible': responsible_nick,
						'reason': reason,
					}
	
	messager.sendMessage('player_punished', dictionary=dictionary)
	
	logString = str(responsible_nick) + "@" + str(responsible_ip) + " has " + str(type) + " " + str(nick) + "@" + str(ip) 
	Logging.info(logString)
	