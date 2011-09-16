from cxsbs.Plugin import Plugin

class Help(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass
		
import cxsbs
Config = cxsbs.getResource("Config")
Logging = cxsbs.getResource("Logging")
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Players = cxsbs.getResource("Players")

class CommandInfo:
	def __init__(self, command):
		self.command = command
		self.usages = []
		self.allowGroups = []
		self.denyGroups = []
		self.documentation = ''
	def addUsage(self, str):
		str = '#' + self.command + ' ' + str
		self.usages.append(str)
		
	def configureGroups(self):
		config = Config.PluginConfig('Commands')
		self.allowGroups = config.getOption('Permissions', 'deny_groups', ' '.join(self.allowGroups)).split()
		self.denyGroups = config.getOption('Permissions', 'allow_groups', ' '.join(self.denyGroups)).split()
		del config
		
	def finalize(self):
		self.configureGroups()
		if self.documentation == '':
			Logging.warn("No documentation for command: " + self.command)
		if self.allowGroups == []:
			Logging.warn("No groups are allowed to issue command: " + self.command)

def loadCommandInfo(command, handler):
	docs = handler.__doc__
	if docs != None:
		info = CommandInfo(command)
		lines = docs.split('\n')
		doc = False
		
		for line in lines:
			line = line.strip()
			if line[0] == '@':
				tag = line.split(' ', 1)[0]
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
				elif tag == '@allowGroups':
					info.allowGroups += text.split()
					doc = False
				elif tag == '@denyGroups':
					info.denyGroups += text.split()
					doc = False
				elif tag == '@doc':
					doc = True
					info.documentation += text + '\n'
				elif doc:
					info.documentaation += text + '\n'
					
		info.finalize()
					
		command_info[command] = info
	else:
		Logging.warn('No help info for command: ' + command)

def msgHelpText(cn, cmd):
	try:
		helpinfo = command_info[cmd]
	except KeyError:
		ServerCore.playerMessage(cn, UI.error('Command not found'))
	else:
		msgs = []
		try:
			msgs.append(helpinfo.description)
		except AttributeError:
			pass
		for usage in helpinfo.usages:
			msgs.append(usage)
		for msg in msgs:
			ServerCore.playerMessage(cn, UI.info(msg))

def onHelpCommand(cn, args):
	'''@description Display help information about a command
	   @usage (command)
	   @public'''
	if args == '':
		msgHelpText(cn, 'help')
	else:
		args = args.split(' ')
		msgHelpText(cn, args[0])

def onPlayerCommands(cn, args):
	if args != '':
		ServerCore.playerMessage(cn, UI.error('Usage: #playercommands'))
	else:
		msg = Colors.blue('Available commands: ')
		for command in command_info.keys():
			msg += '#' + command + ' '
		ServerCore.playerMessage(cn, Colors.orange(msg))

def listCommands(cn, args):
	'''@description Display all commands available to a user
	   @usage
	   @public'''
	if Players.isAdmin(cn):
		listAdminCommands(cn, args)
	elif Players.isMaster(cn):
		listMasterCommands(cn, args)
	else:
		listPublicCommands(cn, args)
		
def listPublicCommands(cn, args):
	str = 'Public commands: '
	for cmd in command_info.items():
		if cmd[1].public:
			str += cmd[1].command + ' '
	ServerCore.playerMessage(cn, UI.info(str))
	
def listMasterCommands(cn, args):
	str = 'Master commands: '
	for cmd in command_info.items():
		if cmd[1].public:
			str += cmd[1].command + ' '
		elif cmd[1].master:
			str += cmd[1].command + ' '
	ServerCore.playerMessage(cn, UI.info(str))
	
def listAdminCommands(cn, args):
	str = 'Admin commands: '
	for cmd in command_info.items():
		str += cmd[1].command + ' '
	ServerCore.playerMessage(cn, UI.info(str))
	
def init():
	global command_info
	command_info = {}