import pyTensible, org

class threads(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		self.thread_manager = ThreadManager()
		
		Interfaces = {}
		Resources = {'thread_manager': self.thread_manager, 'queue': self.thread_manager.queue}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		self.thread_manager.stop_all()

class ThreadManager:
	def __init__(self):
		self.processing_threads = {}
	
	def start(self, name):
		if name == "main":
			return
		
		if not name in self.processing_threads.keys():
			self.processing_threads[name] = ProcessingThread(name)
			self.processing_threads[name].start()
	
	def queue(self, name, function, args, kwargs):
		if name == "main":
			org.cxsbs.core.slice.queue(function, args, kwargs)
			return
		
		if not name in self.processing_threads.keys():
			self.start(name)
			
		self.processing_threads[name].queue(function, args, kwargs)
	
	def stop_all(self):
		for processing_thread in self.processing_threads.values():
			processing_thread.stop()
	
	def stop(self, name):
		if name == "main":
			return
		
		if name in self.processing_threads.keys():
			self.processing_threads[name].stop()
		
	def join_all(self):
		for processing_thread in self.processing_threads.values():
			processing_thread.join()
		
import threading
import sys
import traceback
	
class ProcessingThread(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		
		self.name = name
		self.running = True
		self.event_queue = []
		self.flag = threading.Event()
		self.flag.clear()
		
	def run(self):
		while self.running:
			
			self.flag.wait()
			
			while len(self.event_queue) > 0:
				event = self.event_queue.pop(0)
				#do something with it
				try:
					event[0](*(event[1]))
				except:
					exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
					org.cxsbs.core.logger.log.error("Uncaught exception occurred in a ProcessingThread named %s." %self.name)
					org.cxsbs.core.logger.log.error(traceback.format_exc())
					
	def stop(self):
		self.running = False
		self.flag.set()
				
	def queue(self, function, args, kwargs):
		
		datum = (function, args, kwargs)
		
		self.event_queue.append( datum )
		self.flag.set()