from cxsbs.Plugin import Plugin

class CommandInformation(Plugin):
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

class CommandInfo:
	def __init__(self, command):
		self.command = command
		self.usages = []
		self.allowGroups = []
		self.denyGroups = []
		self.allowFunctionGroups = {}
		self.denyFunctionGroups = {}
		self.documentation = ''
	def addUsage(self, str):
		str = '#' + self.command + ' ' + str
		self.usages.append(str)
		
	def configureGroups(self):
		config = Config.PluginConfig('Permissions')
		self.allowGroups = config.getOption(self.command, 'allow_groups', ' '.join(self.allowGroups)).split()
		self.denyGroups = config.getOption(self.command, 'deny_groups', ' '.join(self.denyGroups)).split()
		
		for function, groups in self.allowFunctionGroups.items():
			self.allowFunctionGroups[function] = config.getOption(self.command, function + '_allow_groups', ' '.join(groups)).split()
		
		for function, groups in self.denyFunctionGroups.items():
			self.denyFunctionGroups[function] = config.getOption(self.command, function + '_deny_groups', ' '.join(groups)).split()
		
		del config
		
	def finalize(self):
		self.configureGroups()
		if self.documentation == '':
			cxsbs.Logging.logger.warn("No documentation for command: " + self.command)
		if self.allowGroups == []:
			cxsbs.Logging.logger.warn("No groups are allowed to issue command: " + self.command)

def loadCommandInfo(command, handler):
	docs = handler.__doc__
	if docs != None:
		info = CommandInfo(command)
		lines = docs.split('\n')
		doc = False
		
		for line in lines:
			line = line.strip()
			if len(line) > 0 or doc:
				if line[0] == '@':
					tag = line.split(' ', 1)[0].lower()
					text = line[len(tag)+1:]
					if tag == '@usage':
						if len(line) == len(tag):
							info.addUsage('')
						else:
							info.addUsage(text)
						doc = False
					elif tag == '@description':
						info.description = text
						doc = False
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
		
		command_info[command] = info
	else:
		cxsbs.Logging.logger.warn('No help info for command: ' + command)
		
def getCommandInfo(command):
	try:
		return command_info[command]
	except KeyError:
		return None
	
def allowCommand(cmd, p):
	playerGroups = p.groups()
	for group in playerGroups:
		if group in cmd.allowGroups and not group in cmd.denyGroups:
			return True
		
def init():
	global command_info
	command_info = {}