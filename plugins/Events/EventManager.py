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
	def __init__(self, Players=None, debugging=False):
		self.Players = Players
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