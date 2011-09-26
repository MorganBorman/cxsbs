import sys
import traceback

import cxsbs
Logging = cxsbs.getResource("Logging")
UI = cxsbs.getResource("UI")
EventInformation = cxsbs.getResource("EventInformation")

def executeEvent(func, args):
	"""Used to execute the event itself"""
	try:
		func(*args)
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.error('Uncaught exception occurred in event handler.')
		Logging.error(traceback.format_exc())

class EventManager:
	def __init__(self, Players=None):
		self.Players = Players
		self.events = {}
	def connect(self, event, func):
		if not event in self.events.keys():
			self.events[event] = []
		
		for i in range(len(self.events[event])):
			f = self.events[event][i]
			if f.__module__ == func.__module__ and f.__name__ == func.__name__:
				self.events[event][i] = func
				return
			
		self.events[event].append(func)
		
	def trigger(self, eventName, args=()):
		Logging.debug("Event: " + str(eventName) + " " + str(args))
		try:
			#Logging.debug("Event handlers: " + str(self.events[eventName]))
			for event in self.events[eventName]:
				info = EventInformation.getEventHandlerInfo(event)
				if info != None:
					if info.isCommandType:
						try:
							cn = args[0]
							Players = cxsbs.getResource('Events').Players
							p = Players.player(cn)
							if not EventInformation.allowEvent(info, p):
								UI.insufficientPermissions(p.cn)
								return
						except:
							Logging.error("Players probably was not bootstrapped into the event framework. Make sure a Players modules is loaded and does this.")
				executeEvent(event, args)
		except KeyError:
			pass