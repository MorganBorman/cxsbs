import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
Players = cxsbs.getResource("Players")
Events = cxsbs.getResource("Events")
Messages = cxsbs.getResource("Messages")

import groups

from groups import Group
from groups.Query import Is, Not, Select, Intersection

pluginCategory = 'Teamkill'

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="teamkill_broadcast", 
						displayName="Teamkill broadcast", 
						default="${info}${red}${teamkiller}${white} has teamkilled ${green}${victim}${white}.", 
						doc="Message to show when a player teamkills another."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

@Events.eventHandler('player_teamkill')
def onTeamkill(cn, tcn):
	if cn == tcn:
		return
	p = Players.player(cn)
	t = Players.player(tcn)
	p.logAction('Teamkilled: ' + t.name() + '@' + t.ipLong())
	messageGroup = Players.AllPlayersGroup.query(Intersection(Select(cn=Not(Is(cn))), Select(cn=Not(Is(tcn))))).all()
	messager.sendMessage('teamkill_broadcast', messageGroup, dictionary={'teamkiller':p.name(), 'victim':t.name()})