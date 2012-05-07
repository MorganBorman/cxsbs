import pyTensible, org

class commands(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		self.command_manager = CommandManager()
		
		self.command_manager.register("listcommands", on_listcommands, False)
		self.command_manager.register("help", on_help, False)
		
		event_manager = org.cxsbs.core.events.manager.event_manager
		event_manager.register_handler('command', self.command_manager.on_command)
		
		Interfaces = {}
		Resources = 	{
							'command_manager': self.command_manager, 
							'handler': get_command_decorator(self.command_manager),
							'UsageError': UsageError,
							'StateError': StateError,
							'ArgumentValueError': ArgumentValueError,
							'InsufficientPermissions': InsufficientPermissions
						}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
@org.cxsbs.core.messages.Message
def permission_denied_message():
    """
    @fields 
    @doc The message printed when the client lacks sufficient permissions to run the specified command.
    """
    return "${denied}Insufficient permissions."
   
@org.cxsbs.core.messages.Message
def usage_error_message():
    """
    @fields 
    @doc The message printed when a command is improperly used.
    """
    return "${error}Invalid usage"
   
@org.cxsbs.core.messages.Message
def usage_message():
    """
    @fields usage
    @doc The message printed to describe how a command should be used.
    """
    return "${help}Usage: ${usage}"
   
@org.cxsbs.core.messages.Message
def help_generic_message():
    """
    @fields
    @doc The message printed when the help command is used without specifying a command.
    """
    return "${help}Welcome to the CXSBS help system. Use #listcommands to see the available commands."
   
@org.cxsbs.core.messages.Message
def help_description_message():
    """
    @fields command description
    @doc The message printed to show the command name and usage.
    """
    return "${help}${command}: ${description}"
   
@org.cxsbs.core.messages.Message
def listcommands_message():
    """
    @fields commands
    @doc The message printed show the list of commands available to the user.
    """
    return "${help}Available commands: ${commands}"
   
@org.cxsbs.core.messages.Message
def state_error_message():
    """
    @fields description
    @doc The message printed when a command is used when the server is the wrong state.
    """
    return "${error}State error: ${description}"
   
@org.cxsbs.core.messages.Message
def argument_value_error_message():
    """
    @fields description
    @doc The message printed when a command is used with an erroneous arugment value.
    """
    return "${error}Argument error: ${description}"
   
@org.cxsbs.core.messages.Message
def unknown_command_message():
    """
    @fields 
    @doc The message printed when the specified command doesn't exist.
    """
    return "${error}Unknown command."
   
class UsageError(Exception):
	'''Invalid client usage of command'''
	def __init__(self, value=''):
		Exception.__init__(self, value)

class StateError(Exception):
	'''State of server is invalid for command'''
	def __init__(self, value):
		Exception.__init__(self, value)

class ArgumentValueError(Exception):
	'''Value of an argument is erroneous'''
	def __init__(self, value):
		Exception.__init__(self, value)
		
class InsufficientPermissions(Exception):
	'''Client lacks required permissions for action'''
	def __init__(self):
		Exception.__init__(self, "Insufficient Permissions")

class Command(object):
	def __init__(self, command_name, handler):
		
		self.command_name = command_name
		self.handler = handler
		self.qualified_command_name = handler.__module__ + '.' + command_name
		self.usage = ""
		self.description = ""
		self.documentation = []
		permissions = {'execute': ([],[])} 
		
		docs = handler.__doc__
		if docs != None:
			lines = docs.split('\n')
			doc = False
			
			for line in lines:
				line = line.strip().rstrip()
				if len(line) > 0:
					if line[0] == '@':
						tag, text = line.split(None, 1)
						tag = tag.lower()
						if tag == '@usage':
							self.usage = text
							doc = False
							
						elif tag == '@description':
							self.description = text
							doc = False
							
						elif tag == '@doc':
							doc = True
							self.documentation.append(text)
							
					elif line[0] == '$':
						split_functionality_line = line.split()
						if len(split_functionality_line) > 1:
							functionality = split_functionality_line[0]
							groups = split_functionality_line[1:]
						else:
							functionality = split_functionality_line[0]
							groups = []
						functionality = functionality.lower()[1:]
						
						if not functionality in permissions.keys():
							permissions[functionality] = ([],[])
						
						for group in groups:
							if group[0] == '-':
								permissions[functionality][1].append(group[1:])
							elif group[0] == '+':
								permissions[functionality][0].append(group[1:])
							else:
								permissions[functionality][0].append(group)
								
					elif doc:
						self.documentation.append(line)
						
				elif doc:
					self.documentation.append(line)
			
		else:
			org.cxsbs.core.logger.warn('No help info for command: ' + self.command_name)
			
		self.documentation = "\n".join(self.documentation)
			
		has_printed_command_doc = False
		command_doc = []
		command_doc.append("#"*79)
		command_doc.append("%s: %s" % (self.qualified_command_name, self.description))
		command_doc.append("usage: %s" % self.usage)
		command_doc.append("")
		command_doc.append(self.documentation)
		command_doc.append("-"*39)
		command_doc = "\n".join(command_doc)
			
		for functionality, (allowed_groups, denied_groups) in permissions.items():
			
			qualified_functionality = "%s_%s" %(self.qualified_command_name, functionality)
			
			if not has_printed_command_doc:
				setting_doc = command_doc
				has_printed_command_doc = True
			else:
				setting_doc = ""
			
			org.cxsbs.core.settings.manager.Setting.static_initialization	(
																				setting_symbolic_name = "%s_allowed" % qualified_functionality, 
																				setting_category = "commands", 
																				setting_default_wbpolicy = "never", 
																				setting_doc = setting_doc, 
																				setting_default_value = allowed_groups
																			)
			
			setting_doc = ""
			
			org.cxsbs.core.settings.manager.Setting.static_initialization	(
																				setting_symbolic_name = "%s_denied" % qualified_functionality, 
																				setting_category = "commands", 
																				setting_default_wbpolicy = "never", 
																				setting_doc = setting_doc, 
																				setting_default_value = denied_groups
																			)
			
	def execute(self, client, command_line):
		try:
			if not client.isActionPermitted(self.qualified_command_name + "_execute"):
				raise InsufficientPermissions()
			
			args = command_line.split()
			self.handler(client, *args)
		except (TypeError, UsageError), e:
			usage_error_message.server(client)
			usage_message.server(client, {'usage': self.usage})
		except StateError, e:
			state_error_message.server(client, {'description': str(e)})
		except StateError, e:
			argument_value_error_message.server(client, {'description': str(e)})
		except InsufficientPermissions:
			permission_denied_message.server(client)
			context_description = "%s@%s: Insufficient Permissions for command: '%s' args '%s'" %(client.name, client.ip_string, self.qualified_command_name, command_line)
			org.cxsbs.core.logger.log.warn(context_description)
		except:
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
			context_description = "%s@%s: Uncaught exception occurred in command handler for command: '%s' args '%s'" %(client.name, client.ip_string, self.qualified_command_name, command_line)
			org.cxsbs.core.logger.log.warn(context_description)
			org.cxsbs.core.logger.log.warn(traceback.format_exc())

def get_command_decorator(command_manager):
	class CommandDecorator(object):
		def __init__(self, command_name, raw_line=False):
			self.command_name = command_name
			self.raw_line = raw_line
		
		def __call__(self, handler):
			self.__doc__ = handler.__doc__
			self.__name__ = handler.__name__
			command_manager.register(self.command_name, handler, self.raw_line)
			return handler
		
	return CommandDecorator
	
class CommandManager(object):
	def __init__(self):
		self.command_handlers = {}
		
	def get_allowed_commands(self, client):
		allowed = []
		
		for command_name, command in self.command_handlers.items():
			if client.isActionPermitted(command.qualified_command_name + "_execute"):
				allowed.append(command_name)
				
		return allowed
	
	def get_command(self, client, command_name):
		if command_name in self.command_handlers.keys():
			command = self.command_handlers[command_name]
			if not client.isActionPermitted(command.qualified_command_name + "_execute"):
				return None
			
			return command
			
		else:
			return None
		
	def register(self, command_name, handler, raw_line):
		self.command_handlers[command_name] = Command(command_name, handler)
		
	def on_command(self, event):
		'''
		@thread commands
		'''
		client = event.args[0]
		command_line = event.args[1]
		
		split_command_line = command_line.split(None, 1)
		if len(split_command_line) > 1:
			command_name, arguments = split_command_line
		else:
			command_name = split_command_line[0]
			arguments = ""
		
		if command_name in self.command_handlers.keys():
			self.command_handlers[command_name].execute(client, arguments)
		else:
			#tell the client we don't know about that command
			unknown_command_message.server(client)

def on_listcommands(client):
	"""
	@usage #listcommands
	@description View the available commands.
	$execute __all__
	@doc Lists those commands which the client can run.
	"""
	commands = org.cxsbs.core.commands.command_manager.get_allowed_commands(client)
	listcommands_message.server(client, {'commands': ", ".join(commands)})
	
def on_help(client, command_name=None):
	"""
	@usage #help [<command>]
	@description View information on a command.
	$execute __all__
	@doc Prints the command name, usage, and description.
	"""
	if command_name is None:
		help_command = org.cxsbs.core.commands.command_manager.get_command(client, "help")
		help_generic_message.server(client)
		usage_message.server(client, {'usage': help_command.usage})
		return
	
	command = org.cxsbs.core.commands.command_manager.get_command(client, command_name)
	if command is None:
		unknown_command_message.server(client)
		return
	
	help_description_message.server(client, {'command': command.command_name, 'description': command.description})
	usage_message.server(client, {'usage': command.usage})
