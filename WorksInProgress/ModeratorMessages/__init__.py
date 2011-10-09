import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
		
@Commands.commandHandler('addtemplate')
def onAddTemplate(cn, args):
	'''
	@description Add a message template to the stored ones.
	@usage 5m
	@allowGroups __admin__
	@denyGroups
	@doc Add a message template to the stored ones.
	'''
	pass

@Commands.commandHandler('deltemplate')
def onDelTemplate(cn, args):
	'''
	@description Add a message template to the stored ones.
	@usage 5m
	@allowGroups __admin__
	@denyGroups
	@doc Delete a message template from the stored ones.
	'''
	pass
		
@Commands.commandHandler('templatemessage')
def onTemplateMessageCommand(cn, args):
	'''
	@description Send a template message to a specified player.
	@usage <cn> <message name>
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Add a message template to the stored ones.
	'''
	pass

@Commands.commandHandler('templatebroadcast')
def onTemplateBroadcastCommand(cn, args):
	'''
	@description Add a message template to the stored ones.
	@usage 5m
	@allowGroups __admin__
	@denyGroups
	@doc Add a message template to the stored ones.
	'''
	pass