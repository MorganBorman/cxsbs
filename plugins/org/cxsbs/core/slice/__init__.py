import pyTensible, org

class slice(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {'update': update, 'queue': queue}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

import sys, traceback

function_queue = []

def update():
	while len(function_queue) > 0:
		item = function_queue.pop(0)
		try:
			item[0](*item[1], **item[2])
		except:
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
			pyTensible.plugin_loader.logger.error("Uncaught exception occurred in server slice queue." %self.name)
			pyTensible.plugin_loader.logger.error(traceback.format_exc())

def queue(func, args, kwargs):
	function_queue.append((func, args, kwargs))

@org.cxsbs.core.events.manager.event_handler('server_stop')
def on_server_stop(event):
	print "\nServer going down."
	org.cxsbs.core.events.manager.trigger_event('server_shutdown')
	pyTensible.plugin_loader.unload_all()
	
@org.cxsbs.core.events.manager.event_handler('server_reload')
def on_server_reload(event):
	print "Reloading server. Hang on."
	pyTensible.plugin_loader.unload_all()