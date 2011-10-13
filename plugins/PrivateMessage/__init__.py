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
Players = cxsbs.getResource("Players")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")

pluginCategory = "PrivateMessage"

SettingsManager.addSetting(Setting.TemplateSetting	(
												category="Messages", 
												subcategory=pluginCategory, 
												symbolicName="pm_prefix", 
												displayName="Pm prefix", 
												default="[pm]: ${message}", 
												doc="Prefix for a private message."
											))

settings = SettingsManager.getAccessor(category="Messages", subcategory=pluginCategory)
	
@Commands.commandHandler('pm')
def onPmCommand(cn, args):
	'''
	@description Send a private message
	@usage <cn> <message>
	@allowGroups __all__
	@denyGroups
	@doc Send a private message.
	'''
	args = args.split(' ', 1) #split the arguments into two parts (cn, message)
	if len(args) < 2:
		raise Commands.UsageError()
	try:
		tcn = int(args[0])
	except ValueError:
		raise Commands.UsageError()
	
	Players.player(cn).say(tcn, settings['pm_prefix'].substitute(message=args[1]))