import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import abc
import cxsbs
Commands = cxsbs.getResource("Commands")
	
class Manager(object):
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def __init__(self):
		pass
		
	@abc.abstractmethod
	def search(self, cn, term):
		pass
	
	@abc.abstractmethod
	def searchAction(self, cn, term):
		pass
	
	@abc.abstractmethod
	def clear(self, cn, identifier):
		pass
	
	@abc.abstractmethod
	def insert(self, cn, ip, seconds, reason):
		pass
	
	@abc.abstractmethod
	def recent(self, cn, count):
		pass

class Management:
	def __init__(self):
		self.managers = {}
		
	def register(self, handle, manager):
		"""handle is the one word identifier for the manager in question."""
		self.managers[handle] = manager
		
	def search(self, cn, handle, term):
		self.managers[handle].search(cn, term)
		
	def searchAction(self, cn, handle, term):
		self.managers[handle].searchAction(cn, term)
		
	def clear(self, cn, handle, identifier):
		self.managers[handle].clear(cn, identifier)
		
	def insert(self, cn, handle, ip, mask, actionTime, reason):
		self.managers[handle].insert(cn, ip, mask, actionTime, reason)
	
	def recent(self, cn, handle, show_expired, count):
		self.managers[handle].recent(cn, show_expired, count)

management = Management()
		
def registerManager(handle, manager):
	management.register(handle, manager)
	
@Commands.commandHandler('search')
def onSearchCommand(cn, args):
	'''
	@description Search among the various registered search scopes
	@usage <scope> <term>
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Search among the various registered search scopes
	'''
	try:
		text = args
		args = args.split()
		if len(args) < 2:
			raise Commands.UsageError()
		handle = args[0]
		term = text[len(args[0]) + 1:]
		management.search(cn, handle, term)
	except (ValueError, KeyError, IndexError):
		raise Commands.UsageError()
	
#@Commands.commandHandler('searchAction')
def onSearchActionCommand(cn, args):
	'''
	@description Interactively search and perform an action on the results
	@usage <scope> <term>
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Interactively search and perform an action on the results
	'''
	try:
		text = args
		args = args.split()
		if len(args) < 2:
			raise Commands.UsageError()
		handle = args[0]
		term = text[len(args[0]) + 1:]
		management.searchAction(cn, handle, term)
	except (ValueError, KeyError, IndexError):
		raise Commands.UsageError()
	
@Commands.commandHandler('clear')
def onClearCommand(cn, args):
	'''
	@description Clear a particular id entry from the data
	@usage <scope> <id>
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Clear a particular id entry from the data
	'''
	try:
		args = args.split()
		handle = args[0]
		identifier = int(args[1])
		management.clear(cn, handle, identifier)
	except (ValueError, KeyError, IndexError):
		raise Commands.UsageError()
	
@Commands.commandHandler('insert')
def onRecentCommand(cn, args):
	'''
	@description Insert a new item of a scope.
	@usage <scope> <ip>(:mask) (time string) (reason)
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Insert a new item of a scope.
	'''
	try:
		args = args.split()
		handle = args[0]
		
		if len(args) < 2:
			raise Commands.UsageError()
				
		if ":" in args[1]:
			sp = args[1].split(':')
			
			if len(sp) != 2:
				raise Commands.ArgumentValueError("Extra ':' found when determining command target.")
			
			args[1] = sp[0]
			
			mask = sp[1]
		else:
			mask = "255.255.255.255"
				
		ip = args[1]
		
		if len(args) < 3:
			actionTime = None
		else:
			actionTime = args[2]
			
		if len(args) < 4:
			reason = None
		else:
			reason = ' '.join(args[3:])
			
		management.insert(cn, handle, ip, mask, actionTime, reason)
	except (ValueError, KeyError, IndexError):
		raise Commands.UsageError()
	
def castBool(string):
	if string.lower() == "true" or string.lower() == 'yes':
		return True
	try:
		v = int(string)
		if v > 0:
			return True
	except ValueError:
		return False
	
@Commands.commandHandler('recent')
def onRecentCommand(cn, args):
	'''
	@description List recent items among the search scope
	@usage <scope> (show expired=False) (count)
	@allowGroups __admin__ __master__
	@denyGroups
	@doc List recent items in the given search scope.
	'''
	try:
		args = args.split()
		
		handle = args[0]
		
		if len(args) > 1:
			show_expired = castBool(args[1])
		else:
			show_expired = False
		
		if len(args) > 2:
			count = int(args[2])
		else:
			count = 10
			
		management.recent(cn, handle, show_expired, count)
	except (ValueError, KeyError, IndexError):
		raise Commands.UsageError()
	