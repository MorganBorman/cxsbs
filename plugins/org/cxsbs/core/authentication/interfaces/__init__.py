import pyTensible, abc, org

class interfaces(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {'IAuthority': IAuthority, 'ICredential': ICredential}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
class IAuthority(object):
	__metaclass__ = abc.ABCMeta
	
	"""
	These objects also must emit the following events:
		authority_challenge (global_id, challenge) {}
		authority_authorize (global_id) {}
		authority_deny (global_id) {}
	
	"""
	
	@abc.abstractproperty
	def domains(self):
		"Return the domains for which this authority handles authentication requests."
		pass
	
	@abc.abstractmethod
	def request(self, authentication_event):
		"Called when a client attempts to authenticate with this authority."
		pass
	
	@abc.abstractmethod
	def validate(self, authentication_event, answer):
		"Called when a client sends their challenge response."
		pass
	
	@abc.abstractmethod
	def shutdown(self):
		"Called by org.cxsbs.core.authentication.manager when the server is going down."
		pass
	
class ICredential(object):
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractproperty
	def groups(self):
		"Return the groups that this client is part of."
		pass
	
	@abc.abstractmethod
	def deauthorize(self):
		"Called when the client has been deauthorized from a particular authority."
		pass