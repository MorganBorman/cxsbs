
import sys
import os
import time as time_module

cxsbsPath = os.path.abspath("../")
sys.path.append(cxsbsPath)
os.chdir(cxsbsPath)

from debugServerOrchestrator import Orchestrator, TimedEventGenerator, DataRequestHandler, RepeatingEventGenerator, ServerEvent, FunctionEvent
orchestrator = Orchestrator(maxFrames=1800, printFrame=False, printEvents=False, printFps=True)

import sbserver

sbserver.orchestratorContainer.setOrchestrator(orchestrator)

class Server:
	def __init__(self):
		self.players = {}
		self.mastermode = 0
		self.mode = None
		self.map = None
		self.paused = False
		self.max_clients = 124
		self.start_time = time_module.time()
		
		self.variables = {}
		self.variables['serverport'] = 28785
		self.variables['serverip'] = "127.0.0.1"
		
	def instanceRoot(self, time, frame, args):
		return cxsbsPath + "/instances/pydev/"
	
	def uptime(self, time, frame, args):
		return int(time_module.time() - self.start_time)
	
	def isPaused(self, time, frame, args):
		return False
	
	def setPaused(self, time, frame, args):
		self.paused = args[0]
	
	def hashPassword(self, time, frame, args):
		return ""
	
	def masterMode(self, time, frame, args):
		return self.mastermode
	
	def maxClients(self, time, frame, args):
		return self.max_clients
	
	def setMaxClients(self, time, frame, args):
		self.max_clients = args[0]
	
	def getVariable(self, time, frame, args):
		return self.variables[args[0]]
	
	def setVariable(self, time, frame, args):
		self.variables[args[0]] = args[1]
		
	def setRecordNextMatch(self, time, frame, args):
		self.recording_next_match = args[0]
	
	def requestPlayerAuth(self, time, frame, args):
		cn = args[0]
		desc = args[1]
		
		p = self.players[cn]
		
		orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_auth_request", (cn, p.name, desc)), waitFrames=5))
		
	def sendAuthChallenge(self, time, frame, args):
		cn = args[0]
		desc = args[1]
		reqId = args[2]
		publicKey = args[3]
		
		orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_auth_challenge_response", (cn, reqId, "foobarbaz")), waitFrames=10))
		
		return "foobarbaz"

	def setMap(self, time, frame, args):
		self.map = args[0]
		self.mode = args[1]
	
	def gameMode(self, time, frame, args):
		return self.mode
	
	def playerIsInvisible(self, time, frame, args):
		return self.players[args[0]].invisible
	
	def setInvisible(self, time, frame, args):
		self.players[args[0]].invisible = args[1]
		
	def playerIsSpectator(self, time, frame, args):
		return self.players[args[0]].spectating
	
	def spectate(self, time, frame, args):
		self.players[args[0]].spectating = True
	
	def unspectate(self, time, frame, args):
		self.players[args[0]].spectating = False
	
	def spectators(self, time, frame, args):
		return []
	
	def clients(self, time, frame, args):
		return self.players.keys()
	
	def playerName(self, time, frame, args):
		return self.players[args[0]].name
	
	def playerTeam(self, time, frame, args):
		return self.players[args[0]].team
		
	def playerIpLong(self, time, frame, args):
		return self.players[args[0]].ip
	
	def playerPrivilege(self, time, frame, args):
		return self.players[args[0]].privilege
	
	def playerMessage(self, time, frame, args):
		pass
	
	def sendMapInit(self, time, frame, args):
		pass
	
	def shutdown(self, time, frame, args):
		print "server.shutdown() called"
		#exit_status = args[0]
		#sys.exit(exit_status)
	
	#######################################################################################
	"""Macros for larger server events"""
	#######################################################################################
	
	def connectPlayer(self, player):
		self.players[player.cn] = player
		
		orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_connect_pre", (player.cn,)), waitFrames=0))
		orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_connect", (player.cn,)), waitFrames=5))
		
	def disconnectPlayer(self, player):
		orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_disconnect", (player.cn,)), waitFrames=0))
		orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_disconnect_post", (player.cn,)), waitFrames=5))
		
	def disconnectPlayerPost(self, cn):
		del self.players[cn]
		
class Player:
	def __init__(self, cn, name, team, ip, sessionId):
		self.cn = cn
		self.name = name
		self.team = team
		self.ip = ip
		self.sessionId = sessionId
		
		self.privilege = 0
		self.invisible = False
		self.frags = 0
		self.deaths = 0
		self.damage_spent = 0
		self.damage_dealt = 0
		self.shot_hits = 0
		
		self.spectating = False
		
server = Server()
	
orchestrator.addRequestHandler("isPaused", DataRequestHandler(server.isPaused))
orchestrator.addRequestHandler("setPaused", DataRequestHandler(server.setPaused))

orchestrator.addRequestHandler("getVariable", DataRequestHandler(server.getVariable))
orchestrator.addRequestHandler("setVariable", DataRequestHandler(server.setVariable))

orchestrator.addRequestHandler("setRecordNextMatch", DataRequestHandler(server.setRecordNextMatch))

orchestrator.addRequestHandler("instanceRoot", DataRequestHandler(server.instanceRoot))
orchestrator.addRequestHandler("setMap", DataRequestHandler(server.setMap))
orchestrator.addRequestHandler("uptime", DataRequestHandler(server.uptime))
orchestrator.addRequestHandler("hashPassword", DataRequestHandler(server.hashPassword))
orchestrator.addRequestHandler("gameMode", DataRequestHandler(server.gameMode))
orchestrator.addRequestHandler("masterMode", DataRequestHandler(server.masterMode))
orchestrator.addRequestHandler("clients", DataRequestHandler(server.clients))

orchestrator.addRequestHandler("playerIsSpectator", DataRequestHandler(server.playerIsSpectator))
orchestrator.addRequestHandler("spectate", DataRequestHandler(server.spectate))
orchestrator.addRequestHandler("unspectate", DataRequestHandler(server.unspectate))

orchestrator.addRequestHandler("playerIsInvisible", DataRequestHandler(server.playerIsInvisible))
orchestrator.addRequestHandler("setInvisible", DataRequestHandler(server.setInvisible))

orchestrator.addRequestHandler("setMaxClients", DataRequestHandler(server.setMaxClients))
orchestrator.addRequestHandler("maxClients", DataRequestHandler(server.maxClients))

orchestrator.addRequestHandler("playerPrivilege", DataRequestHandler(server.playerPrivilege))
orchestrator.addRequestHandler("playerTeam", DataRequestHandler(server.playerTeam))
orchestrator.addRequestHandler("sendMapInit", DataRequestHandler(server.sendMapInit))
orchestrator.addRequestHandler("playerMessage", DataRequestHandler(server.playerMessage))

orchestrator.addRequestHandler("spectators", DataRequestHandler(server.spectators))
orchestrator.addRequestHandler("playerName", DataRequestHandler(server.playerName))
orchestrator.addRequestHandler("playerIpLong", DataRequestHandler(server.playerIpLong))
orchestrator.addRequestHandler("requestPlayerAuth", DataRequestHandler(server.requestPlayerAuth))
orchestrator.addRequestHandler("sendAuthChallenge", DataRequestHandler(server.sendAuthChallenge))
orchestrator.addRequestHandler("shutdown", DataRequestHandler(server.shutdown))

import cxsbs
cxsbs.loadPlugins(cxsbsPath + "/plugins/")
