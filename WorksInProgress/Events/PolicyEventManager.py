from EventManager import EventManager

import sys, traceback

import cxsbs
Logging = cxsbs.getResource("Logging")

class PolicyEventManager(EventManager):
	def __init__(self):
		EventManager.__init__(self)
	def trigger(self, eventName, args=()):
		Logging.debug("PolicyEvent: " + eventName + " " + str(args))
		try:
			if eventName in self.events.keys():
				for event in self.events[eventName]:
						output = event(*args)
						if output == None:
							Logging.error("PolicyEventHandler: " + event.__name__ + " from module " + event.__module__ + " returned None.")
							pass
						elif not output:
							Logging.debug("PolicyEventHandler: " + event.__name__ + " from module " + event.__module__ + " returned False.")
							return False
						else:
							Logging.debug("PolicyEventHandler: " + event.__name__ + " from module " + event.__module__ + " returned True.")
			else:
				Logging.debug("PolicyEventHandler: No handler to policy event: " + eventName)
		except:
			Logging.error("PolicyEventHandler: error while processing policy event handlers.")
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
			Logging.error(traceback.format_exc())
			return False
		Logging.debug("PolicyEventHandler: No False' returned.")
		return True