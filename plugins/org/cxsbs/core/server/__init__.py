import pyTensible, org

class server(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		#self.server_object = ServerClass()
		
		Interfaces = {}
		Resources = {
						'state': ServerState(),
						'constants': ServerConstants(),
					}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
import cube2server

class enum(object):
	def __init__(self, items):
		i = 0
		for item in items:
			self.__setattr__(item, i)
			i += 1

class ServerConstants(object):
	pass
	
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
	def set_time_remaining(self, value):
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
	def master_mode(self):
		return cube2server.serverMasterMode()
	
	@master_mode.setter
	def master_mode(self, value):
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