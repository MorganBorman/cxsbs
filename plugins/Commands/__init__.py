from cxsbs.Plugin import Plugin

class Commands(Plugin):
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
Events = cxsbs.getResource("Events")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Players = cxsbs.getResource("Players")
Help = cxsbs.getResource("Help")
CommandInformation = cxsbs.getResource("CommandInformation")

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
		info = Help.getCommandInfo(command)
		if info == None:
			raise StateError("Commands without info cannot be executed.")
			
		if not Help.allowCommand(info, p):
			raise InsufficientPermissions()
		
		func(p.cn, args)
	except UsageError, e:
		try:
			usages = Help.command_info[command].usages
		except KeyError:
			usages = []
		p.message(UI.error('Invalid Usage of #' + command + ' command. ' + str(e)))
		for usage in usages:
			p.message(UI.info('Usage: ' + command + ' ' + usage))
	except StateError, e:
		p.message(UI.error(str(e)))
	except ArgumentValueError, e:
		p.message(UI.error('Invalid argument. ' + str(e)))
	except ValueError:
		p.message(UI.error('Value Error: Did you specify a valid cn?'))
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.warn('Uncaught ValueError raised in command handler.')
		Logging.warn(traceback.format_exc())
	except InsufficientPermissions:
		UI.insufficientPermissions(p.cn)
		Logging.warn('Insufficient Permissions for command:' + command + " args: " + str(args) + " player: " + p.name() + "@" + p.ipString())
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.warn('Uncaught exception occured in command handler.')
		Logging.warn(traceback.format_exc())
					
def executeCallback(p, command, func, args):
	removeCallback = False
	try:
		returnValue = func(p.cn, command, args)
		if returnValue or returnValue == None:
			removeCallback = True
	except UsageError, e:
		try:
			usages = Help.command_info[command].usages
		except KeyError:
			usages = []
		p.message(UI.error('Invalid Usage of #' + command + ' command. ' + str(e)))
		for usage in usages:
			p.message(UI.info('Usage: ' + self.command + ' ' + usage))
	except StateError, e:
		p.message(UI.error(str(e)))
	except ArgumentValueError, e:
		p.message(UI.error('Invalid argument. ' + str(e)))
	except ValueError:
		p.message(UI.error('Value Error: Did you specify a valid cn?'))
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.warn('Uncaught ValueError raised in command handler.')
		Logging.warn(traceback.format_exc())
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.warn('Uncaught exception occurred in command handler.')
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
			p.message(UI.error('Command not found'))
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