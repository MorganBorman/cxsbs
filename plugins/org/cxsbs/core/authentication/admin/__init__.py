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
		time_val_seed = str(time.time())
		object_id_seed = str(id(object()))
		
		seed_chars = []
		
		for ix in range(max(len(time_val_seed), len(object_id_seed))):
			try:
				seed_chars.append(time_val_seed[ix])
			except:
				seed_chars.append(str(random.random()))
				
			try:
				seed_chars.append(object_id_seed[ix])
			except:
				seed_chars.append((random.random()))
		
		return ''.join(seed_chars)

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