import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global flagTimingAuthority
		flagTimingAuthority = FlagTimingAuthority()
		
		Events.registerServerEventHandler('flag_taken', flagTimingAuthority.onTakeFlag)
		Events.registerServerEventHandler('flag_dropped', flagTimingAuthority.onFlagDropped)
		Events.registerServerEventHandler('flag_scored', flagTimingAuthority.onFlagScored)
		Events.registerServerEventHandler('flag_stopped', flagTimingAuthority.onFlagStopped)
		Events.registerServerEventHandler('flag_reset', flagTimingAuthority.onFlagReset)
		#Events.registerServerEventHandler('flag_spawned', flagTimingAuthority.onFlagReset)
		
		Events.registerServerEventHandler('map_changed', flagTimingAuthority.onMapChange)
		
		Events.registerServerEventHandler('player_frag', flagTimingAuthority.onFrag)
		
		Events.registerServerEventHandler('paused', flagTimingAuthority.onPause)
		Events.registerServerEventHandler('unpaused', flagTimingAuthority.onResume)
		
		Events.registerServerEventHandler('player_disconnect', flagTimingAuthority.onDisconnect)
		
	def unload(self):
		pass
	
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, func, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

import cxsbs
Colors = cxsbs.getResource("Colors")
Commands = cxsbs.getResource("Commands")
Game = cxsbs.getResource("Game")
Players = cxsbs.getResource("Players")
DatabaseManager = cxsbs.getResource("DatabaseManager")
Events = cxsbs.getResource("Events")
Timers = cxsbs.getResource("Timers")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Messages = cxsbs.getResource("Messages")
UserNames = cxsbs.getResource("UserNames")

import time

pluginCategory = "FlagTiming"

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="table_name", 
												displayName="Table name", 
												default="flagruntimes",
												doc="Table name for storing the clantag-group associations."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

pluginCategory = "FlagTiming"

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="thisRun", 
						displayName="This run", 
						default="Flag run ${green}completed${white} in ${blue}${recordTime}${white}", 
						doc="Message to print when a flag run finishes."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="overall", 
						displayName="Overall", 
						default="${green}${gameMode}${white} on ${orange}${gameMap}${white} as ${teamName}: ${green}${recordHolder}${white}: ${blue}${recordTime}${white}, split: ${split}", 
						doc="Message to print when a flag run finishes, showing overall records."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="notLogged", 
						displayName="Not logged", 
						default="${info}Please ${green}login${white} to set records.", 
						doc="Message to print when a flag run starts but a player is not loggged in.",
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="records", 
						displayName="Records", 
						default="${green}${gameMode}${white} on ${orange}${gameMap}${white} as ${teamName}: ${green}${recordHolder}${white}: ${blue}${recordTime}${white}", 
						doc="Message to print when a player requests the records for the map."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="loggedRecords", 
						displayName="Logged records", 
						default="${green}${gameMode}${white} on ${orange}${gameMap}${white} as ${teamName}: ${green}${recordHolder}${white}: ${blue}${recordTime}${white}, personal: ${recordTime}", 
						doc="Message to print when a player ...?."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="interrupted", 
						displayName="Interrupted", 
						default="Flag run ${red}interrupted${white}, no time will be recorded.", 
						doc="Message to print when a flag run is interrupted."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

Base = declarative_base()

class FlagRun(Base):
	__tablename__= tableSettings["table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer)
	gameMap = Column(String(128), nullable=False)
	gameMode = Column(Integer)
	team = Column(Integer)
	frags = Column(Integer)
	start = Column(Float)
	end = Column(Float)
	time = Column(Float)
	def __init__(self, userId, gameMap, gameMode, team, frags, start, end, time):
		self.userId = userId
		self.gameMap = gameMap
		self.gameMode = gameMode
		self.team = team
		self.frags = frags
		self.start = start
		self.end = end
		self.time = time
		
def getBestByMapModeTeam(gameMap, gameMode, team):
	session = DatabaseManager.dbmanager.session()
	try:
		return session.query(FlagRun).filter(FlagRun.gameMap==gameMap).filter(FlagRun.gameMode==gameMode).filter(FlagRun.team==team).order_by(FlagRun.time.asc()).first()
	finally:
		session.close()

def getUserBestByMapModeTeam(userId, gameMap, gameMode, team):
	session = DatabaseManager.dbmanager.session()
	try:
		return session.query(FlagRun).filter(FlagRun.userId==userId).filter(FlagRun.gameMap==gameMap).filter(FlagRun.gameMode==gameMode).filter(FlagRun.team==team).order_by(FlagRun.time.asc()).first()
	finally:
		session.close()
		
def timeFormat(time):
	s = ""
	s += str(round(time, 3)) + " s"	
	
	return s

def splitFormat(time):
	s = ""
	if time >= 0:
		s += Colors.red('+' + str(round(time, 3)) + " s")
	else:
		s += Colors.green(str(round(time, 3)) + " s")
	
	return s

def colorTeam(teamName):
	if teamName == "good":
		return Colors.blue(teamName)
	elif teamName == "evil":
		return Colors.red(teamName)
	else:
		return Colors.green(teamName)
		
class FlagTimingAuthority:
	def __init__(self):
		self.timedModes = [11, 12, 17]
	
		#store the details of all active flag runs by cn
		self.activeRuns = {}
		
		#store the status of the flags by team
		self.flagStatus = {0: "clean", 1: "clean", 2: "clean"}
		
	def reset(self):
		self.activeRuns = {}
		self.flagStatus = {0: "clean", 1: "clean", 2: "clean"}
		
	def clear(self, cn):
		if cn in self.activeRuns.keys():
			del self.activeRuns[cn]
			
	def commit(self, record):
		cn = record['cn']
		userId = record['userId']
		gameMap = record['gameMap']
		gameMode = record['gameMode']
		team = record['team']
		frags = record['frags']
		start = record['start']
		end = record['end']
		time = record['time']
		
		mapModeTeamBest = getBestByMapModeTeam(gameMap, gameMode, team)
		userMapModeTeamBest = None
		
		if userId != None:
			userMapModeTeamBest = getUserBestByMapModeTeam(userId, gameMap, gameMode, team)
	
			session = DatabaseManager.dbmanager.session()
			try:
				item = FlagRun(userId, gameMap, gameMode, team, frags, start, end, time)
				session.add(item)
				session.commit()
			finally:
				session.close()
				
		self.announce(cn, record, mapModeTeamBest, userMapModeTeamBest)
				
		
	def announce(self, cn, record, mapModeTeamBest, userMapModeTeamBest):
		cn = record['cn']
		userId = record['userId']
		gameMap = record['gameMap']
		gameMode = record['gameMode']
		team = record['team']
		frags = record['frags']
		start = record['start']
		end = record['end']
		time = record['time']
		
		if userId != None:
			publicName = UserNames.getDisplayName(userId)
		
		messager.sendMessage("thisRun", dictionary={"recordTime": timeFormat(time)})
		
		if mapModeTeamBest != None:
			previousHolder = UserNames.getDisplayName(mapModeTeamBest.userId)
			
			data = {
					"gameMap": gameMap,
					"gameMode": Game.modeName(gameMode),
					"teamName": colorTeam(Game.teamName(team)),
					"recordHolder": previousHolder,
					"recordTime": timeFormat(mapModeTeamBest.time),
					"split": splitFormat(time - mapModeTeamBest.time),
				}
		
			messager.sendPlayerMessage("overall", Players.player(cn), dictionary=data)
			
		
		if userMapModeTeamBest != None:
			data = {
					"gameMap": gameMap,
					"gameMode": Game.modeName(gameMode),
					"teamName": colorTeam(Game.teamName(team)),
					"recordHolder": "personal",
					"recordTime": timeFormat(userMapModeTeamBest.time),
					"split": splitFormat(time - userMapModeTeamBest.time),
				}
		
			messager.sendPlayerMessage("overall", Players.player(cn), dictionary=data)
		
	def onTakeFlag(self, cn, team):
		if not Game.currentMode() in self.timedModes:
			return
	
		if self.flagStatus[team] == "clean":
			self.flagStatus[team] = "taken"
		else:
			return
		
		try:
			p = Players.player(cn)
			userId = p.userId
		except AttributeError:
			userId = None
		except:
			return
		
		self.activeRuns[cn] = {
							"cn": cn,
							"userId": userId,
							"gameMap": Game.currentMap(),
							"gameMode": Game.currentMode(),
							"team": team, "frags": 0,
							"start": time.time(),
							"end": None,
							"time": -1
							}
	
	def onFlagDropped(self, cn, team):
		if not Game.currentMode() in self.timedModes:
			return
			
		self.flagStatus[team] = "dirty"
		self.clear(cn)
	
	def onFlagScored(self, cn, team):
		if not Game.currentMode() in self.timedModes:
			return
			
		self.flagStatus[team] = "clean"
		
		if cn in self.activeRuns.keys():
			self.activeRuns[cn]["end"] = time.time()
			self.activeRuns[cn]["time"] = self.activeRuns[cn]["end"] - self.activeRuns[cn]["start"]
			
			self.commit(self.activeRuns[cn])
		
		self.clear(cn)
	
	def onFlagStopped(self, cn, killerCn):
		if not Game.currentMode() in self.timedModes:
			return
			
		p = Players.player(cn)
		self.flagStatus[Game.teamNumber(p.team())] = "dirty"
		self.clear(cn)
	
	def onFlagReset(self, team):
		if not Game.currentMode() in self.timedModes:
			return
			
		self.flagStatus[team] = "clean"
		
	def onMapChange(self, gameMap, gameMode):
		if not Game.currentMode() in self.timedModes:
			return
		pass
		
	def onPause(self, cn):
		if not Game.currentMode() in self.timedModes:
			return
			
		pass
		
	def onResume(self, cn):
		if not Game.currentMode() in self.timedModes:
			return
			
		pass
		
	def onFrag(self, cn, tcn):
		if not Game.currentMode() in self.timedModes:
			return
			
		if cn in self.activeRuns.keys():
			p = Players.player(cn)
			t = Players.player(tcn)
			
			if p.team() != t.team():
				self.activeRuns[cn]["frags"] += 1
				
	def onDisconnect(self, cn):
		if not Game.currentMode() in self.timedModes:
			return
			
		self.clear(cn)

Base.metadata.create_all(DatabaseManager.dbmanager.engine)