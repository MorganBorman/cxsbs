from cxsbs.Plugin import Plugin

class Reload(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		deinit()
		
import cxsbs
Commands = cxsbs.getResource("Commands")
		
def init():
	@Commands.commandHandler('reload')
	def onReload(cn, args):
		'''
		@description Reload the server configuration
		@allowGroups __admin__
		@denyGroups
		'''
		cxsbs.reload()

def deinit():
	pass