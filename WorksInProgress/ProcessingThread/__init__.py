import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global processingThread
		processingThread = ProcessingThread()
		processingThread.start()
		
	def unload(self):
		processingThread.stop()
	
import cxsbs
Logging = cxsbs.getResource("Logging")

import threading
import sys
import traceback
	
class ProcessingThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		
		self.running = True
		self.event_queue = []
		self.flag = threading.Event()
		
	def run(self):
		while self.running:
			
			self.flag.clear()
			self.flag.wait()
			
			while len(self.event_queue) > 0:
				event = self.event_queue.pop(0)
				#do something with it
				try:
					event[0](*(event[1]))
				except:
					exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
					Logging.error('Uncaught exception occurred in ProcessingThread.')
					Logging.error(traceback.format_exc())
					
	def stop(self):
		self.running = False
		self.flag.set()
				
	def queue(self, function, args, kwargs):
		
		datum = (function, args, kwargs)
		
		self.event_queue.append( datum )
		self.flag.set()
		
def queue(function, args=(), kwargs={}):
	"Queue a function and the args to execute it with."
	processingThread.queue(function, args, kwargs)