from EventManager import EventManager

class PolicyEventManager(EventManager):
	def __init__(self, debugging=False):
		EventManager.__init__(self, debugging)
	def trigger(self, event, args=()):
		if self.debugging:
			print "PolicyEvent:", event, args
		try:
			for event in self.events[event]:
					if not event(*args):
						return False
					
		except KeyError:
			return True
		return True