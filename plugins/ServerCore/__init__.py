import sbserver
	
import sys, inspect

import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		#this messy bit of code creates local callable objects for each function
		#in ServerCore which use execLater to be executed inside the servers event loop
		global_dict = globals()
		print dir(sbserver)
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
		CoreLoop.execLater(self.function, args)