from cxsbs.Plugin import Plugin

class Commands(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		commandManager.command_handlers.clear()
		init()
		
	def unload(self):
		pass
		
import cxsbs
Logging = cxsbs.getResource("Logging")
ServerCore = cxsbs.getResource("ServerCore")
Events = cxsbs.getResource("Events")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Players = cxsbs.getResource("Players")
Help = cxsbs.getResource("Help")
CommandInformation = cxsbs.getResource("CommandInformation")
MessageFramework = cxsbs.getResource("MessageFramework")

import sys
import traceback
import threading

class UsageError(Exception):
	'''Invalid client usage of command'''
	def __init__(self, value=''):
		Exception.__init__(self, value)

class ExtraArgumentError(UsageError):
	'''Argument specified when none expected'''
	def __init__(self):
		UsageError.__init__(self, 'Extra argument specified')

class StateError(Exception):
	'''State of server is invalid for command'''
	def __init__(self, value):
		Exception.__init__(self, value)

class ArgumentValueError(Exception):
	'''Value of an argument is erroneous'''
	def __init__(self, value):
		Exception.__init__(self, value)
		
class InsufficientPermissions(Exception):
	'''...'''
	def __init__(self):
		Exception.__init__(self, "Insufficient Permissions")
		
def executeCommand(p, command, func, args):
	try:
		info = CommandInformation.getCommandInfo(command)
		if info == None:
			raise StateError("Commands without info cannot be executed.")
			
		if not CommandInformation.allowCommand(info, p):
			raise InsufficientPermissions()
		
		func(p.cn, args)
	except UsageError, e:
		try:
			usages = CommandInformation.getCommandInfo(command).usages
		except KeyError:
			usages = []
		messageModule.sendPlayerMessage('invalid_usage', p, dictionary={'command': command})
		for usage in usages:
			messageModule.sendPlayerMessage('command_usage', p, dictionary={'command': command, 'usage':usage})
	except StateError, e:
		messageModule.sendPlayerMessage('command_state_error', p, dictionary={'msg': str(e)})
	except ArgumentValueError, e:
		messageModule.sendPlayerMessage('command_argument_error', p, dictionary={'msg': str(e)})
	except ValueError:
		messageModule.sendPlayerMessage('command_value_error', p)
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.warn('Uncaught ValueError raised in command handler.')
		Logging.warn(traceback.format_exc())
	except InsufficientPermissions:
		UI.insufficientPermissions(p.cn)
		Logging.warn(p.name() + "@" + p.ipString() + ': Insufficient Permissions for command:' + command + " args: " + str(args))
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.warn(p.name() + "@" + p.ipString() + ': Uncaught exception occurred in command handler.')
		Logging.warn(traceback.format_exc())
					
def executeCallback(p, command, func, args):
	removeCallback = False
	try:
		returnValue = func(p.cn, command, args)
		if returnValue or returnValue == None:
			removeCallback = True
	except UsageError, e:
		try:
			usages = CommandInformation.getCommandInfo(command).usages
		except KeyError:
			usages = []
		messageModule.sendPlayerMessage('invalid_usage', p, dictionary={'command': command})
		for usage in usages:
			messageModule.sendPlayerMessage('command_usage', p, dictionary={'command': command, 'usage':usage})
	except StateError, e:
		messageModule.sendPlayerMessage('command_state_error', p, dictionary={'msg': str(e)})
	except ArgumentValueError, e:
		messageModule.sendPlayerMessage('command_argument_error', p, dictionary={'msg': str(e)})
	except ValueError:
		messageModule.sendPlayerMessage('command_value_error', p)
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.warn('Uncaught ValueError raised in command handler.')
		Logging.warn(traceback.format_exc())
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.warn(p.name() + "@" + p.ipString() + ': Uncaught exception occurred in command handler.')
		Logging.warn(traceback.format_exc())
	if removeCallback:
		commandManager.removeCallback(p.cn)
		

class CommandManager:
	def __init__(self):
		self.prefixes = '#'
		self.command_handlers = {}
		self.callbacks = {}
		Events.registerPolicyEventHandler('allow_message', self.onMsg)
	def register(self, command, func):
		if not self.command_handlers.has_key(command):
			self.command_handlers[command] = []
		self.command_handlers[command].append(func)
	def registerCallback(self, cn, func):
		self.callbacks[cn] = func
	
	def removeCallback(self, cn):
		try:
			del self.callbacks[cn]
		except:
			pass
	
	def triggerCallback(self, cn, command, text):
		if self.hasCallback(cn):
				p = Players.player(cn)
				func = self.callbacks[cn]
				executeCallback(p, command, func, text)
		
	def hasCallback(self, cn):
		return cn in self.callbacks.keys()
		
	def trigger(self, cn, command, text):
		p = Players.player(cn)
		
		if self.command_handlers.has_key(command):
			for func in self.command_handlers[command]:
					executeCommand(p, command, func, text)
		else:
			messageModule.sendPlayerMessage('unknown_command', p)
	def onMsg(self, cn, text):
		if len(text) > 0 and self.prefixes.find(text[0]) != -1:
			cmd = text[1:].split(' ')[0]
			args = text[len(cmd)+2:]
			if self.hasCallback(cn):
				self.triggerCallback(cn, cmd, args)
			else:
				self.trigger(cn, cmd, args)
			return False
		return True

def registerCommandHandler(command, func):
	CommandInformation.loadCommandInfo(command, func)
	commandManager.register(command, func)
	
def registerCallback(cn, func):
	commandManager.registerCallback(cn, func)

class CommandThreadQueuer:
	def __init__(self, f):
		self.func = f
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__

	def __call__(self, *args, **kwargs):
		cxsbs.AsyncronousExecutor.queue(self.func, *args, **kwargs)
		
class threadedCommandHandler(object):
	'''Decorator to register an event as an asyncronous command handler.'''
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerCommandHandler(self.name, CommandThreadQueuer(f))
		return f

class commandHandler(object):
	def __init__(self, name):
		self.command_name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerCommandHandler(self.command_name, f)
		return f
	
def init():
	global commandManager
	commandManager = CommandManager()
	
	registerCommandHandler('help', Help.onHelpCommand)
	registerCommandHandler('listcommands', Help.listCommands)
	
	global messageModule
	messageModule = MessageFramework.MessagingModule()
	messageModule.addMessage('unknown_command', '${error}Command not found.', "Help")
	messageModule.addMessage('command_usage', '${info}Usage: #${command} ${usage}', "Help")
	messageModule.addMessage('invalid_usage', '${error}Usage Error: #${command}:', "Commands")
	messageModule.addMessage('command_value_error', '${error}Value Error: Did you specify a valid cn?', "Commands")
	messageModule.addMessage('command_argument_error', '${error}Argument Error: ${msg}', "Commands")
	messageModule.addMessage('command_state_error', '${error}State Error: ${msg}', "Commands")
	messageModule.finalize()