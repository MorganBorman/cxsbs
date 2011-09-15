from EventManager import EventManager

class PolicyEventManager(EventManager):
	def __init__(self):
		EventManager.__init__(self)
	def trigger(self, event, args=()):
		try:
			for event in self.events[event]:
					if not event(*args):
						return False
					
		except KeyError:
			return True
		return True