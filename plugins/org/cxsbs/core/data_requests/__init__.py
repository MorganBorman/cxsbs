import pyTensible, org

class data_requests(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {'data_request_handler': data_request_handler}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
class DataRequest(object):
	name = ""
	args = []
	kwargs = {}
	def __init__(self, name, args, kwargs):
		self.name = name
		self.args = args
		self.kwargs = kwargs
	
class data_request_handler(object):
	'''Decorator which acts as a proxy around a function as a data request handler.'''
	def __init__(self, name):
		self.name = name
	def __call__(self, f):
		self.func = f
		
		def handle(event):
			if event.args[0] == self.name:
				request = DataRequest(self.name, event.args[1:], event.kwargs)
				self.func(request)
				
		handle.__doc__ = f.__doc__
		handle.__name__ = f.__name__
		
		org.cxsbs.core.events.manager.event_manager.register_handler("data_request", handle)
		return f