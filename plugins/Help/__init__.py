import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
		
import cxsbs
Messages = cxsbs.getResource("Messages")
Logging = cxsbs.getResource("Logging")
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Players = cxsbs.getResource("Players")
CommandInformation = cxsbs.getResource("CommandInformation")

import cxsbs.Logging

Messages.addMessage	(
						subcategory="Help", 
						symbolicName="available_commands", 
						displayName="Available commands", 
						default="${help}${yellow}Available commands:${white} ${commands}.",
						doc="Prefix for #listcommands command.",
					)

Messages.addMessage	(
						subcategory="Help", 
						symbolicName="unkown_command", 
						displayName="Unknown command", 
						default="${error}Command not found.",
						doc="Command not found error message.",
					)

Messages.addMessage	(
						subcategory="Help", 
						symbolicName="help_message", 
						displayName="Help message", 
						default="${help}${msg}",
						doc="Generic help message form.",
					)

messager = Messages.getAccessor(subcategory="Help")

def msgHelpText(cn, cmd):
	p = Players.player(cn)
	try:
		helpinfo = CommandInformation.getCommandInfo(cmd)
	except KeyError:
		messager.sendPlayerMessage('unknown_command', p)
	else:
		msgs = []
		try:
			msgs.append(helpinfo.description)
		except AttributeError:
			pass
		for usage in helpinfo.usages:
			msgs.append(usage)
		for msg in msgs:
			messager.sendPlayerMessage('help_message', p, dictionary={'msg':msg})

def onHelpCommand(cn, args):
	if args == '':
		msgHelpText(cn, 'help')
	else:
		args = args.split(' ')
		msgHelpText(cn, args[0])

def listCommands(cn, args):
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
	messager.sendPlayerMessage('available_commands', q, dictionary={'commands':', '.join(available)})