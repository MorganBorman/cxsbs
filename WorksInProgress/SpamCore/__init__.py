import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
	
from xsbs.settings import PluginConfig
from xsbs.ui import error, notice, warning, info
from xsbs.players import player, playerPrivilege
from xsbs.events import registerServerEventHandler
from xsbs.ban import ban
from xsbs.mute import mute
from xsbs.spectate import spectate
from xsbs.colors import colordict
import sbserver
import time
import string

#returns the largest integer in a list
def maxInt(items):
	newlist = []
	
	for item in items:
		if type(item) == int:
			newlist.append(item)
			
	return max(newlist)

#helper function to convert all the string values in a dictionary to template strings
def templatize(dictionary):
	for key in dictionary.keys():
		dictionary[key] = string.Template(dictionary[key])
		
	return dictionary

class SpamHandler:
	def __init__(self, eventName, config):
		self.config = config
		self.config["messages"] = templatize(self.config["messages"])
		self.caseRegistry = {}
		self.totals = {}
		self.gameTotals = {}
		self.warningsGiven = {}
		
	def __call__(self, *args):
		cnFeild = self.config["cnFeild"]
		cn = args[cnFeild]
		
		if not cn in self.caseRegistry.keys():
			self.caseRegistry[cn] = []
			
		self.caseRegistry[cn].append(time.time())
		
		if not cn in self.totals.keys():
			self.totals[cn] = 0
			
		self.totals[cn] += 1
		
		if not cn in self.gameTotals.keys():
			self.gameTotals[cn] = 0
			
		self.gameTotals[cn] += 1
		
		self.checkForSpamming(cn)
		self.cleanUp()
		
	def cleanUp(self):
		largestInterval = maxInt(self.config["intervals"].keys())
	
		staleTime = time.time() - self.config["intervals"][largestInterval]
		
		for cn in self.warningsGiven.keys():
			tempList = []
			for warnTime in self.warningsGiven[cn]:
				if warnTime >= staleTime:
					tempList.append(warnTime)
			self.warningsGiven[cn] = tempList[:]
					
		warningStaleTime = time.time() - self.config["warningExpireTime"]
		
		for cn in self.caseRegistry.keys():
			tempList = []
			for entryTime in self.caseRegistry[cn]:
				if entryTime >= staleTime:
					tempList.append(entryTime)
			self.caseRegistry[cn] = tempList[:]
					
	def onDisconnect(self, cn):
		if cn in self.caseRegistry.keys():
			self.caseRegistry.pop(cn)
			
		if cn in self.gameTotals.keys():
			self.gameTotals.pop(cn)
			
		if cn in self.totals.keys():
			self.totals.pop(cn)
			
	def onNewGame(self):
		for cn in self.gameTotals.keys():
			self.gameTotals[cn] = 0
					
	def ban(self, cn, duration):
		#ban code goes here
		try:
			ban(cn, duration, self.config["action reason"], -1)
		except ValueError:
			#sbserver.message("Error: noNameSpam: Error while banning spamming player by cn" + str(cn))
			pass
		
	def spectate(self, cn, duration):
		#spectate code goes here
		try:
			spectate(cn, duration, self.config["action reason"], -1)
		except ValueError:
			#sbserver.message("Error: noNameSpam: Error while spectating spamming player by cn" + str(cn))
			pass
	
	def mute(self, cn, duration):
		#mute code goes here
		try:
			mute(cn, duration, self.config["action reason"], -1)
		except:
			#sbserver.message("Error: antiSpam: Failed mute player regarding spam. reason: player cn: " + str(cn) + " does not exist.")
			pass
		
	def action(self, cn, action):
		if action[0] == "ban":
			self.ban(cn, action[1])
		elif action[0] == "spectate":
			self.spectate(cn, action[1])
		elif action[0] == "mute":
			self.mute(cn, action[1])
		elif action[0] == "none":
			pass
		else:
			sbserver.message("Error: antiSpam: Failed take action against player regarding spam. reason: invalid configured action: " + str(action))
					
	def takeAction(self, cn, category):
		#sbserver.message(category + str(playerPrivilege(cn)))
		try:
			action = self.config["actions"][category][playerPrivilege(cn)]
		except:
			sbserver.message("Error: antiSpam: Failed take action against player regarding spam. reason: player cn: " + str(cn) + " does not exist.")
			return
			
		self.action(cn, action)

					
	def warn(self, cn):
		if cn in self.warningsGiven.keys():
			warningsLeft = self.config["maxWarnings"] - len(self.warningsGiven[cn])
			self.warningsGiven[cn].append(time.time())
		else:
			warningsLeft = self.config["maxWarnings"] - 1
			self.warningsGiven[cn] = [time.time()]
		
		if warningsLeft <= 0:
			self.takeAction(cn, "interval")
			return
			
		try:
			thePlayer = player(cn)
		except:
			sbserver.message("Error: antiSpam: Failed warn player regarding spam. reason: player cn: " + str(cn) + " does not exist.")
			return
	
		spamName = self.config["spamName"]
		messages = self.config["messages"]
		valueDictionary = dict(colordict)
		valueDictionary.update({"spamName": spamName, "playerName": thePlayer.name(), "warningsLeft": warningsLeft})
		
		#pull the messages out of the config for the various scenarios
		if thePlayer.isAdmin() and self.config["ignoreAdmins"]:
			if "admin" in messages.keys():
				message = messages["admin"].substitute(valueDictionary)
			else:
				sbserver.message("Error: antiSpam: No admin specific warning exists.")
				return
				
		elif thePlayer.isMaster() and self.config["ignoreMasters"]:
			if "master" in messages.keys():
				message = messages["master"].substitute(valueDictionary)
			else:
				sbserver.message("Error: antiSpam: No master specific warning exists.")
				return
				
		elif warningsLeft in messages.keys():
			message = messages[warningsLeft].substitute(valueDictionary)
			
		else:
			if "*" in messages.keys():
				message = messages["*"].substitute(valueDictionary)
			else:
				sbserver.message("Error: antiSpam: No generic warning exists.")
				return
		
		#warning code goes here
		try:
			thePlayer.message(warning(message))
		except:
			sbserver.message("Error: antiSpam: Failed send warning to player regarding spam. reason: player cn: " + str(cn) + " does not exist.")
			return
					
	def checkForSpamming(self, cn):
	
		#sbserver.message("checkForSpamming: " + self.config["spamName"] + ": " + str(cn))
	
		if cn in self.totals.keys() and self.config["intervals"]["totalMax"] != None:
			if self.totals[cn] > self.config["intervals"]["totalMax"]:
				self.takeAction(cn, "totalMax")
				return
			
		if cn in self.gameTotals.keys() and self.config["intervals"]["gameMax"] != None:
			if self.gameTotals[cn] > self.config["intervals"]["gameMax"]:
				self.takeAction(cn, "gameMax")
				return
				
		for interval in self.config["intervals"].keys():
			if type(interval) == int: #only use those intervals which represent seconds prior to the current message
				intervalAge = time.time() - interval
				intervalMax = self.config["intervals"][interval]
				
				if cn in self.caseRegistry.keys():
					intervalOccurances = 0
		
					for timeValue in self.caseRegistry[cn]:
						if timeValue > intervalAge:
							intervalOccurances += 1
			
					if intervalOccurances > intervalMax:
						self.warn(cn)
						return
				
		

class SpamManager:
	def __init__(self):
		self.spamTypes = []		
			
	def addSpamType(self, eventName, config):
		spamHandler = SpamHandler(eventName, config)
		self.spamTypes.append(spamHandler)
		registerServerEventHandler(eventName, spamHandler)
		
	def onDisconnect(self, cn):
		for spamType in self.spamTypes:
			spamType.onDisconnect(cn)
			
	def onNewGame(self):
		for spamType in self.spamTypes:
			spamType.onNewGame()

spamManager = SpamManager()

registerServerEventHandler("player_disconnect", spamManager.onDisconnect)
		
