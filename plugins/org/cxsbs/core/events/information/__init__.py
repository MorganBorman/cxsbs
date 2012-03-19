import pyTensible, org

class information(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {'HandlerInformation': RHandlerInformation}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
class RHandlerInformation(org.cxsbs.core.events.interfaces.IHandlerInformation):
	_name = ""
	_event_name = ""
	_handler = None
	_thread = "main"
	_documentation = ""
	
	@property
	def name(self):
		return self._name
	
	@property
	def event_name(self):
		return self._event_name
	
	@property
	def handler(self):
		return self._handler
	
	@property
	def thread(self):
		return self._thread
	
	@property
	def documentation(self):
		return self._documentation
	
	def __init__(self, event_name, handler):
		self._name = handler.__name__ + '@' + handler.__module__
		self._event_name = event_name
		self._handler = handler
		self._thread = "main"
		self._documentation = ""
		
		docs = handler.__doc__
		if docs != None:
			lines = docs.split('\n')
			doc = False
			
			for line in lines:
				line = line.strip()
				if len(line) > 0 or doc:
					if doc:
						info._documentation += line + '\n'
					elif line[0] == '@':
						tag = line.split(' ', 1)[0].lower()
						text = line[len(tag)+1:]
						if tag == '@thread':
							self._thread = text
							doc = False
						elif tag == '@doc':
							doc = True
							self._documentation += text + '\n'
		else:
			pass #log here