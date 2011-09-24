from cxsbs.Plugin import Plugin

class EventInformation(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass
	
import cxsbs.Logging
import cxsbs
Config = cxsbs.getResource("Config")
		
class EventInfo:
	def __init__(self, event, handler):
		self.handler = handler
		self.name = self.handler.__name__ + '@' + self.handler.__module__
		self.event = event
		self.id = id(handler)
		self.isCommandType = False
		self.allowGroups = []
		self.denyGroups = []
		self.allowFunctionGroups = {}
		self.denyFunctionGroups = {}
		self.documentation = ''
		
	def configureGroups(self):
		config = Config.PluginConfig('Permissions')
		self.allowGroups = config.getOption(self.name, 'allow_groups', ' '.join(self.allowGroups)).split()
		self.denyGroups = config.getOption(self.name, 'deny_groups', ' '.join(self.denyGroups)).split()
		
		for function, groups in self.allowFunctionGroups.items():
			self.allowFunctionGroups[function] = config.getOption(self.command, function + '_allow_groups', ' '.join(groups)).split()
		
		for function, groups in self.denyFunctionGroups.items():
			self.denyFunctionGroups[function] = config.getOption(self.command, function + '_deny_groups', ' '.join(groups)).split()
		
		del config
		
	def finalize(self):
		self.configureGroups()
		if self.documentation == '':
			cxsbs.Logging.logger.warn("No documentation for event handler: " + self.handler.__name__ + '@' + self.handler.__module__)
		if self.allowGroups == []:
			cxsbs.Logging.logger.warn("No groups are allowed to invoke handler to event: " + self.handler.__name__ + '@' + self.handler.__module__)

def loadEventHandlerInfo(event, handler):
	docs = handler.__doc__
	if docs != None:
		info = EventInfo(event, handler)
		lines = docs.split('\n')
		doc = False
		
		for line in lines:
			line = line.strip()
			if len(line) > 0:
				if line[0] == '@':
					tag = line.split(' ', 1)[0].lower()
					text = line[len(tag)+1:]
					if tag == '@commandtype':
						info.isCommandType = True
					elif tag == '@allowgroups':
						info.allowGroups += text.split()
						doc = False
					elif tag == '@denygroups':
						info.denyGroups += text.split()
						doc = False
					elif tag == '@allowfunctiongroup':
						args = text.split()
						
						function = args[0]
						groups = args[1:]
						
						if not function in info.allowFunctionGroups.keys():
							info.allowFunctionGroups[function] = []
						
						info.allowFunctionGroups[function] += groups
					elif tag == '@denyfunctiongroup':
						args = text.split()
						
						function = args[0]
						groups = args[1:]
						
						if not function in info.denyFunctionGroups.keys():
							info.denyFunctionGroups[function] = []
						
						info.denyFunctionGroups[function] += groups
					elif tag == '@doc':
						doc = True
						info.documentation += text + '\n'
					elif doc:
						info.documentaation += text + '\n'
		
		info.finalize()
		
		eventhandler_info[id(handler)] = info
	else:
		#probably not a good idea to warn for this
		cxsbs.Logging.logger.warn('No info for eventhandler: ' + event)
		
def getEventHandlerInfo(handlerFunction):
	try:
		return eventhandler_info[id(handlerFunction)]
	except KeyError:
		return None
	
def allowEvent(eventInfo, p):
	playerGroups = p.groups()
	for group in playerGroups:
		if group in eventInfo.allowGroups and not group in eventInfo.denyGroups:
			return True
		
def init():
	global eventhandler_info
	eventhandler_info = {}