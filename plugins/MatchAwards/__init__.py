import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
from groups.Query import MaxMins

import cxsbs
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Messages = cxsbs.getResource("Messages")

pluginCategory = "MatchAwards"

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='awards_main', 
						displayName='Awards main', 
						default="${blue}Awards: ${white}${most_frags} ${most_teamkills} ${most_deaths} ${most_kpd} ${most_accuracy}",
						doc="Main awards template."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='most_frags', 
						displayName='Most frags', 
						default="Most Frags: ${orange}${names} ${blue}(${green}${count}${blue})${white} ",
						doc="Frags awards template."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='most_teamkills', 
						displayName='Most teamkills', 
						default="Most TeamKills: ${orange}${names} ${blue}(${green}${count}${blue})${white} ",
						doc="Teamkills awards template."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='most_deaths', 
						displayName='Most deaths', 
						default="Most Deaths: ${orange}${names} ${blue}(${green}${count}${blue})${white} ",
						doc="Deaths awards template."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='most_kpd', 
						displayName='Most kpd', 
						default="Greatest kpd: ${orange}${names} ${blue}(${green}${count}${blue})${white} ",
						doc="kpd awards template."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='most_accuracy', 
						displayName='Most accuracy', 
						default="Highest accuracy: ${orange}${names} ${blue}(${green}${count}${blue})${white} ",
						doc="Deaths awards template."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

def getNamesString(group):
	names = group.action('name', ())
	if len(names) < 1:
		return ""
	elif len(names) == 1:
		return names[0]
	else:
		return ', '.join(names[:-1]) + ', and ' + names[-1]
	
def getValue(group, feild):
	values = group.action(feild, ())
	if len(values) > 0:
		return values[0]
	else:
		return None

@Events.eventHandler('intermission_begin')
def onIntermission():
	
	stats = ['frags', 'deaths', 'teamkills', 'kpd', 'accuracy']
	
	bestStatGroups = {}
	submessages = {}
	dictionary = {}
	
	for stat in stats:
		bestStatGroups[stat] = Players.AllPlayersGroup.query(MaxMins(**{stat:'>'})).all()
		
		if getValue(bestStatGroups[stat], stat) != None and getValue(bestStatGroups[stat], stat) > 0:
			submessages['most_' + stat] = {'names': getNamesString(bestStatGroups[stat]), 'count': getValue(bestStatGroups[stat], stat)}
		else:
			dictionary['most_' + stat] = ""
	
	messager.sendMessage('awards_main', dictionary=dictionary, submessages=submessages)