import sys

import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		reactor.startRunning() #@UndefinedVariable
		
		import EventManager
		import PolicyEventManager
		
		global eventManager
		global policyEventManager
		
		eventManager = EventManager.EventManager()
		policyEventManager = PolicyEventManager.PolicyEventManager()
		
		#eventManager.events.clear()
		#policyEventManager.events.clear()
		
	def unload(self):
		global dont_iterate
		dont_iterate = True
		reactor.stop()
	
import cxsbs
Logging = cxsbs.getResource("Logging")
EventInformation = cxsbs.getResource("EventInformation")

import cxsbs.AsyncronousExecutor
		
from twisted.internet import reactor

import traceback

eventManager = None
policyEventManager = None
exec_queue = []

def registerServerEventHandler(event, func):
	'''Call function when event has been executed.'''
	EventInformation.loadEventHandlerInfo(event, func)
	eventManager.connect(event, func)

class eventHandler(object):
	'''Decorator which registers a function as an event handler.'''
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerServerEventHandler(self.name, f)
		return f
	
class EventThreadQueuer:
	def __init__(self, f):
		self.func = f
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__

	def __call__(self, *args, **kwargs):
		cxsbs.AsyncronousExecutor.dispatch(self.func, args=args, kwargs=kwargs, time=0)
		
class threadedEventHandler(object):
	'''Decorator to register an event as an asyncronous event handler.'''
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerServerEventHandler(self.name, EventThreadQueuer(f))
		return f

def triggerServerEvent(event, args):
	'''Trigger event with arguments.'''
	eventManager.trigger(event, args)

def registerPolicyEventHandler(event, func):
	'''Call function when policy event has been executed.'''
	policyEventManager.connect(event, func)

class policyHandler(object):
	'''Decorator which registers a function as a policy event handler.'''
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerPolicyEventHandler(self.name, f)
		return f

def triggerPolicyEvent(event, args):
	'''Trigger policy event with arguments.'''
	return policyEventManager.trigger(event, args)

def execLater(func, args):
	'''Call function at a later time with arguments in tuple args.'''
	exec_queue.append((func, args))

def triggerExecQueue():
	for event in exec_queue:
		try:
			event[0](*event[1])
		except:
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
			Logging.warn('Uncaught exception execLater queue.')
			Logging.warn(traceback.format_exc())
			Logging.warn(traceback.extract_tb(exceptionTraceback))
	del exec_queue[:]
	
def bootStrapPlayersModule(module):
	global Players
	Players = module

def update():
		reactor.runUntilCurrent() #@UndefinedVariable
		reactor.doIteration(0) #@UndefinedVariable
		triggerExecQueue()