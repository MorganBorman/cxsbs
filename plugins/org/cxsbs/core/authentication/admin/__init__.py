import pyTensible, org

class voting(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = 	{}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.authentication.admin')

import cube2crypto

@org.cxsbs.core.settings.manager.Setting
def full_admin_keypair():
		"""
		@category authentication
		@display_name 
		@wbpolicy immediate
		@doc This is the authkey pair which is used to gain full administrative access to server.
		"""
		return cube2crypto.genkeypair()