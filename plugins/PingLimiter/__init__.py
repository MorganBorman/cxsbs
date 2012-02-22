import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		Players.update_session_vars_template({'average_ping': 0})
		
		global limiter
		limiter = PingLimiter()
		Timers.addTimer(settings['action_interval'], limiter.checkPlayers, ())
		
	def unload(self):
		pass
	
import cxsbs
Timers = cxsbs.getResource("Timers")
Commands = cxsbs.getResource("Commands")
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
ServerCore = cxsbs.getResource("ServerCore")
Logging = cxsbs.getResource("Logging")
Messages = cxsbs.getResource("Messages")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")

import groups

from groups import Group
from groups.Query import Is, Not, Select, Intersection

pluginCategory = 'PingLimiter'
pluginSubcategory = 'General'
	
SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="max_ping", 
												displayName="Max ping", 
												default=300,
												doc="Maximum ping to allow before spectating players."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="action_interval", 
												displayName="Action Interval", 
												default=5000,
												doc="Time between checks of all players pings in milliseconds."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="enabled", 
												displayName="Enabled", 
												default=True,
												doc="Should the ping limiter be enabled on startup."
											))

settings = SettingsManager.getAccessor(pluginCategory, pluginSubcategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='action', 
						displayName='action', 
						default="${info}The ping limiter is now ${blue}${status}${white}.",
						doc="Message to print to show whether or not the ping limiter has just been enabled or disabled."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='action_message', 
						displayName='Action message', 
						default="${info}You have been spectated for ${red}high ping${white}. Please lower your ping if you wish to play here.",
						doc="Message to print privately when someone has been spectated for high ping."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='deny_unspectate', 
						displayName='Deny unspectate', 
						default="${denied}You have ${red}high ping${white}. You cannot play until it is lowered.",
						doc="Message to print privately when someone tries to unspectate with high ping."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='public_action_message', 
						displayName='Public Action message', 
						default="${info}${green}${name}${white} has been spectated for ${red}high ping${white}.",
						doc="Message to print publicly when someone has been spectated for high ping."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

class PingLimiter:
	def __init__(self):
		self.enabled = settings['enabled']
		
	def checkPlayers(self):
		Timers.addTimer(settings['action_interval'], self.checkPlayers, ())
		if not self.enabled:
			return
		self.update_averages()
		
		for player in Players.all():
			if not player.isSpectator() and player.sessionvars['average_ping'] > settings['max_ping']:
				player.spectate()
				
				messager.sendPlayerMessage('action_message', player)
				
				messageGroup = Players.AllPlayersGroup.query(Select(cn=Not(Is(player.cn)))).all()
				messager.sendMessage('public_action_message', messageGroup, dictionary={'name':player.name()})
				
	def update_averages(self):
		"""
		Uses an exponential average, this will punish spikes harder than a multiple of instances calculated into an average.
		A spike-friendlier method is to arrange a list of values and calculate the average on the whole list divided by its length,
		like this: sum(pingvalueslist)/len(pingvalueslist) //Henrik L
		"""
		for player in Players.all():
				player.sessionvars['average_ping'] = (player.sessionvars['average_ping'] + player.ping()) / 2

@Events.policyHandler('player_unspectate')
def onUnspectate(cn, tcn):
	if cn != tcn:
		return True
	
	p = Players.player(cn)
	
	if p.sessionvars['average_ping'] > settings['max_ping'] and limiter.enabled:
		messager.sendPlayerMessage('deny_unspectate', p)
		return False

@Commands.commandHandler('pinglimiter')
def pingLimiterCmd(cn, args):
	'''
	@description Enable or disable the ping limiter
	@usage enable/disable
	@allowGroups __admin__
	@denyGroups
	@doc Enable or disable spectating of high ping players.
	'''
	
	if args == 'enable':
		limiter.enabled = True
		messager.sendMessage('action', dictionary={'status': 'enabled'})
	elif args == 'disable':
		limiter.enabled = False
		messager.sendMessage('action', dictionary={'status': 'disabled'})
	else:
		raise Commands.UsageError('enable/disable')