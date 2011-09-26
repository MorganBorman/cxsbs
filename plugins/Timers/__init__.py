import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
import twisted.internet

def addTimer(msecs, func, args=(), persistent=False):
	if not persistent:
		twisted.internet.reactor.callLater(msecs / 1000, func, *args) #@UndefinedVariable
	else:
		call = twisted.internet.task.LoopingCall(func, *args)
		call.start(msecs / 1000)