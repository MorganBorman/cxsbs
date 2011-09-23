import sys

import cxsbs
Logging = cxsbs.getResource("Logging")

def executeEvent(func, args):
	"""Used to execute the event itself"""
	try:
		func(*args)
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		Logging.error('Uncaught exception occured in event handler.')
		Logging.error(traceback.format_exc())

class EventManager:
	def __init__(self, debugging=False):
		self.debugging = debugging
		self.events = {}
	def connect(self, event, func):
		try:
			self.events[event].append(func)
		except KeyError:
			self.events[event] = []
			self.connect(event, func)
	def trigger(self, eventName, args=()):
		if self.debugging:
			Logging.debug("Event: " + eventName + " " + str(args))
		try:
			for event in self.events[eventName]:
				executeEvent(event, args)
		except KeyError:
			pass