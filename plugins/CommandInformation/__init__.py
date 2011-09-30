import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global command_info
		command_info = {}
		
	def unload(self):
		pass
		
import cxsbs.Logging
import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")

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
		pluginCategory = 'Permissions'
		
		SettingsManager.addSetting(Setting.ListSetting	(
															category=pluginCategory, 
															subcategory=self.command, 
															symbolicName="allow_groups",
															displayName="Allow Groups", 
															default=self.allowGroups,
															doc="Allowed groups for command type event: " + self.command
														))
		
		SettingsManager.addSetting(Setting.ListSetting	(
															category=pluginCategory, 
															subcategory=self.command, 
															symbolicName="deny_groups",
															displayName="Deny Groups", 
															default=self.denyGroups,
															doc="Denied groups for command type event: " + self.command
														))
		
		for function, groups in self.allowFunctionGroups.items():
			SettingsManager.addSetting(Setting.ListSetting	(
																category=pluginCategory, 
																subcategory=self.command, 
																symbolicName=function + '_allow_groups',
																displayName="Allow Groups for " + function, 
																default=groups,
																doc="Allowed groups for command type event: " + self.command + " function:" + function
															))
		
		for function, groups in self.denyFunctionGroups.items():
			SettingsManager.addSetting(Setting.ListSetting	(
																category=pluginCategory, 
																subcategory=self.command, 
																symbolicName=function + '_deny_groups',
																displayName="Deny Groups for " + function, 
																default=groups,
																doc="Denied groups for command type event: " + self.command + " function:" + function
															))
		
		self.settings = SettingsManager.getAccessor(category=pluginCategory, subcategory=self.command)
		
	def getAllowedGroups(self):
		return self.settings["allow_groups"]
		
	def getDeniedGroups(self):
		return self.settings["deny_groups"]
	
	def getAllowFunctionGroups(self, functionName):
		return self.settings[functionName + "_allow_groups"]
		
	def getDeniedFunctionGroups(self, functionName):
		return self.settings[functionName + "_deny_groups"]
		
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
				if doc:
					info.documentation += line + '\n'
				elif line[0] == '@':
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
						
						if len(args) > 0:
							function = args[0]
							groups = args[1:]
							
							if not function in info.allowFunctionGroups.keys():
								info.allowFunctionGroups[function] = []
							
							info.allowFunctionGroups[function] += groups
						else:
							cxsbs.Logging.logger.warn("allowfunctiongroup without specified function in command declaration: " + info.command)
					elif tag == '@denyfunctiongroup':
						args = text.split()
						
						if len(args) > 0:
							function = args[0]
							groups = args[1:]
							
							if not function in info.denyFunctionGroups.keys():
								info.denyFunctionGroups[function] = []
							
							info.denyFunctionGroups[function] += groups
						else:
							cxsbs.Logging.logger.warn("denyfunctiongroup without specified function in command declaration: " + info.command)
					elif tag == '@doc':
						doc = True
						info.documentation += text + '\n'

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