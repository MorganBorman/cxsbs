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
def full_admin_keypair():
		"""
		@category authentication
		@display_name Full Admin Keypair
		@wbpolicy immediate
		@doc This is the authkey pair which is used to gain full administrative access to server.
		"""
		admin_key_pair = cube2crypto.genkeypair(generate_seed())
		print admin_key_pair
		return admin_key_pair
	
class AdminCredential(org.cxsbs.core.authentication.interfaces.ICredential):
	def __init__(self):
		pass
	
	@property
	def groups(self):
		return ("com.example.admin",)
	
	def deauthorize(self):
		pass
	
class AdminAuthority(org.cxsbs.core.authentication.interfaces.IAuthority):
	def __init__(self):
		pass
	
	@property
	def domains(self):
		#TODO: 	Make a setting initialized in org.cxsbs.core.server to specify the domain name of this server instance
		#		then use that here.
		return ("com.example.admin",)
	
	def request(self, auth_ev):
		challenge, answer = cube2crypto.genchallenge(settings['full_admin_keypair'][1], generate_seed())
		auth_ev.answer = answer
		org.cxsbs.core.events.manager.trigger_event('authority_challenge', (auth_ev.global_id, challenge))
	
	def validate(self, auth_ev, answer):
		if auth_ev.answer == answer:
			org.cxsbs.core.events.manager.trigger_event('authority_authorize', (auth_ev.global_id, AdminCredential()))
		else:
			org.cxsbs.core.events.manager.trigger_event('authority_deny', (auth_ev.global_id,))

	def shutdown(self):
		pass