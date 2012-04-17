import pyTensible, org

class manager(pyTensible.Plugin):
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
			
		class select(object):
			'''Decorator which creates a select entry in the event manager'''
			def __init__(self, filters, timeout, thread):
				if len(filters.keys()) < 1:
					raise ValueError("Must specify at least one filter to select events on.")
				
				self.filters = filters
				self.thread = thread
				
				def is_correct_timeout(event):
					return event.args[0] == id(self)
				
				#create timeout timer for the authorities response
				timeout_event = org.cxsbs.core.events.manager.Event('select_timeout', (id(self),), {})
				timeout_timer = org.cxsbs.core.timers.Timer(timeout, (timeout_event,))
				self.filters['select_timeout'] = is_correct_timeout
				org.cxsbs.core.timers.timer_manager.add_timer(timeout_timer)
			
			def __call__(self, callback):
				select_object = RSelect(self.filters, callback, self.thread)
				
				event_manager.initialize_select(select_object)
		
		def trigger_event(event_name, args=(), kwargs={}):
			event_manager.trigger_event(REvent(event_name, args, kwargs))
		
		Interfaces = {}
		Resources = 	{
							'event_manager': event_manager, 
							'Event': REvent, 
							'trigger_event': trigger_event, 
							'event_handler': event_handler, 
							'select': select,
						}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
class REvent(org.cxsbs.core.events.interfaces.IEvent):
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
	
class RSelect(org.cxsbs.core.events.interfaces.ISelect):
	'''
	Takes a dictionary of event names and filter functions to determine
	Whether the given event actually would be selected.
	
	Also a timeout may be specified, which uses the select_timeout event
	with this as an argument.
	'''
	def __init__(self, filters, callback, thread="main"):
		
		for filter in filters.values():
			if not callable(filter):
				raise TypeError("The filter parameters passed to a Select object must be callable.")
			
		if not callable(callback):
			raise TypeError("The callback parameters passed to a Select object must be callable.")
		
		self.__filters = filters
		self.__callback = callback
		self.__thread = thread
		
	@property
	def filters(self):
		return self.__filters
	
	@property
	def callback(self):
		return self.__callback
    
	@property
	def thread(self):
		return self.__thread
	
import sys, traceback
	
class REventManager(org.cxsbs.core.events.interfaces.IEventManager):
	"An event manager allowing multiple handlers of any callable type to be supplied for each named event."
	#dictionary of event handler info indexed by the event name handled
	handlers_info = {}
	#a list of the selects which are pending
	selects = []
	
	def __init__(self):
		self.handlers_info = {}
		self.selects = []
	
	def initialize_select(self, select):
		"Add a select to the list of selects."
		
		if not isinstance(select, org.cxsbs.core.events.interfaces.ISelect):
			raise TypeError("Expected an select object implementing the IEvent interface. Got an object of %s class." %event.__class__.__name__)
		
		self.selects.append(select)
		
	def invoke_selects(self, event):
		"Check whether there are any active selects which are satisfied by this event"
		
		for select in self.selects:
			if event.name in select.filters.keys():
				try:
					if select.filters[event.name](event):
						self.selects.remove(select)
						try:
							org.cxsbs.core.threads.thread_manager.queue(select.thread, select.callback, (event,), {})
						except:
							exception_type, exception_value, exception_traceback = sys.exc_info()	#@UnusedVariable
							org.cxsbs.core.logger.log.error(traceback.format_exc())
				except:
					pass
				
	def register_handler(self, name, handler):
		"Register an event handler function or other callable for a specified event."
		
		org.cxsbs.core.logger.log.debug("Events: Registering handler: %s for: %s", str(handler), str(name))
		if not name in self.handlers_info.keys():
			self.handlers_info[name] = []
			
		handler_info = org.cxsbs.core.events.information.HandlerInformation(name, handler)
			
		self.handlers_info[name].append(handler_info)
		
	def invoke_handlers(self, event):
		
		if event.name in self.handlers_info.keys():
			for handler_info in self.handlers_info[event.name]:
				try:
					org.cxsbs.core.threads.thread_manager.queue(handler_info.thread, handler_info.handler, (event,), {})
				except:
					exception_type, exception_value, exception_traceback = sys.exc_info()	#@UnusedVariable
					org.cxsbs.core.logger.log.error(traceback.format_exc())
	
	def trigger_event(self, event):
		"Trigger an event of the given name with the given arguments. Safe even if their is no handler yet registered for the named event."
		if not isinstance(event, org.cxsbs.core.events.interfaces.IEvent):
			raise TypeError("Expected an event object implementing the IEvent interface. Got an object of %s class." %event.__class__.__name__)
		
		org.cxsbs.core.logger.log.debug("Events: Triggering event: %s with args: %s", str(event.name), str(event.args) + str(event.kwargs))
		
		#trigger the handlers which match this event
		self.invoke_handlers(event)
		
		#just in case we get flooded with something which creates a lot of selects we don't want it to slow down our event system
		#also select handling is by nature more expensive than the rest of the event system
		org.cxsbs.core.threads.thread_manager.queue('selects', self.invoke_selects, (event,), {})
