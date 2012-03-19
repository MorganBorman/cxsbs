import pyTensible, abc, org

class interfaces(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
class IAuthority:
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractproperty
	def name(self):
		pass
	
	@abc.abstractmethod
	def args(self):
		pass