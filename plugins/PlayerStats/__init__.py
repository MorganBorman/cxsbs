import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
Messages = cxsbs.getResource("Messages")
Commands = cxsbs.getResource("Commands")
Players = cxsbs.getResource("Players")

pluginCategory = "PlayerStats"

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="stats", 
						displayName="Stats", 
						default="${white}Stats for ${orange}${name}${white}: Frags=${green}${frags}${white}, Deaths=${red}${deaths}${white}, Teamkills=${magenta}${teamkills}${white}, Accuracy=${yellow}${accuracy}%${white}, KpD=${orange}${ktd}${white}, Scores=${blue}${score}${white}.", 
						doc="Stats template."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

from operator import itemgetter

def showStats(cn, tcn):
	"get the stats of the player indicated by tcn and send them to the player indicated by cn"
	cp = Players.player(cn)
	p = Players.player(tcn)
	
	try:
		statsDict = 	{
							'name':p.name(), 
							'frags':p.frags(), 
							'deaths':p.deaths(), 
							'teamkills':p.teamkills(), 
							'shots':p.shots(), 
							'hits':p.hits(), 
							'accuracy':p.accuracy(), 
							'ktd':p.kpd(), 
							'score':p.score(),
						}
		messager.sendPlayerMessage('stats', cp, dictionary=statsDict)
	except ValueError:
		pass
	
validSortArgs = ['name', 'frags', 'deaths', 'teamkills', 'shots', 'hits', 'accuracy', 'ktd', 'score']
	
def showStatsAll(cn, sortArg):
	cp = Players.player(cn)
	players = Players.all()
	
	statsList = []
	
	reversed = False
	if sortArg[0] == '-':
		reversed = True
		sortArg = sortArg[1:]
	
	if not sortArg in validSortArgs:
		raise Commands.UsageError()
	
	for p in players:
		try:
			statsDict = 	{
								'name':p.name(), 
								'frags':p.frags(), 
								'deaths':p.deaths(), 
								'teamkills':p.teamkills(), 
								'shots':p.shots(), 
								'hits':p.hits(), 
								'accuracy':p.accuracy(), 
								'ktd':p.kpd(), 
								'score':p.score(),
							}
			statsList.append(statsDict)
		except ValueError:
			pass
		
	statsList = sorted(statsList, key=itemgetter(sortArg))
		
	if reversed:
		statsList.reverse()
		
	for statsDict in statsList:
		messager.sendPlayerMessage('stats', cp, dictionary=statsDict)

@Commands.commandHandler('stats')
def onStatsCommand(cn, args):
	'''
	@description Get a players stats for the current match
	@usage (<cn>|all (sort by:name|frags|deaths|teamkills|shots|hits|accuracy|ktd|score))
	@allowGroups __all__
	@denyGroups
	@doc Get player(s) stats for the current match.
	'''
	args = args.split()
	
	if len(args) < 1:
		showStats(cn, cn)
	elif args[0].lower() == "all":
		if len(args) > 1:
			showStatsAll(cn, args[1])
		else:
			showStatsAll(cn, "frags")
	else:
		tcn = int(args[0])
		
		showStats(cn, tcn)
