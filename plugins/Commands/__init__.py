import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global commandManager
		commandManager = CommandManager()
		
		registerCommandHandler('help', onHelpCommand)
		registerCommandHandler('listcommands', onListcommands)
		
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
Messages = cxsbs.getResource("Messages")
	
pluginCategory = 'Commands'
	
Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="command_usage", 
						displayName="Command usage", 
						default="${info}Usage: #${command} ${usage}", 
						doc="Command usage message template."
					)
	
Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="invalid_usage", 
						displayName="Invalid usage", 
						default="${error}Usage Error: #${command}:", 
						doc="Invalid command usage error message tempate."
					)
	
Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="command_value_error", 
						displayName="Command value error", 
						default="${error}Value Error: Did you specify a valid cn?", 
						doc="Command value error message template"
					)
	
Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="command_argument_error", 
						displayName="Command argument error", 
						default="${error}Argument Error: ${msg}", 
						doc="Command argument error message tempate."
					)
	
Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="command_state_error", 
						displayName="Command state error", 
						default="${error}State Error: ${msg}", 
						doc="Command state error message tempate"
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
helpMessager = Messages.getAccessor(subcategory='Help')

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
		messager.sendPlayerMessage('invalid_usage', p, dictionary={'command': command})
		for usage in usages:
			messager.sendPlayerMessage('command_usage', p, dictionary={'command': command, 'usage':usage})
	except StateError, e:
		messager.sendPlayerMessage('command_state_error', p, dictionary={'msg': str(e)})
	except ArgumentValueError, e:
		messager.sendPlayerMessage('command_argument_error', p, dictionary={'msg': str(e)})
	except ValueError:
		messager.sendPlayerMessage('command_value_error', p)
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
		messager.sendPlayerMessage('invalid_usage', p, dictionary={'command': command})
		for usage in usages:
			messager.sendPlayerMessage('command_usage', p, dictionary={'command': command, 'usage':usage})
	except StateError, e:
		messager.sendPlayerMessage('command_state_error', p, dictionary={'msg': str(e)})
	except ArgumentValueError, e:
		messager.sendPlayerMessage('command_argument_error', p, dictionary={'msg': str(e)})
	except ValueError:
		messager.sendPlayerMessage('command_value_error', p)
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
			helpMessager.sendPlayerMessage('unknown_command', p)
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
		cxsbs.AsyncronousExecutor.dispatch(self.func, args=args, time=0, kwargs=kwargs)
		
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
	
def onHelpCommand(cn, args):
	'''@description Display help information about a command
	   @usage (command)
	   @allowGroups __all__
	   @doc Command to retrieve the description string and usage strings and display them to the user in-game.'''
	Help.onHelpCommand(cn, args)
	
def onListcommands(cn, args):
	'''@description Display all commands available to a user
	   @usage <cn>
	   @allowGroups __all__
	   @allowFunctionGroup listothers __admin__
	   @denyFunctionGroup listothers
	   @doc Command to retrieve those commands which are available to the specified client.
	   If no client is specified then the default is to print those commands which are available to the client issuing the command.
	   The setting listothers_allow_groups and listothers_deny_groups settings constrain who is permitted to list other clients available permissions.'''
	Help.listCommands(cn, args)
	