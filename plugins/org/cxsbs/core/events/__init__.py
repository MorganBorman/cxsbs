class events(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		event_manager = REventManager()
		
		class event_handler(object):
			'''Decorator which registers a function as an event handler.'''
			def __init__(self, name):
				self.name = name
			def __call__(self, f):
				self.__doc__ = f.__doc__
				self.__name__ = f.__name__
				event_manager.register_handler(self.name, f)
				return f
		
		def trigger_event(event_name, *args, **kwargs):
			event_manager.trigger_event(REvent(event_name, args, kwargs))
		
		Interfaces = {'IEventManager': IEventManager, 'IEvent': IEvent}
		Resources = {'event_manager': event_manager, 'Event': REvent, 'trigger_event': trigger_event, 'event_handler': event_handler}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
class IEvent:
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractproperty
	def name(self):
		pass
	
	@abc.abstractproperty
	def args(self):
		pass
	
	@abc.abstractproperty
	def kwargs(self):
		pass

class IEventManager:
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def register_handler(self, name, handler):
		pass
	
	@abc.abstractmethod
	def trigger_event(self, event):
		pass
	
class REvent(IEvent):
	def __init__(self, name, args=(), kwargs={}):
		self._name = name
		self._args = args[:]
		self._kwargs = {}
		self._kwargs.update(kwargs)
	
	@property
	def name(self):
		return self._name
	
	@property
	def args(self):
		return self._args
	
	@property
	def kwargs(self):
		return self._kwargs
	
import sys, traceback
	
class REventManager(IEventManager):
	"An event manager allowing multiple handlers of any callable type to be supplied for each named event."
	#dictionary of event handlers indexed by the event name handled
	handlers = {}
	
	def __init__(self):
		self.handlers = {}
				
	def register_handler(self, name, handler):
		"Register an event handler function or other callable for a specified event."
		
		pyTensible.plugin_loader.logger.debug("Events: Registering handler: %s for: %s", str(handler), str(name))
		if not name in self.handlers.keys():
			self.handlers[name] = []
			
		self.handlers[name].append(handler)
	
	def trigger_event(self, event):
		"Trigger an event of the given name with the given arguments. Safe even if their is no handler yet registered for the named event."
		if not isinstance(event, IEvent):
			raise TypeError("Expected an event object implementing the IEvent interface. Got an object of %s class." %event.__class__.__name__)
		
		pyTensible.plugin_loader.logger.debug("Events: Triggering event: %s with args: %s", str(event.name), str(event.args) + str(event.kwargs))
		
		if event.name in self.handlers.keys():
			for handler in self.handlers[event.name]:
				try:
					handler(event)
				except:
					exception_type, exception_value, exception_traceback = sys.exc_info()	#@UnusedVariable
					pyTensible.plugin_loader.logger.error(traceback.format_exc())