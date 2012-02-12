import sys

import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		import EventManager
		import PolicyEventManager
		
		global eventManager
		global policyEventManager
		
		eventManager = EventManager.EventManager()
		eventManager.start()
		policyEventManager = PolicyEventManager.PolicyEventManager()
		
		#eventManager.events.clear()
		#policyEventManager.events.clear()
		
	def unload(self):
		pass
	
import cxsbs
Logging = cxsbs.getResource("Logging")
EventInformation = cxsbs.getResource("EventInformation")

eventManager = None
policyEventManager = None

##############################
##	Handler Registration	##
##############################

def registerServerEventHandler(event, func):
	'''Call function when event has been executed.'''
	EventInformation.loadEventHandlerInfo(event, func)
	eventManager.connect(event, func)
	
def registerPolicyEventHandler(event, func):
	'''Call function when policy event has been executed.'''
	policyEventManager.connect(event, func)
	
def registerAllEventHandler(func):
	'''Register an event handler to all events'''
	eventManager.connectAll(func)
	
##############################
##	Event Triggering		##
##############################
	
def triggerServerEvent(event, args):
	'''Trigger event with arguments.'''
	eventManager.trigger(event, args)

def triggerPolicyEvent(event, args):
	'''Trigger policy event with arguments.'''
	return policyEventManager.trigger(event, args)

##############################
##	Decorators				##
##############################

class eventHandler(object):
	'''Decorator which registers a function as an event handler.'''
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerServerEventHandler(self.name, f)
		return f
	
class policyHandler(object):
	'''Decorator which registers a function as a policy event handler.'''
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.__doc__ = f.__doc__
		self.__name__ = f.__name__
		registerPolicyEventHandler(self.name, f)
		return f
		
##############################
##	Other					##
##############################
		
def bootStrapPlayersModule(module):
	global Players
	Players = module