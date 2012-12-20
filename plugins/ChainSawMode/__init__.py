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
Messages = cxsbs.getResource("Messages")
ServerCore = cxsbs.getResource("ServerCore")
Players = cxsbs.getResource("Players")

pluginCategory = "ChainSawMode"

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='action', 
						displayName='action', 
						default="${info}Chainsaw only mode is now ${blue}${status}${white}.",
						doc="Message to print to show whether or not chainsaw only mode has just been enabled or disabled."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
	
@Commands.commandHandler('chainsawmode')
def onChainSawMode(cn, args):
	'''
	@description Toggle chainsaw only mode.
	@usage enable/disable
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Toggles chainsaw only mode.
	'''
	if args == 'enable':
		ServerCore.setChainSawOnly(True)
		messager.sendMessage('action', dictionary={'status': 'enabled'})
	elif args == 'disable':
		ServerCore.setChainSawOnly(False)
		messager.sendMessage('action', dictionary={'status': 'disabled'})
	else:
		raise Commands.UsageError()
