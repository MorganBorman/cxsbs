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
CommandInformation = cxsbs.getResource("CommandInformation")
MessageFramework = cxsbs.getResource("MessageFramework")

import cxsbs.Logging

def msgHelpText(cn, cmd):
	p = Players.player(cn)
	try:
		helpinfo = CommandInformation.getCommandInfo(cmd)
	except KeyError:
		messageModule.sendPlayerMessage('unknown_command', p)
	else:
		msgs = []
		try:
			msgs.append(helpinfo.description)
		except AttributeError:
			pass
		for usage in helpinfo.usages:
			msgs.append(usage)
		for msg in msgs:
			messageModule.sendPlayerMessage('help_message', p, dictionary={'msg':msg})

def onHelpCommand(cn, args):
	'''@description Display help information about a command
	   @usage (command)
	   @allowGroups __all__'''
	if args == '':
		msgHelpText(cn, 'help')
	else:
		args = args.split(' ')
		msgHelpText(cn, args[0])

def listCommands(cn, args):
	'''@description Display all commands available to a user
	   @usage <cn>
	   @allowGroups __all__
	   @allowFunctionGroup listothers'''
	q = Players.player(cn)
	
	args = args.split()
	if len(args) == 0:
		p = q
	elif len(args) == 1:
		p = Players.player(int(args[0]))
	else:
		raise Commands.UsageError()
	
	playerGroups = p.groups()
	
	available = []
	
	for cmd in CommandInformation.command_info.values():
		if CommandInformation.allowCommand(cmd, p):
			available.append(cmd.command)
	messageModule.sendPlayerMessage('available_commands', q, dictionary={'commands':', '.join(available)})
	
def init():

	global messageModule
	messageModule = MessageFramework.MessagingModule()
	messageModule.addMessage('available_commands', '${help}${yellow}Available commands:${white} ${commands}.', "Help")
	messageModule.addMessage('unkown_command', '${error}Command not found.', "Help")
	messageModule.addMessage('help_message', '${help}${msg}', "Help")
	messageModule.finalize()