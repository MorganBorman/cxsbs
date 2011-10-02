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

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="count_down", 
						displayName="Count down", 
						default="Clan war starts in ${green}${count}${white}.", 
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
						doc="Message to print  clanwar."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

messageModule = MessagingModule("clanwar")
messageModule.addMessage("count_down", "Clan war starts in ${green}${count}${white}.")
messageModule.addMessage("count_ended", "Fight!")
messageModule.addMessage("interclan_war_initiated", "A bitter feud has sprung up between ${blue}${clan1}${white} and ${red}${clan2}${white}. Event now, final battle preparations are underway, please wait while they are finished.")
messageModule.addMessage("intraclan_war_initiated", "Hard times foment discontent and unrest within ${blue}${clan}${white}. Soon a bitter conflict shall flare up, please wait while the final preparations are made.")
messageModule.addMessage("generic_war_initiated", "Hard times foment discontent. Please await the impending conflict.")
messageModule.addMessage("intermission", "An eerie calm has descended on this plain of destruction. Will the tired and wounded combatants resume their quarrel?")
messageModule.addMessage("interruption", "The balance of the force has been disrupted. Please check teams and use #resume.")
messageModule.addMessage("clanwar_ended", "A peace has returned to the land now that the clanwar has ended.")
messageModule.finalize()

def clanWarTimer(count):
	while count > 0:
		messageModule.sendMessage("count_down", dictionary={"count": count})
		time.sleep(1)
		count -= 1
	messageModule.sendMessage("count_ended")
	
class ClanWar:
	def __init__(self, clan1=None, clan2=None):
		self.combatants = []
	
		self.firstIntermission = True
		
		ServerCore.setPersistentIntermission(True)
		ServerCore.setMinsRemaining(0)
		
		time.sleep(1)
		
		if clan1 != None and clan2 != None:
			messageModule.sendMessage("interclan_war_initiated", dictionary={"clan1": clan1, "clan2": clan2})
		elif clan1 !=None:
			messageModule.sendMessage("intraclan_war_initiated", dictionary={"clan": clan1})
		else:
			messageModule.sendMessage("generic_war_initiated")
		
		self.restoreMasterMode = ServerCore.masterMode()
		self.restoreTeamMode = Teams.getTeamMode()
		
		Server.setMasterMode(2)
		Teams.setTeamMode('+r+l+s')
	
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
		pass
		
	def isCombatant(self, cn):
		pass
	
	def onMapChange(self, gameMap, gameMode):
		self.isIntermission = False
		self.saveCombatants()
		self.start()
			
	def onDisconnect(self, cn): #make on disconnect events sync_
		p = Players.player(cn)
		if not p.isSpectator() and not self.isIntermission:
			messageModule.sendMessage("interruption")
			Server.setPaused(True, -1)
			
	def onSpectate(self, cn):
		messageModule.sendMessage("interruption")
		Server.setPaused(True, -1)
		
	def onUnspectate(self, cn):
		self.saveCombatants()
		
	def onIntermission(self):
		self.isIntermission = True
		if not self.firstIntermission:
			messageModule.sendMessage("intermission")
		
	def start(self):
		ServerCore.setAllowShooting(False)
		
		Server.setPaused(True, -1)
		Server.setFrozen(True)
		
		clanWarTimer(10)
		
		Server.setFrozen(False)
		Server.setPaused(False)
		
		time.sleep(.75)
		ServerCore.setAllowShooting(True)
		
	def end(self):
		Server.setMasterMode(self.restoreMasterMode)
		Teams.setTeamMode(self.restoreTeamMode)
		ServerCore.setPersistentIntermission(False)
		messageModule.sendMessage("clanwar_ended")

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
	
clanWarManager = ClanWarManager()

Events.registerServerEventHandler('map_changed', clanWarManager.onMapChange)
Events.registerServerEventHandler('player_disconnect', clanWarManager.onDisconnect)
Events.registerServerEventHandler('player_spectated', clanWarManager.onSpectate)
Events.registerServerEventHandler('player_unspectated', clanWarManager.onUnspectate)
Events.registerServerEventHandler('intermission_begin', clanWarManager.onIntermission)

@Commands.commandHandler('clanwar')
def clanWar(cn, args):
	'''@description Enter clanwar mode
	   @usage <clantag1> (clantag2)'''
	if Server.isFrozen():
		raise Commands.StateError('Server is currently frozen')
	
	if clanWarManager.enabled():
		raise Commands.StateError('There is already a clanwar in progress. Use #endclanwar')
	
	clan1 = None
	clan2 = None
	if args == '':
		pass
	else:
		args = args.split(' ')
		if len(args) == 1:
			clan1 = args
		elif len(args) >= 2:
			clan1 = args[0]
			clan2 = args[1]
			
	clanWarManager.initiate(clan1, clan2)

@Commands.commandHandler('endclanwar')
def endClanWar(cn, args):
	'''@description Leave clanwar mode
	   @usage'''
	
	if not clanWarManager.enabled():
		raise Commands.StateError('There is no clanwar in progress.')
	
	clanWarManager.end()