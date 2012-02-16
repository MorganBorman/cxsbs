class OrchestratorContainer:
	def __init__(self):
		self.orchestrator = None
	
	def setOrchestrator(self, orchestrator):
		self.orchestrator = orchestrator
		
orchestratorContainer = OrchestratorContainer()

def reinitializeHandlers():
	return orchestratorContainer.orchestrator.request("reinitializeHandlers", ())

def getVariable(name):
	return orchestratorContainer.orchestrator.request("getVariable", (name,))

def setVariable(name, value):
	return orchestratorContainer.orchestrator.request("setVariable", (name, value))

def setClientVariable(name, value):
	return orchestratorContainer.orchestrator.request("setClientVariable", (name, value))

def numClients():
	return orchestratorContainer.orchestrator.request("numClients", ())
	
def message(text):
	return orchestratorContainer.orchestrator.request("message", (text,))
	
def sendMapInit(cn):
	return orchestratorContainer.orchestrator.request("sendMapInit", (cn,))
	
def sendEditMap(cn, data):
	return orchestratorContainer.orchestrator.request("sendEditMap", (cn, data))
	
def clients():
	return orchestratorContainer.orchestrator.request("clients", ())
	
def players():
	return orchestratorContainer.orchestrator.request("players", ())
	
def spectators():
	return orchestratorContainer.orchestrator.request("spectators", ())
	
def playerMessage(cn, text):
	return orchestratorContainer.orchestrator.request("playerMessage", (cn, text))
	
def playerMessageAll(cn, text):
	return orchestratorContainer.orchestrator.request("playerMessageAll", (cn, text))
	
def playerMessageTeam(cn, text):
	return orchestratorContainer.orchestrator.request("playerMessageTeam", (cn, text))
	
def playerName(cn):
	return orchestratorContainer.orchestrator.request("playerName", (cn,))
	
def playerSessionId(cn):
	return orchestratorContainer.orchestrator.request("playerSessionId", (cn,))
	
def playerIpLong(cn):
	return orchestratorContainer.orchestrator.request("playerIpLong", (cn,))

def playerPrivilege(cn):
	return orchestratorContainer.orchestrator.request("playerPrivilege", (cn,))

def playerFrags(cn):
	return orchestratorContainer.orchestrator.request("playerFrags", (cn,))
	
def playerTeamkills(cn):
	return orchestratorContainer.orchestrator.request("playerTeamkills", (cn,))
	
def playerDeaths(cn):
	return orchestratorContainer.orchestrator.request("playerDeaths", (cn,))
	
def playerShots(cn):
	return orchestratorContainer.orchestrator.request("playerShots", (cn,))
	
def playerHits(cn):
	return orchestratorContainer.orchestrator.request("playerHits", (cn,))

def playerPing(cn):
	return orchestratorContainer.orchestrator.request("playerPing", (cn,))
	
def playerScore(cn):
	return orchestratorContainer.orchestrator.request("playerScore", (cn,))

def playerDamageDealt(cn):
	return orchestratorContainer.orchestrator.request("playerDamageDealt", (cn,))
	
def playerDamageReceived(cn):
	return orchestratorContainer.orchestrator.request("playerDamageReceived", (cn,))

def playerTeam(cn):
	return orchestratorContainer.orchestrator.request("playerTeam", (cn,))
	
def playerIsSpectator(cn):
	return orchestratorContainer.orchestrator.request("playerIsSpectator", (cn,))
	
def playerIsInvisible(cn):
	return orchestratorContainer.orchestrator.request("playerIsInvisible", (cn,))

def playerMapCrc(cn):
	return orchestratorContainer.orchestrator.request("playerMapCrc", (cn,))
	
def playerMapName(cn):
	return orchestratorContainer.orchestrator.request("playerMapName", (cn,))
	
def playerKick(cn):
	return orchestratorContainer.orchestrator.request("playerKick", (cn,))
	
def playerDisc(cn):
	return orchestratorContainer.orchestrator.request("playerDisc", (cn,))
	
def requestPlayerAuth(cn, desc):
	return orchestratorContainer.orchestrator.request("requestPlayerAuth", (cn, desc))

def sendAuthChallenge(cn, desc, reqId, publicKey):
	return orchestratorContainer.orchestrator.request("sendAuthChallenge", (cn, desc, reqId, publicKey))
	
def setInvisible(cn):
	return orchestratorContainer.orchestrator.request("setInvisible", (cn,))
	
def setVisible(cn):
	return orchestratorContainer.orchestrator.request("setVisible", (cn,))
	
def spectate(cn):
	return orchestratorContainer.orchestrator.request("spectate", (cn,))
	
def unspectate(cn):
	return orchestratorContainer.orchestrator.request("unspectate", (cn,))
	
def setPlayerTeam(cn, team):
	return orchestratorContainer.orchestrator.request("setPlayerTeam", (cn,team))
	
def setBotLimit(number):
	return orchestratorContainer.orchestrator.request("setBotLimit", (number,))
	
def hashPassword(cn, password):
	return orchestratorContainer.orchestrator.request("hashPassword", (cn,password))
	
def setMaster(cn):
	return orchestratorContainer.orchestrator.request("setMaster", (cn,))
	
def setAdmin(cn):
	return orchestratorContainer.orchestrator.request("setAdmin", (cn,))
	
def resetPrivilege(cn):
	return orchestratorContainer.orchestrator.request("resetPrivilege", (cn,))
	
def setPaused(value):
	return orchestratorContainer.orchestrator.request("setPaused", (value,))
	
def isPaused():
	return orchestratorContainer.orchestrator.request("isPaused", ())
	
def setMap(gameMap, gameMode):
	return orchestratorContainer.orchestrator.request("setMap", (gameMap, gameMode))
	
def setMasterMode(cn):
	return orchestratorContainer.orchestrator.request("setMasterMode", (cn,))
	
def masterMode():
	return orchestratorContainer.orchestrator.request("masterMode", ())
	
def setMasterMask(mask):
	return orchestratorContainer.orchestrator.request("setMasterMask", (mask,))
	
def gameMode():
	return orchestratorContainer.orchestrator.request("gameMode", ())
	
def mapName():
	return orchestratorContainer.orchestrator.request("mapName", ())
	
def modeName():
	return orchestratorContainer.orchestrator.request("modeName", ())
	
def maxClients():
	return orchestratorContainer.orchestrator.request("maxClients", ())
	
def setMaxClients(number):
	return orchestratorContainer.orchestrator.request("setMaxClients", (number,))
	
def uptime():
	return orchestratorContainer.orchestrator.request("uptime", ())
	
def ip():
	return orchestratorContainer.orchestrator.request("ip", ())
	
def port():
	return orchestratorContainer.orchestrator.request("port", ())

def reload():
	return orchestratorContainer.orchestrator.request("reload", ())

def authChallenge(n1, n2, string):
	return orchestratorContainer.orchestrator.request("authChallenge", (n1, n2, string))
	
def sendMapReload():
	return orchestratorContainer.orchestrator.request("sendMapReload", ())

def setSecondsRemaining(secs):
	return orchestratorContainer.orchestrator.request("setSecondsRemaining", (secs,))

def secondsRemaining(secs):
	return orchestratorContainer.orchestrator.request("secondsRemaining", (secs,))

def persistentIntermission():
	return orchestratorContainer.orchestrator.request("persistentIntermission", ())

def setPersistentIntermission(value):
	return orchestratorContainer.orchestrator.request("setPersistentIntermission", (value,))

def allowShooting():
	return orchestratorContainer.orchestrator.request("allowShooting", ())

def setAllowShooting(value):
	return orchestratorContainer.orchestrator.request("setAllowShooting", (value,))
	
def adminPassword():
	return orchestratorContainer.orchestrator.request("adminPassword", ())
	
def publicServer():
	return orchestratorContainer.orchestrator.request("publicServer", ())
	
def sendMapReload():
	return orchestratorContainer.orchestrator.request("sendMapReload", ())
	
def setTeam(cn, team):
	return orchestratorContainer.orchestrator.request("setTeam", (cn, team))
	
def pregameSetTeam(cn, team):
	return orchestratorContainer.orchestrator.request("pregameSetTeam", (cn, team))
	
def teamScore(team):
	return orchestratorContainer.orchestrator.request("teamScore", (team,))
	
def nextMatchRecorded():
	return orchestratorContainer.orchestrator.request("nextMatchRecorded", ())
	
def setRecordNextMatch(value):
	return orchestratorContainer.orchestrator.request("setRecordNextMatch", (value,))
	
def demoSize(demoNum):
	return orchestratorContainer.orchestrator.request("demoSize", (demoNum,))
	
def demoData(demoNum):
	return orchestratorContainer.orchestrator.request("demoData", (demoNum,))
	
def sendDemo(cn, demoNum):
	return orchestratorContainer.orchestrator.request("sendDemo", (cn, demoNum))
	
def saveDemoFile(path):
	return orchestratorContainer.orchestrator.request("saveDemoFile", (path,))
	
def suicide(cn):
	return orchestratorContainer.orchestrator.request("suicide", (cn,))
	
def instanceRoot():
	return orchestratorContainer.orchestrator.request("instanceRoot", ())

def shutdown(status):
	return orchestratorContainer.orchestrator.request("shutdown", (status,))