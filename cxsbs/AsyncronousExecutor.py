import concurrent.futures
import twisted.internet
import threading

executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def queue(func, *args, **kwargs):
	executor.submit(func, *args, **kwargs)
	
def dispatch(func, *args, **kwargs):
	twisted.internet.reactor.callLater(0, func, *args)
	
import time
	
#my own version because the twisted one is being stupid
class LoopingCall(threading.Thread):
	''''A looping call, similar to the one in twisted, except we'll be able to exit with this one.'''
	def __init__(self, interval, function, callAtStart=True, *args, **kwargs):
		'''
		interval is a number of seconds between calls to function
			only supports whole seconds >1
		
		'''
		threading.Thread.__init__(self)
		
		self.interval = interval
		self.function = function
		self.args = args
		self.kwargs = kwargs
		callAtStart = callAtStart
		self.lastRun = None
		self.running = False
		
	def execute(self):
		self.lastRun = time.time()
		self.function(*self.args, **self.kwargs)
		
	def run(self):
		self.running = True
		try:
			while self.running:
				if self.lastRun == None:
					self.execute()
				elif (time.time() - self.lastRun) > self.interval:
					self.execute()
				else:
					pass
				time.sleep(1)
		except:
			print "caught exception in LoopingCall"
			self.running = False