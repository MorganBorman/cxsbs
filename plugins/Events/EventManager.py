import threading
import cxsbs
logging = cxsbs.getResource("Logging")

def executeEvent(func, args):
	"""Used to execute the event itself"""
	try:
		func(*args)
	except:
		exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
		logging.error('Uncaught exception occured in event handler.')
		logging.error(traceback.format_exc())

class EventThread(threading.Thread):
	def __init__(self, func, args):
		self.args = args
		self.func = func
		
		threading.Thread.__init__(self)

	def run(self):
		executeEvent(self.func, self.args)

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
			print "Event:", eventName, args
		try:
			if eventName.find("sync_") == 0:
				eventName = eventName[5:]
				for event in self.events[eventName]:
					executeEvent(event, args)
			else:
				for event in self.events[eventName]:
					et = EventThread(event, args)
					et.start()
		except KeyError:
			pass