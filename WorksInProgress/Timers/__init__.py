import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
		
import twisted.internet

def addTimer(msecs, func, args=(), kwargs={}, persistent=False):
	if not persistent:
		twisted.internet.reactor.callLater(msecs / 1000, func, *args, **kwargs) #@UndefinedVariable
	else:
		call = twisted.internet.task.LoopingCall(func, *args, **kwargs)
		call.start(msecs / 1000)