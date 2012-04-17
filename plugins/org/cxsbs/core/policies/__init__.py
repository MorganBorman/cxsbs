import pyTensible, abc, org

import sys, traceback

class policies(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		policy_manager = RPolicyManager()
		
		class policy_handler(object):
			'''Decorator which registers a function as an policy handler.'''
			def __init__(self, name):
				self.name = name
			def __call__(self, f):
				self.__doc__ = f.__doc__
				self.__name__ = f.__name__
				policy_manager.register_handler(self.name, f)
				return f
		
		Interfaces = {'IPolicyManager': IPolicyManager, 'IQuery': IQuery}
		Resources = {'policy_manager': policy_manager, 'Query': RQuery, 'query_policy': policy_manager.query_policy, 'policy_handler': policy_handler}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
class IQuery:
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractproperty
	def name(self):
		pass
	
	@abc.abstractproperty
	def default(self):
		pass
	
	@abc.abstractproperty
	def args(self):
		pass
	
	@abc.abstractproperty
	def kwargs(self):
		pass

class IPolicyManager:
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def register_handler(self, name, handler):
		pass
	
	@abc.abstractmethod
	def query_policy(self, query):
		pass
	
class RQuery(IQuery):
	def __init__(self, name, default=False, args=(), kwargs={}):
		self._name = name
		self._default = default
		self._args = args[:]
		self._kwargs = {}
		self._kwargs.update(kwargs)
	
	@property
	def name(self):
		return self._name
	
	@property
	def default(self):
		return self._default
	
	@property
	def args(self):
		return self._args
	
	@property
	def kwargs(self):
		return self._kwargs
	
class RPolicyManager(IPolicyManager):
	"A Policy manager which calls the set of handlers for each policy and returns a binary answer."
	#dictionary of policy handlers indexed by the policy name handled
	handlers = {}
	
	def __init__(self):
		self.handlers = {}
				
	def register_handler(self, name, handler):
		"Register a policy handler function or other callable for a specified event."
		
		org.cxsbs.core.logger.log.debug("Policies: Registering handler: %s for: %s", str(handler), str(name))
		if not name in self.handlers.keys():
			self.handlers[name] = []
			
		self.handlers[name].append(handler)
	
	def query_policy(self, query):
		if not isinstance(query, IQuery):
			raise TypeError("Expected a query object implementing the IQuery interface. Got an object of %s class." %query.__class__.__name__)
		
		org.cxsbs.core.logger.log.debug("Policies: Querying policy: %s with args: %s and default of: %s", str(query.name), str(query.args) + str(query.kwargs), str(query.default))
		
		if query.name in self.handlers.keys():
			for handler in self.handlers[query.name]:
				try:
					response = handler(query)
					if response in [True, False]:
						return 
				except:
					exception_type, exception_value, exception_traceback = sys.exc_info()	#@UnusedVariable
					org.cxsbs.core.logger.log.error(traceback.format_exc())
					
		return query.default