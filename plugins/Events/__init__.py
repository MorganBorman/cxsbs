from cxsbs.Plugin import Plugin

from twisted.internet import reactor

import EventManager
import PolicyEventManager

eventManager = None
policyEventManager = None

def registerServerEventHandler(event, func):
	'''Call function when event has been executed.'''
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
			logging.warn('Uncaught exception execLater queue.')
			logging.warn(traceback.format_exc())
			logging.warn(traceback.extract_tb(exceptionTraceback))
	del exec_queue[:]

def update():
	reactor.runUntilCurrent() #@UndefinedVariable
	reactor.doIteration(0) #@UndefinedVariable
	triggerExecQueue()

reactor.startRunning() #@UndefinedVariable

class Events(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		global eventManager
		global policyEventManager
		
		eventManager = EventManager.EventManager()
		policyEventManager = PolicyEventManager.PolicyEventManager()
		
	def reload(self):
		eventManager.events.clear()
		policyEventManager.events.clear()
		
	def unload(self):
		print "Events Plugin: unload function"
		