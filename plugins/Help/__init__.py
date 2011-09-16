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
Logging = cxsbs.getResource("Logging")
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Players = cxsbs.getResource("Players")

class CommandInfo:
	def __init__(self, command):
		self.command = command
		self.usages = []
		self.public = False
	def addUsage(self, str):
		str = '#' + self.command + ' ' + str
		self.usages.append(str)

def loadCommandInfo(command, handler):
	docs = handler.__doc__
	if docs != None:
		info = CommandInfo(command)
		lines = docs.split('\n')
		valid = False
		info.public = False
		info.master = False
		info.admin = False
		for line in lines:
			line = line.strip()
			if line[0] == '@':
				tag = line.split(' ', 1)[0]
				if tag == '@usage':
					if len(line) == len(tag):
						info.addUsage('')
					else:
						info.addUsage(line[len(tag)+1:])
					valid = True
				elif tag == '@description':
					info.description = line[len(tag)+1:]
					valid  = True
				elif tag == '@public':
					info.public = True
					valid = True
				elif tag == '@master':
					info.master = True
					valid = True
				elif tag == '@admin':
					info.admin = True
					valid = True
		if valid:
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