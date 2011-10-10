import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global clanWarManager
		clanWarManager = ClanWarManager()
		
		Events.registerServerEventHandler('map_changed', clanWarManager.onMapChange)
		Events.registerServerEventHandler('player_disconnect', clanWarManager.onDisconnect)
		Events.registerServerEventHandler('player_spectated', clanWarManager.onSpectate)
		Events.registerServerEventHandler('player_unspectated', clanWarManager.onUnspectate)
		Events.registerServerEventHandler('intermission_begin', clanWarManager.onIntermission)
		
	def unload(self):
		pass
	
import cxsbs
Commands = cxsbs.getResource("Commands")
Server = cxsbs.getResource("Server")
Teams = cxsbs.getResource("Teams")
Events = cxsbs.getResource("Events")
Messages = cxsbs.getResource("Messages")
ServerCore = cxsbs.getResource("ServerCore")
Players = cxsbs.getResource("Players")
Game = cxsbs.getResource("Game")
Timers = cxsbs.getResource("Timers")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource('SettingsManager')

from groups import Group
from groups.Query import Contains, Not, Select, Intersection

import time, random

pluginCategory = "ClanWar"
pluginSubcategory = 'General'

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory=pluginSubcategory, 
												symbolicName="end_when_vacant", 
												displayName="End when vacant", 
												default=True,
												doc="Whether or not the clanwar should end when there are no clients connected."
											))

settings = SettingsManager.getAccessor(pluginCategory, pluginSubcategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="count_down", 
						displayName="Count down", 
						default="Battle starts in ${green}${count}${white}.", 
						doc="Message to print for count down at the start of the clanwar."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="count_ended", 
						displayName="Count ended", 
						default="Fight!", 
						doc="Message to print after count down at the start of the clanwar."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="interclan_war_initiated", 
						displayName="Interclan war initiated", 
						default="A bitter feud has sprung up between ${blue}${clan1}${white} and ${red}${clan2}${white}. Event now, final battle preparations are underway, please wait while they are finished.", 
						doc="Message to print at the start of a clanwar between two clans."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="intraclan_war_initiated", 
						displayName="Intraclan war initiated", 
						default="Hard times foment discontent and unrest within ${blue}${clan}${white}. Soon a bitter conflict shall flare up, please wait while the final preparations are made.", 
						doc="Message to print at the start of an internal clanwar."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="generic_war_initiated", 
						displayName="generic_war_initiated", 
						default="Hard times foment discontent. Please await the impending conflict.", 
						doc="Message to print at the start of a generic clanwar."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="intermission", 
						displayName="Intermission", 
						default="An eerie calm has descended on this plain of destruction. Will the tired and wounded combatants resume their quarrel?", 
						doc="Message to print inbetween the games of a clanwar."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="interruption", 
						displayName="Interruption", 
						default="The balance of the force has been disrupted. Please check teams and use \"/pausegame 0\" to resume.", 
						doc="Message to print when someone leaves or otherwise changes the opposing forces."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="clanwar_ended", 
						displayName="Clanwar_ended", 
						default="A peace has returned to the land now that the clanwar has ended.", 
						doc="Message to print when the clanwar has ended."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

def clanWarTimer(count):
	if count > 0:
		messager.sendMessage("count_down", dictionary={"count": count})
		Timers.addTimer(1000, clanWarTimer, (count-1,))
	else:
		messager.sendMessage("count_ended")
		Server.setFrozen(False)
		Server.setPaused(False)
		Timers.addTimer(750, ServerCore.setAllowShooting, (True,))
	
class ClanWar:
	def __init__(self, clan1=None, clan2=None):
		self.combatants = []
	
		self.firstIntermission = True
		
		ServerCore.setPersistentIntermission(True)
		ServerCore.setSecondsRemaining(0)
		
		self.restoreMasterMode = ServerCore.masterMode()
		self.restoreTeamMode = Teams.getTeamMode()
		
		Server.setMasterMode(2)
		Teams.setTeamMode('+l+s')
		
		if clan1 != None and clan2 != None:
			Timers.addTimer(1000, messager.sendMessage, ("interclan_war_initiated",), {'dictionary':{"clan1": clan1, "clan2": clan2}})
		elif clan1 !=None:
			Timers.addTimer(1000, messager.sendMessage, ("intraclan_war_initiated",), {'dictionary':{"clan": clan1}})
		else:
			Timers.addTimer(1000, messager.sendMessage, ("generic_war_initiated",))
	
		if clan1 != None:
			self.clan1 = Players.AllPlayersGroup.query(Select(name=Contains(clan1)))
		else:
			self.clan1 = Players.EmptyPlayersGroup
			
		if clan2 != None:
			self.clan2 = Players.AllPlayersGroup.query(Select(name=Contains(clan2)))
		else:
			self.clan2 = Players.EmptyPlayersGroup
			
		if clan1 != None and clan2 != None:
			self.others = Players.AllPlayersGroup.query(Intersection(Select(name=Not(Contains(clan1))), Select(name=Not(Contains(clan2)))))
		elif clan1 != None:
			self.others = Players.AllPlayersGroup.query(Select(name=Not(Contains(clan1))))
		else:
			self.others = Players.AllPlayersGroup
		
		self.clan1.all().action('unspectate', ())
		if clan2 != None:
			self.clan2.all().action('unspectate', ())
			
		if self.others.all() != None:
			self.others.all().action('spectate', ())
		
		if clan2 != None:
			teams = ["good", "evil"]
			random.shuffle(teams)
			self.clan1.all().action('setTeam', (teams[0],))
			self.clan2.all().action('setTeam', (teams[1],))
		else:
			pass
			#teamBalance()
			
	def saveCombatants(self):
		self.combatants = ServerCore.players()
		
	def isCombatant(self, cn):
		return cn in self.combatants
	
	def onMapChange(self, gameMap, gameMode):
		self.isIntermission = False
		self.saveCombatants()
		Timers.addTimer(1, self.start, ())
			
	def onDisconnect(self, cn):
		if self.isCombatant(cn) and not self.isIntermission:
			messager.sendMessage("interruption")
			Server.setPaused(True, -1)
			self.saveCombatants()
			
	def onSpectate(self, cn):
		if self.isCombatant(cn) and not self.isIntermission:
			messager.sendMessage("interruption")
			Server.setPaused(True, -1)
			self.saveCombatants()
		
	def onUnspectate(self, cn):
		self.saveCombatants()
		
	def onIntermission(self):
		self.isIntermission = True
		if not self.firstIntermission:
			messager.sendMessage("intermission")
		
	def start(self):
		ServerCore.setAllowShooting(False)
		
		Server.setPaused(True, -1)
		Server.setFrozen(True)
		
		self.saveCombatants()
		
		clanWarTimer(10)
		
	def end(self):
		Server.setMasterMode(self.restoreMasterMode)
		Teams.setTeamMode(self.restoreTeamMode)
		ServerCore.setPersistentIntermission(False)
		messager.sendMessage("clanwar_ended")

class ClanWarManager:
	def __init__(self):
		self.activeClanwar = None
		
	def initiate(self, clan1, clan2):
		self.end()
		self.activeClanwar = ClanWar(clan1, clan2)
		
	def end(self):
		if self.enabled():
			self.activeClanwar.end()
		self.activeClanwar = None
		
	def enabled(self):
		return self.activeClanwar != None
	
	def onMapChange(self, gameMap, gameMode):
		if self.enabled():
			self.activeClanwar.onMapChange(gameMap, gameMode)
	
	def onDisconnect(self, cn):
		if self.enabled():
			self.activeClanwar.onDisconnect(cn)
			
	def onSpectate(self, cn):
		if self.enabled():
			self.activeClanwar.onSpectate(cn)
			
	def onUnspectate(self, cn):
		if self.enabled():
			self.activeClanwar.onUnspectate(cn)
			
	def onIntermission(self):
		if self.enabled():
			self.activeClanwar.onIntermission()

@Commands.commandHandler('clanwar')
def clanWar(cn, args):
	'''
	@threaded
	@description Toggle clanwar mode
	@usage <clantag1> (clantag2)
	@usage
	@allowGroups __master__ __admin__
	@denyGroups
	@doc This command is used to put the server into a special clanwar mode
	'''
	if Server.isFrozen():
		raise Commands.StateError('Server is currently frozen')
	
	if clanWarManager.enabled():
		clanWarManager.end()
	else:
		clan1 = None
		clan2 = None
		if args == '':
			pass
		else:
			args = args.split()
			if len(args) == 1:
				clan1 = args[0]
			elif len(args) >= 2:
				clan1 = args[0]
				clan2 = args[1]
				
		clanWarManager.initiate(clan1, clan2)
		
@Events.eventHandler('no_clients')
def onEmpty():
	if settings["end_when_vacant"]:
		if clanWarManager.enabled():
			clanWarManager.end()