import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, func
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

from xsbs.users.displaynames import getDisplayNameByUser
from xsbs.events import registerServerEventHandler
from xsbs.game import currentMap, currentMode, modeName, teamNumber, teamName
from xsbs.players import player
from xsbs.settings import PluginConfig
import time

from xsbs.MessagingFramework import MessagingModule

config = PluginConfig('dbtables')
tablename = config.getOption('FlagTiming', 'tablename', 'flagtimetrial')
del config

messageModule = MessagingModule(config="flagtiming")
messageModule.addMessage("thisRun", "Flag run ${green}completed${white} in ${blue}${recordTime}${white}")
messageModule.addMessage("overall", "${green}${gameMode}${white} on ${orange}${gameMap}${white} as ${teamName}: ${green}${recordHolder}${white}: ${blue}${recordTime}${white}, split: ${split}")
messageModule.addMessage("notLogged", "Please login to set records.")

messageModule.addMessage("records", "${green}${gameMode}${white} on ${orange}${gameMap}${white} as ${teamName}: ${green}${recordHolder}${white}: ${blue}${recordTime}${white}")
messageModule.addMessage("loggedRecords", "${green}${gameMode}${white} on ${orange}${gameMap}${white} as ${teamName}: ${green}${recordHolder}${white}: ${blue}${recordTime}${white}, personal: ${recordTime}")

messageModule.addMessage("interrupted", "flag run ${red}interrupted${white}, no time will be recorded.")

messageModule.finalize()

Base = declarative_base()

class FlagRun(Base):
	__tablename__= tablename
	id = Column(Integer, primary_key=True)
	userId = Column(Integer)
	gameMap = Column(String(128), nullable=False)
	gameMode = Column(Integer)
	team = Column(Integer)
	frags = Column(Integer)
	start = Column(Integer)
	end = Column(Integer)
	time = Column(Integer)
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
		return blue(teamName)
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
			publicName = getDisplayNameByUser(userId)
		
		messageModule.sendMessage("thisRun", dictionary={"recordTime": timeFormat(time)})
		
		if mapModeTeamBest != None:
			previousHolder = getDisplayNameByUser(mapModeTeamBest.userId)
			
			data = {
					"gameMode": gameMap,
					"gameMap": modeName(gameMode),
					"teamName": colorTeam(teamName(team)),
					"recordHolder": previousHolder,
					"recordTime": timeFormat(mapModeTeamBest.time),
					"split": splitFormat(time - mapModeTeamBest.time),
				}
		
			messageModule.sendMessage("overall", dictionary=data)
			
		
		if userMapModeTeamBest != None:
			data = {
					"gameMode": gameMap,
					"gameMap": modeName(gameMode),
					"teamName": colorTeam(teamName(team)),
					"recordHolder": "personal",
					"recordTime": timeFormat(mapModeTeamBest.time),
					"split": splitFormat(time - mapModeTeamBest.time),
				}
		
			messageModule.sendMessage("overall", dictionary=data)
		
	def onTakeFlag(self, cn, team):
		if not currentMode() in self.timedModes:
			return
	
		if self.flagStatus[team] == "clean":
			self.flagStatus[team] = "taken"
		else:
			return
		
		try:
			p = player(cn)
			userId = p.user.id
		except AttributeError:
			userId = None
		except:
			return
		
		self.activeRuns[cn] = {
							"cn": cn,
							"userId": userId,
							"gameMap": currentMap(),
							"gameMode": currentMode(),
							"team": team, "frags": 0,
							"start": time.time(),
							"end": None,
							"time": -1
							}
	
	def onFlagDropped(self, cn, team):
		if not currentMode() in self.timedModes:
			return
			
		self.flagStatus[team] = "dirty"
		self.clear(cn)
	
	def onFlagScored(self, cn, team):
		if not currentMode() in self.timedModes:
			return
			
		self.flagStatus[team] = "clean"
		
		if cn in self.activeRuns.keys():
			self.activeRuns[cn]["end"] = time.time()
			self.activeRuns[cn]["time"] = self.activeRuns[cn]["end"] - self.activeRuns[cn]["start"]
			
			self.commit(self.activeRuns[cn])
		
		self.clear(cn)
	
	def onFlagStopped(self, cn, killerCn):
		if not currentMode() in self.timedModes:
			return
			
		p = player(cn)
		self.flagStatus[teamNumber(p.team())] = "dirty"
		self.clear(cn)
	
	def onFlagReset(self, team):
		if not currentMode() in self.timedModes:
			return
			
		self.flagStatus[team] = "clean"
		
	def onMapChange(self, gameMap, gameMode):
		if not currentMode() in self.timedModes:
			return
		pass
		
	def onPause(self, cn):
		if not currentMode() in self.timedModes:
			return
			
		pass
		
	def onResume(self, cn):
		if not currentMode() in self.timedModes:
			return
			
		pass
		
	def onFrag(self, cn, tcn):
		if not currentMode() in self.timedModes:
			return
			
		if cn in self.activeRuns.keys():
			p = player(cn)
			t = player(tcn)
			
			if p.team() != t.team():
				self.activeRuns[cn]["frags"] += 1
				
	def onDisconnect(self, cn):
		if not currentMode() in self.timedModes:
			return
			
		self.clear(cn)		
		
flagTimingAuthority = FlagTimingAuthority()

registerServerEventHandler('flag_taken', flagTimingAuthority.onTakeFlag)
registerServerEventHandler('flag_dropped', flagTimingAuthority.onFlagDropped)
registerServerEventHandler('flag_scored', flagTimingAuthority.onFlagScored)
registerServerEventHandler('flag_stopped', flagTimingAuthority.onFlagStopped)
registerServerEventHandler('flag_reset', flagTimingAuthority.onFlagReset)
#registerServerEventHandler('flag_spawned', flagTimingAuthority.onFlagReset)

registerServerEventHandler('map_changed', flagTimingAuthority.onMapChange)

registerServerEventHandler('player_frag', flagTimingAuthority.onFrag)

registerServerEventHandler('paused', flagTimingAuthority.onPause)
registerServerEventHandler('unpaused', flagTimingAuthority.onResume)

registerServerEventHandler('player_disconnect', flagTimingAuthority.onDisconnect)

Base.metadata.create_all(DatabaseManager.dbmanager.engine)