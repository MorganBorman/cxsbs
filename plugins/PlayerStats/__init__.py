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

@Commands.commandHandler('stats')
def onCommand(cn, args):
	'''
	@description Get a players stats for the current match
	@usage <cn>
	@allowGroups __all__
	@denyGroups
	@doc Get a players stats for the current match.
	'''
	cp = Players.player(cn)
	if args != '':
		tcn = int(args)
		p = Players.player(tcn)
	else:
		p = cp

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

@Commands.commandHandler('statsall')
def showStatsAll(cn, args):
	'''
	@description Get all player stats for the current match
	@usage
	@allowGroups __all__
	@denyGroups
	@doc Get all player stats for the current match.
	'''
	cp = Players.player(cn)
	players = Players.all()
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
			messager.sendPlayerMessage('stats', cp, dictionary=statsDict)
		except ValueError:
			continue
