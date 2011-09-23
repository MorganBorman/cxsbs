from EventManager import EventManager

import cxsbs
Logging = cxsbs.getResource("Logging")

class PolicyEventManager(EventManager):
	def __init__(self, debugging=False):
		EventManager.__init__(self, debugging)
	def trigger(self, event, args=()):
		if self.debugging:
			Logging.debug("PolicyEvent: " + eventName + " " + str(args))
		try:
			for event in self.events[event]:
					output = event(*args)
					if output == None:
						Logging.error("PolicyEventHandler: " + event.__name__ + " from module " + event.__module__ + " returned None.")
						pass
					elif not output:
						return False
		except KeyError:
			return True
		return True