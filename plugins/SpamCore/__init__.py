import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global spamManager
		spamManager = SpamManager()
					
		Events.registerAllEventHandler(spamManager.all_event_handler)
		Events.registerServerEventHandler("player_disconnect", spamManager.onDisconnect)
		Events.registerServerEventHandler("map_changed", spamManager.onNewGame)
		
	def unload(self):
		pass
	
import time
	
import cxsbs
MuteCore = cxsbs.getResource("MuteCore")
BanCore = cxsbs.getResource("BanCore")
SpectCore = cxsbs.getResource("SpectCore")
Messages = cxsbs.getResource("Messages")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Logging = cxsbs.getResource("Logging")
Events = cxsbs.getResource("Events")
ServerCore = cxsbs.getResource("ServerCore")
Players = cxsbs.getResource("Players")

pluginCategory = "Spam"

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="spam_warning", 
						displayName="Spam warning", 
						default="${warning}This server is ${red}${type}${white} intolerant!", 
						doc="Message to print when a player is spamming."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

class SpamHandler:
	def __init__(self, eventName):
		self.settings = SettingsManager.getAccessor(pluginCategory, eventName + "_spam_protection")
		
		SettingsManager.addSetting(Setting.BoolSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="enabled", 
														displayName="Enabled", 
														default=False,
														doc="Should this event be spam protected? Only enabled this for events which have a cn as the first argument."
													))
		
		SettingsManager.addSetting(Setting.Setting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="type_name", 
														displayName="Type name", 
														default="Spam",
														doc="What should this type of spam be referred to in warnings, and action reasons."
													))
		
		SettingsManager.addSetting(Setting.BoolSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="use_ips", 
														displayName="Use ips", 
														default=False,
														doc="Should this spam be tracked and enforced using ip's rather than cn's?."
													))
		
		SettingsManager.addSetting(Setting.IntSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="warnings", 
														displayName="Warnings", 
														default=3,
														doc="How many warnings should an offending player receive before action is taken."
													))
		
		SettingsManager.addSetting(Setting.IntSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="warning_expiration", 
														displayName="Warning expiration", 
														default=60,
														doc="How many seconds before warnings expire."
													))
		
		SettingsManager.addSetting(Setting.ListSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="intervals", 
														displayName="Intervals", 
														default=[],
														doc="What intervals should the spam protection be triggered by. Use the format \"time:max,time:max\""
													))
		
		SettingsManager.addSetting(Setting.IntSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="max_per_game", 
														displayName="Max per game", 
														default=0,
														doc="Max occurrences per game. zero to disable."
													))
		
		SettingsManager.addSetting(Setting.IntSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="max_per_connection", 
														displayName="Max per connection", 
														default=0,
														doc="Max occurrences per connection. zero to disable."
													))
		
		SettingsManager.addSetting(Setting.IntSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="total_max", 
														displayName="Total_max", 
														default=0,
														doc="Max total occurrences. Same as max_per_connection if use_ips is enabled. Zero to disable."
													))
		
		SettingsManager.addSetting(Setting.Setting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="action", 
														displayName="Action", 
														default="",
														doc="What action should be taken when the max warnings are exceeded. Valid actions are; ban, mute, and spectate. Leave blank to disable taking action."
													))
		
		SettingsManager.addSetting(Setting.IntSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="action_duration", 
														displayName="Action duration", 
														default=450,
														doc="Duration for which an action should persist. ie how long should a player be banned muted or spectated."
													))
		
		SettingsManager.addSetting(Setting.ListSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="exempt_groups", 
														displayName="Exempt groups", 
														default=['__admin__'],
														doc="Which groups should be exempt from this spam protection."
													))
		
		SettingsManager.addSetting(Setting.ListSetting	(
														category=pluginCategory, 
														subcategory=eventName + "_spam_protection", 
														symbolicName="unexempt_groups", 
														displayName="Unexempt groups", 
														default=[],
														doc="Which groups should be unexempt from this spam protection."
													))
		
		self.occurrences = {}
		self.gameOccurrences = {}
		self.totalOccurrences = {}
		self.connectionOccurrences = {}
		self.warningsGiven = {}
		
	def handle(self, args):
		if not self.settings['enabled']:
			return
		
		try:
			cn = args[0]
			if self.settings['use_ips']:
				key = ServerCore.playerIpLong(cn)
			else:
				key = cn
		except ValueError:
			return #TODO log spam triggered for invalid player
		except IndexError:
			return #TODO log invalid spam type
		
		try:
			self.occurrences[key].append(time.time())
		except KeyError:
			self.occurrences[key] = [time.time()]
		
		try:
			self.gameOccurrences[key] += 1
		except KeyError:
			self.gameOccurrences[key] = 1
			
		try:
			self.totalOccurrences[key] += 1
		except KeyError:
			self.totalOccurrences[key] = 1
			
		try:
			self.connectionOccurrences[key] += 1
		except KeyError:
			self.connectionOccurrences[key] = 1
			
		self.checkForSpamming(cn, key)
		self.cleanup()
		
	def getIntervals(self):
		intervals = self.settings['intervals']
		
		intervalDict = {}
		
		def getKeyValue(intervalString):
			pair = map(int, intervalString.split(':'))
			return {pair[0]:pair[1]}
		
		map(intervalDict.update, map(getKeyValue, intervals))
		
		return intervalDict
		
	def checkForSpamming(self, cn, key):
		if key in self.totalOccurrences.keys() and self.settings['total_max'] != 0:
			if self.totalOccurrences[key] >= self.settings['total_max']:
				self.takeAction(cn, key)
			elif self.totalOccurrences[key] >= 0.75*self.settings['total_max']:
				self.warn(cn, key)
				
		if key in self.connectionOccurrences.keys() and self.settings['max_per_connection'] != 0:
			if self.connectionOccurrences[key] >= self.settings['max_per_connection']:
				self.takeAction(cn, key)
			elif self.connectionOccurrences[key] >= 0.75*self.settings['max_per_connection']:
				self.warn(cn, key)
				
		if key in self.gameOccurrences.keys() and self.settings['max_per_game'] != 0:
			if self.gameOccurrences[key] >= self.settings['max_per_game']:
				self.takeAction(cn, key)
			elif self.gameOccurrences[key] >= 0.75*self.settings['max_per_game']:
				self.warn(cn, key)
				
		intervals = self.getIntervals()
		
		for interval in intervals.keys():
			intervalAge = time.time() - interval
			intervalMax = intervals[interval]
			
			if key in self.occurrences.keys():
				intervalOccurrences = 0
	
				for timeValue in self.occurrences[key]:
					if timeValue > intervalAge:
						intervalOccurrences += 1
		
				if intervalOccurrences > intervalMax:
					self.warn(cn, key)
					return
	
	def cleanup(self):
		intervals = self.getIntervals()
		largestInterval = max(intervals.keys())
		
		staleTime = time.time() - intervals[largestInterval]
		warningStaleTime = time.time() - self.settings["warning_expiration"]
		
		for key in self.occurrences.keys():
			tempList = []
			for item in self.occurrences[key]:
				if item > staleTime:
					tempList.append(item)
			self.occurrences[key] = tempList[:]
			
		for key in self.warningsGiven.keys():
			tempList = []
			for item in self.warningsGiven[key]:
				if item > staleTime:
					tempList.append(item)
			self.warningsGiven[key] = tempList[:]
	
	def onDisconnect(self, cn):
		if self.settings['use_ips']:
			try:
				key = ServerCore.playerIpLong(args[0])
				del self.connectionOccurrences[key]
			except:
				pass
			return
		else:
			if cn in self.connectionOccurrences.keys():
				del self.connectionOccurrences[cn]
		
		if cn in self.occurrences.keys():
			del self.occurrences[cn]
			
		if cn in self.gameOccurrences.keys():
			del self.gameOccurrences[cn]
		
		if cn in self.totalOccurrences.keys():
			del self.totalOccurrences[cn]
	
	def onNewGame(self):
		for cn in self.gameOccurrences.keys():
			self.gameOccurrences[cn] = 0
			
	def warn(self, cn, key):
		if key in self.warningsGiven.keys():
			warningsLeft = self.settings['warnings'] - len(self.warningsGiven[key])
			
			if warningsLeft <= 0:
				self.takeAction(cn, key)
				return
		
		try:
			p = Players.player(cn)
		except ValueError:
			return 
		
		messager.sendPlayerMessage('spam_warning', p, dictionary={'type': self.settings['type_name']})
		try:
			self.warningsGiven[key].append(time.time())
		except KeyError:
			self.warningsGiven[key] = [time.time()]
		
	def takeAction(self, cn, key):
		action = self.settings['action']
		reason = self.settings['type_name']
		duration = self.settings['action_duration']
		
		if action == "ban":
			BanCore.addBan(cn, duration, reason)
		elif action == "spectate":
			SpectCore.addSpect(cn, duration, reason)
		elif action == "mute":
			MuteCore.addMute(cn, duration, reason)
		elif action == "":
			pass
		else:
			Logging.error("Failed take action against player regarding spam of type: " + self.settings['type_name'] + ". reason: invalid configured action: " + str(action))

class SpamManager:
	def __init__(self):
		self.spamEvents = {}
		self.initializeEvents()
		
	def initializeEvents(self):
		for eventName in playerActionEvents:
			self.spamEvents[eventName] = SpamHandler(eventName)
		
	def all_event_handler(self, eventName, args):
		if eventName in self.spamEvents.keys():
			try:
				self.spamEvents[eventName].handle(args)
			except:
				pass
		
	def onDisconnect(self, cn):
		for spamHandler in self.spamEvents.values():
			spamHandler.onDisconnect(cn)
			
	def onNewGame(self, gameMap, gameMode):
		for spamHandler in self.spamEvents.values():
			spamHandler.onNewGame()
			
#a list of events for which the first argument is the cn and which are caused by a player's actions
playerActionEvents = [
						"player_teamkill",
						"player_spectated",
						"player_unspectated",
						"player_disconnect",
						"player_uploaded_map",
						"player_connect",
						"player_message",
						"player_message_team",
						"player_name_changed",
						"player_map_vote",
						"player_set_mastermode",
						"player_request_spectate",
						"player_request_unspectate",
						"player_set_team",
						"player_get_map",
						"player_setmaster",
						"player_setmaster_off",
						"player_auth_request",
						"player_pause",
						"flag_dropped",
						"flag_scored",
						"flag_taken",
					]