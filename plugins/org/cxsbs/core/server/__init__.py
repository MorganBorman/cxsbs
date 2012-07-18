import pyTensible, org
import CategoryConfig
import os.path
import cube2crypto
import random

class server(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		self.server_instance = ServerInstance()
		
		Interfaces = {}
		Resources = {
						'instance': self.server_instance,
						'state': ServerState(),
						'constants': ServerConstants(),
					}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

class ServerInstance(object):
	def __init__(self):
		config_path = self.root
		config_category = "instance"
		config_extension = ".conf"
		
		config_object = CategoryConfig.CategoryConfig(config_path, config_category, config_extension)
		
		doc_host = "What host/ip should this server instance listen on."
		default_host = "localhost"
		self._host = config_object.getOption('org.cxsbs.core.server.instance.host', default_host, doc_host)
		
		doc_port = "What port should this server instance listen on."
		default_port = "28785"
		self._port = config_object.getOption('org.cxsbs.core.server.instance.port', default_port, doc_port)
		
		doc_maxclients = "What should the absolute max number of clients be for this server instance."
		default_maxclients = "32"
		self._maxclients = config_object.getOption('org.cxsbs.core.server.instance.maxclients', default_maxclients, doc_maxclients)
		
		doc_instance_name = "The name that should be used to refer to this server instance."
		default_instance_name = os.path.basename(self.root)
		self._name = config_object.getOption('org.cxsbs.core.server.instance.name', default_instance_name, doc_instance_name)
		
		doc_instance_domain = "The domain that this server is serving for."
		default_instance_domain = "example.com"
		self._domain = config_object.getOption('org.cxsbs.core.server.instance.domain', default_instance_domain, doc_instance_domain)
		
		keypair = cube2crypto.genkeypair(format(random.getrandbits(128), 'X'))
		
		doc_instance_privkey = "The keys used to identify this server instance to other systems.\npubkey: %s" % keypair[1]
		default_instance_privkey = keypair[0]
		self._privkey = config_object.getOption('org.cxsbs.core.server.instance.privkey', default_instance_privkey, doc_instance_privkey)
		
		del config_object
		
		self._engine = None
		
	def run(self):
		#org.cxsbs.core.engine.Engine(self.host, self.port, self.maxclients, self.maxdown, self.maxup)
		engine = org.cxsbs.core.engine.Engine(self.host, self.port, self.maxclients, 0, 0)
		engine.start()
	
	@property
	def host(self):
		return self._host
	
	@property
	def port(self):
		return self._port
	
	@property
	def maxclients(self):
		return self._maxclients
	
	@property
	def name(self):
		return self._name
	
	@property
	def root(self):
		return instance_root
	
	@property
	def domain(self):
		return self._domain
	
	@property
	def privkey(self):
		return self._privkey


class enum(object):
	def __init__(self, items):
		i = 0
		for item in items:
			self.__setattr__(item, i)
			i += 1

class ServerConstants(object):
	item_modes = [0, 1, 9, 11, 13, 15]
	flag_modes = [11, 12, 13, 14, 15, 16, 17, 18, 19]
	base_modes = [9, 10]
	
	
class Team(object):
	name = ""
	
	def __init__(self, teamname):
		self.name = teamname
		
	@property
	def score(self):
		return cube2server.serverTeamScore(self.name)
	
	@score.setter
	def score(self, to_score):
		cube2server.serverSetTeamScore(self.name, to_score)
		
class Teams(object):
	def __getitem__(self, key):
		return Team(key)

class ServerState(object):
	@property
	def client_count(self):
		return cube2server.serverClientCount()
	
	@property
	def clients(self):
		return org.cxsbs.core.clients.client_manager.clients
	
	@property
	def client_states(self):
		return cube2server.serverClientStates()
	
	@property
	def uptime(self):
		return cube2server.serverUptime()
	
	@property
	def time_remaining(self):
		return cube2server.serverTimeRemaining()
	
	@time_remaining.setter
	def time_remaining(self, value):
		cube2server.serverSetTimeRemaining(value)
	
	class Variables:
		def __getitem__(self, key):
			cube2server.serverGetVariable(key)
		
		def __setitem__(self, key, value):
			cube2server.serverSetVariable(key, value)
			
	variables = property(Variables())
	
	@property
	def bot_limit(self):
		return cube2server.serverBotLimit()
	
	@bot_limit.setter
	def bot_limit(self, value):
		cube2server.serverSetBotLimit(value)
		
	@property
	def bot_balance(self):
		return cube2server.serverBotBalance()
	
	@bot_balance.setter
	def bot_balance(self, value):
		cube2server.serverSetBotBalance(value)
	
	@property
	def paused(self):
		return cube2server.serverTimeRemaining()
	
	@paused.setter
	def paused(self, value):
		cube2server.serverSetPaused(value)
	
	@property
	def mastermode(self):
		return cube2server.serverMasterMode()
	
	@mastermode.setter
	def mastermode(self, value):
		cube2server.serverSetMasterMode(value)
		
	@property
	def master_mask(self):
		return cube2server.serverMasterMask()
	
	@master_mask.setter
	def master_mask(self, value):
		cube2server.serverSetMasterMask(value)
		
	@property
	def game_mode(self):
		return cube2server.serverGameMode()
	
	@property
	def map_name(self):
		return cube2server.serverMapName()
	
	@property
	def max_clients(self):
		return cube2server.serverMaxClients()
	
	@property
	def capacity(self):
		return cube2server.serverCapacity()
	
	@capacity.setter
	def capacity(self, value):
		cube2server.serverSetCapacity(value)
		
	@property
	def match_recording(self):
		return cube2server.serverMatchRecording()
	
	@match_recording.setter
	def match_recording(self, value):
		cube2server.serverSetMatchRecording(value)
	
	@property
	def record_next_match(self):
		return cube2server.serverRecordNextMatch()
	
	@record_next_match.setter
	def record_next_match(self, value):
		cube2server.serverSetRecordNextMatch(value)
		
	@property
	def instance_root(self):
		return cube2server.serverInstanceRoot()
			
	@property
	def teams(self):
		return Teams()
	
	def message(self, msg):
		cube2server.serverMessage(msg)
		
	def send_map_reload(self):
		cube2server.serverSendMapReload()
		
	def set_map_mode(self, map_name, mode_number):
		cube2server.serverSetMapMode(map_name, mode_number)
		
	def set_map_items(self, items):
		cube2server.serverSetMapItems(items)
		
	def set_map_flags(self, flags):
		cube2server.serverSetMapFlags(flags)
		
	def set_map_bases(self, bases):
		cube2server.serverSetMapBases(bases)