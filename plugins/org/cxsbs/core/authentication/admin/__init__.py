import pyTensible, org

class admin(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {'AdminAuthority': AdminAuthority}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.authentication.admin')

import cube2crypto
import time
import random

def generate_seed():
	return format(random.getrandbits(128), 'X')

@org.cxsbs.core.settings.manager.Setting
def root_keypair():
		"""
		@category authentication
		@display_name Root Keypair
		@wbpolicy immediate
		@doc This is the authkey pair which is used to gain full administrative access to server.
		"""
		return cube2crypto.genkeypair(generate_seed())
	
class AdminCredential(org.cxsbs.core.authentication.interfaces.ICredential):
	def __init__(self):
		pass
	
	@property
	def groups(self):
		return ("__root__",)
	
	def deauthorize(self):
		pass
	
class AdminAuthority(org.cxsbs.core.authentication.interfaces.IAuthority):
	def __init__(self):
		print settings['root_keypair']
	
	@property
	def domains(self):
		#TODO: 	Make a setting initialized in org.cxsbs.core.server to specify the domain name of this server instance
		#		then use that here.
		return ("local." + org.cxsbs.core.server.instance.domain,)
	
	def request(self, auth_ev):
		if auth_ev.name != "root":
			org.cxsbs.core.events.manager.trigger_event('authority_deny', (auth_ev.global_id,))
			return
		
		challenge, answer = cube2crypto.genchallenge(settings['root_keypair'][1], generate_seed())
		auth_ev.answer = answer
		org.cxsbs.core.events.manager.trigger_event('authority_challenge', (auth_ev.global_id, challenge))
	
	def validate(self, auth_ev, answer):
		if auth_ev.answer == answer:
			org.cxsbs.core.events.manager.trigger_event('authority_authorize', (auth_ev.global_id, AdminCredential()))
		else:
			org.cxsbs.core.events.manager.trigger_event('authority_deny', (auth_ev.global_id,))

	def shutdown(self):
		pass