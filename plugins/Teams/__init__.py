import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global teamManager
		teamManager = TeamManager()
		
		Events.registerServerEventHandler('autoteam', teamManager.autoTeam)
		Events.registerServerEventHandler('player_switch_team', teamManager.onSwitchTeam)
		Events.registerServerEventHandler('player_set_team', teamManager.onSetTeam)
		Events.registerServerEventHandler('player_connect_delayed', teamManager.onConnect)
		Events.registerServerEventHandler('player_disconnect', teamManager.onDisconnect)
		Events.registerServerEventHandler('player_spectated', teamManager.onSpectate)
		Events.registerServerEventHandler('player_unspectated', teamManager.onUnspectate)
		
		Events.registerPolicyEventHandler('player_switch_team', teamManager.allowSwitchTeam)
		Events.registerPolicyEventHandler('player_set_team', teamManager.allowSetTeam)
		
	def unload(self):
		pass
	
import cxsbs
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Game = cxsbs.getResource("Game")
Messages = cxsbs.getResource("Messages")
Commands = cxsbs.getResource("Commands")
UI = cxsbs.getResource("UI")
ServerCore = cxsbs.getResource("ServerCore")
SettingsManager = cxsbs.getResource("SettingsManager")
Setting = cxsbs.getResource("Setting")

import time

pluginCategory = "Teams"

SettingsManager.addSetting(Setting.BoolSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="start_sticky",
													displayName="Start sticky", 
													default=False,
													doc="Should the server start in sticky team mode.",
												))

SettingsManager.addSetting(Setting.BoolSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="start_locked",
													displayName="Start locked", 
													default=False,
													doc="Should the server start in locked team mode.",
												))

#Default modes where clients can switch team
switchteam_modes = 	[
						"instateam",
						"efficteam",
						"tacteam",
						"capture",
						"regencapture",
						"ctf",
						"instactf",
						"protect",
						"instaprotect",
						"hold",
						"instahold",
						"efficctf",
						"efficprotect",
						"effichold",
					]

SettingsManager.addSetting(Setting.ListSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="switchteam_modes",
													displayName="Switch team modes", 
													default=switchteam_modes,
													doc="Modes in which clients can switch teams.",
												))

# modes where clients can set team name
setteam_modes = 	[
						"team",
						"instateam",
						"efficteam",
						"capture",
						"regencapture",
					]

SettingsManager.addSetting(Setting.ListSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="setteam_modes",
													displayName="Set team modes", 
													default=setteam_modes,
													doc="Modes in which clients can custom team names.",
												))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

SettingsManager.addSetting(Setting.ListSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="setteam_modes",
													displayName="Set team modes", 
													default=setteam_modes,
													doc="Modes in which clients can custom team names.",
												))

permissionsCategory = "Permissions"

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_set_team",
													displayName="Allow groups set_team", 
													default=['__master__', '__admin__'],
													doc="Groups which are allowed to set the team of another player.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="deny_groups_set_team",
													displayName="Deny groups set_team", 
													default=[],
													doc="Groups which are not allowed to set the team of another player.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_switch_when_locked",
													displayName="Allow groups switch when locked", 
													default=['__master__', '__admin__'],
													doc="Groups which are allowed to switch teams when the teams are locked.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="deny_groups_switch_when_locked",
													displayName="Deny groups switch when locked", 
													default=[],
													doc="Groups which are not allowed to switch teams when the teams are locked.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_switch_teams",
													displayName="Allow groups switch teams", 
													default=['__all__'],
													doc="Groups which are allowed to change teams.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="deny_groups_switch_teams",
													displayName="Deny groups switch teams", 
													default=[],
													doc="Groups which are not allowed change teams.",
												))

groupSettings = SettingsManager.getAccessor(category=permissionsCategory, subcategory=pluginCategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="denied_team_change", 
						displayName="Denied team change", 
						default="${denied}You are not permitted to join team ${blue}${team}${white} in game mode ${green}${modeName}${white}.", 
						doc="Message to print when a team change is disallowed."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="denied_team_set", 
						displayName="Denied team set", 
						default="${denied}You are not permitted to move players to team ${blue}${team}${white} in game mode ${green}${modeName}${white}.", 
						doc="Message to print when a team change is disallowed."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="team_control_status", 
						displayName="Team control status", 
						default="${info}Team control status: locked(${locked}), sticky(${sticky})", 
						doc="Format of message to print when changing team control status."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="teams_locked", 
						displayName="Teams locked", 
						default="${denied}The teams are ${red}locked${white}, you cannot switch.", 
						doc="Format of message to print when user tries to switch while teams are locked."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="team_set", 
						displayName="Team set", 
						default="${info}${green}${actor}${white} has been moved to team ${blue}${teamName}${white} by ${green}${director}${white}.", 
						doc="Format of message to print when a players team has been set by another player."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="team_switch", 
						displayName="Team switch", 
						default="${info}${green}${name}${white} switched to team ${blue}${teamName}${white}.", 
						doc="Format of message to print when a player switches teams."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

def isSafeTeam(team):
	'''Is team safe based on current mode.
	   ex: isSafeTeam('test') would return false in capture mode.'''
	mode = Game.modeName(Game.currentMode())
	if mode in settings["setteam_modes"]:
		return True
	if mode in settings["switchteam_modes"] and team in ['good', 'evil']:
		return True
	return False

@Events.policyHandler('player_switch_team')
def onSwitchTeam(cn, team):
	p = Players.player(cn)
	
	if p.team() == team:
		return False
	
	if not p.isPermitted(groupSettings['allow_groups_switch_teams'], groupSettings['deny_groups_switch_teams']):
		UI.insufficientPermissions(cn)
		return False
	
	if isSafeTeam(team):
		return True
	else:
		messager.sendPlayerMessage('denied_team_change', p, dictionary={'team': team, 'modeName': Game.modeName(Game.currentMode())})
		return False

@Events.policyHandler('player_set_team')
def onSetTeam(cn, tcn, team):
	p = Players.player(cn)
	
	if p.team() == team:
		return False
	
	if not p.isPermitted(groupSettings['allow_groups_set_team'], groupSettings['deny_groups_set_team']):
		UI.insufficientPermissions(cn)
		return False

	if isSafeTeam(team):
		return True
	else:
		messager.sendPlayerMessage('denied_team_set', p, dictionary={'team': team, 'modeName': Game.modeName(Game.currentMode())})
		return False

class TeamManager:
	def __init__(self):
		self.locked = settings["start_locked"]
		self.sticky = settings["start_sticky"]
		
		#maintain a list describing which team each player is on
		self.playerTeams = {} #cn: team
		
		#To keep track of what team to force players to when they unspectate while teams were locked and they spectated.
		self.unspectateTeams = {} #cn: team
		
	def autoTeam(self):
		"""Put the players on the correct teams prior to the game starting"""
		if self.sticky:
			for key in self.playerTeams.keys():
				try:
					#print key, self.playerTeams[key]
					ServerCore.pregameSetTeam(key, self.playerTeams[key])
				except ValueError:
					print "Value error in plugin Team's autoteam function."
		
	def allowSwitchTeam(self, cn, team):
		"""for allow_switch_teams policy handler"""
		p = Players.player(cn)
		
		if self.locked:
			if p.isPermitted(groupSettings["allow_groups_switch_when_locked"], groupSettings["deny_groups_switch_when_locked"]):
				return True
			elif p.isSpectator():
				return True
			else:
				messager.sendPlayerMessage('teams_locked', p)
				return False
		else:
			return True
			
	def allowSetTeam(self, cn, tcn, team):
		return True
				
	def onSpectate(self, cn):
		p = Players.player(cn)
		self.unspectateTeams[cn] = self.playerTeams[cn]
		try:
			del self.playerTeams[cn]
		except IndexError:
			pass
				
	def onUnspectate(self, cn):
		if self.locked:
			p = Players.player(cn)
			if cn in self.unspectateTeams.keys():
				team = self.unspectateTeams[cn]
				del self.unspectateTeams[cn]
				p.setTeam(team)
				self.playerTeams[cn] = team
			else:
				self.playerTeams[cn] = p.team()
		
	def onSwitchTeam(self, cn, team):
		if Events.triggerPolicyEvent('player_switch_team', (cn, team)):
			p = Players.player(cn)
			Events.execLater(p.suicide, ())
			p.setTeam(team)
			messager.sendMessage('team_switch', dictionary={'teamName': p.team(), 'name': p.name()})
			self.playerTeams[cn] = team
			
	def onSetTeam(self, cn, tcn, team):
		if tcn == cn:
			self.onSwitchTeam(cn, team)
		elif Events.triggerPolicyEvent('player_set_team', (cn, tcn, team)):
			p = Players.player(cn)
			q = Players.player(tcn)
			Events.execLater(q.suicide, ())
			q.setTeam(team)
			messager.sendMessage('team_set', dictionary={'teamName': q.team(), 'actor': q.name(), 'director': p.name()})
			self.playerTeams[tcn] = team
		
	def onConnect(self, cn):
		"""Maintain the self.teams data structure"""
		p = Players.player(cn)
		if not p.isSpectator():
			team = p.team()
			self.playerTeams[cn] = team
		
	def onDisconnect(self, cn):
		try:
			del self.playerTeams[cn]
		except:
			pass
		
	def lockedTeams(self, value):
		"""Stops players changing teams without appropriate group privileges"""
		self.locked = value
		
	def isLockedTeams(self):
		return self.locked
	
	def stickyTeams(self, value):
		"""Keeps players on the same team across multiple games"""
		self.sticky = value
		
	def isStickyTeams(self):
		return self.sticky

def getTeamMode():
	modeString = ""
	if teamManager.isLockedTeams():
		modeString += "l"
	if teamManager.isStickyTeams():
		modeString += "s"
	return modeString

def setTeamMode(args):
	for c in args:
		if not c in " +-rls":
			raise Commands.UsageError('+/-<r|l|s>')
		
	if '-l' in args:
		teamManager.lockedTeams(False)
	elif '+l' in args or 'l' in args:
		teamManager.lockedTeams(True)
		
	if '-s' in args:
		teamManager.stickyTeams(False)
	elif '+s' in args or 's' in args:
		teamManager.stickyTeams(True)

@Commands.commandHandler('teammode')
def setTeamsCmd(cn, args):
	'''@description set the teams locked and or sticky.
	   @usage +/-<l|s>
	   @allowGroups __master__ __admin__
	   @denyGroup
	   @doc Set the locked and sticky team modes on or off.
	   Pass "+l" to turn on locking or a "-l" to turn it off.
	   Pass "+s" to turn on sticky or a "-s" to turn it off.
	   '''
	setTeamMode(args)
	dictionary={
			"locked": teamManager.isLockedTeams(), 
			"sticky": teamManager.isStickyTeams(),
			}
	messager.sendMessage('team_control_status', dictionary=dictionary)