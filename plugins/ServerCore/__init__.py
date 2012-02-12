import sbserver
	
import sys, inspect
import threading

import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		#this messy bit of code creates local callable objects for each function
		#in ServerCore which use execLater to be executed inside the servers event loop
		global_dict = globals()
		#print dir(sbserver)
		for name in dir(sbserver):
			obj = getattr(sbserver, name)
			if callable(obj):
				synchronizedCallable = SynchronizedCallable(obj)
				
				global_dict[name] = synchronizedCallable
		
	def unload(self):
		pass

import cxsbs
CoreLoop = cxsbs.getResource("CoreLoop")

class SynchronizedCallable:
	def __init__(self, function):
		self.function = function
		
	def __call__(self, *args):
		if CoreLoop.main_thread != threading.current_thread() and CoreLoop.running:
			#print "Got call to ServerCore function (%s) out of main thread synchronizing" % self.function.__name__
			event_flag = threading.Event()
			CoreLoop.execSynchronized(event_flag)
			event_flag.wait()
			#print "Received signal that we can execute function (%s) now." % self.function.__name__
			try:
				datum = self.function(*args)
			finally:
				CoreLoop.flag.set()
			#print "Signalled main thread that we're done executing our function (%s)." % self.function.__name__
			return datum
		else:
			#print "got call to ServerCore function (%s) in main thread passing through" % self.function.__name__
			return self.function(*args)