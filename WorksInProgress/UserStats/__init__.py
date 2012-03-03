import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):

		self.statWriter = StatWriter()
		self.statWriter.start()
		
		Events.registerServerEventHandler('player_teamkill', self.statWriter.on_teamkill)
		Events.registerServerEventHandler('player_frag', self.statWriter.on_frag)
		Events.registerServerEventHandler('player_suicide', self.statWriter.on_suicide)
		Events.registerServerEventHandler('player_spend_damage', self.statWriter.on_shot)
		Events.registerServerEventHandler('player_inflict_damage', self.statWriter.on_hit)
		Events.registerServerEventHandler('player_connect', self.statWriter.on_connect)
		Events.registerServerEventHandler('player_disconnect', self.statWriter.on_disconnect)
		
	def unload(self):
		self.statWriter.stop()

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import func

import time, threading

Base = declarative_base()

import cxsbs
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Users = cxsbs.getResource("Users")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Messages = cxsbs.getResource("Messages")
Game = cxsbs.getResource("Game")
DatabaseManager = cxsbs.getResource("DatabaseManager")
ServerCore = cxsbs.getResource("ServerCore")

pluginCategory = "UserStats"

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="damage_spent_event_table_name", 
												displayName="Damage Spent Event Table name", 
												default="usermanager_damage_spent_events",
												doc="Table name for storing the user stats."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="damage_dealt_event_table_name", 
												displayName="Damage Dealt Event Table name", 
												default="usermanager_damage_dealt_events",
												doc="Table name for storing the user stats."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="frag_event_table_name", 
												displayName="Frag Event Table name", 
												default="usermanager_frag_events",
												doc="Table name for storing the user stats."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="death_event_table_name", 
												displayName="Death Event Table name", 
												default="usermanager_death_events",
												doc="Table name for storing the user stats."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="connections_table_name", 
												displayName="Connections Table name", 
												default="usermanager_connection_history",
												doc="Table name for storing the time periods that the user is on the server."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='awards_main', 
						displayName='Awards main', 
						default="${blue}Awards: ${white}${most_frags} ${most_teamkills} ${most_deaths} ${most_kpd} ${most_accuracy}",
						doc="Main awards template."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
		
NOTUSER = -1

class DamageSpentEvent(Base):
	"each Damage spent event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["damage_spent_event_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	gun = Column(Integer)
	amount = Column(Integer)
	
	def __init__(self, userId, timestamp, mode, gun, amount):
		self.userId = userId
		self.timestamp = timestamp
		self.mode = mode
		self.gun = gun
		self.amount = amount

class DamageDealtEvent(Base):
	"each damage dealt event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["damage_dealt_event_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	gun = Column(Integer)
	amount = Column(Integer)
	
	def __init__(self, userId, timestamp, mode, gun, amount):
		self.userId = userId
		self.timestamp = timestamp
		self.mode = mode
		self.gun = gun
		self.amount = amount
	
TEAMKILL = -2
		
class FragEvent(Base):
	"each frag event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["frag_event_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	targetId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	
	def __init__(self, userId, targetId, timestamp, mode):
		self.userId = userId
		self.targetId = targetId
		self.timestamp = timestamp
		self.mode = mode
	
SUICIDE = -3

class DeathEvent(Base):
	"each death event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["death_event_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	causeId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	
	def __init__(self, userId, causeId, timestamp, mode):
		self.userId = userId
		self.causeId = causeId
		self.timestamp = timestamp
		self.mode = mode
		
class UserConnection(Base):
	"each death event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["connections_table_name"]
	id = Column(Integer, primary_key=True)
	userId = Column(Integer, index=True)
	connect_timestamp = Column(BigInteger, index=True)
	disconnect_timestamp = Column(BigInteger, index=True)
	
	def __init__(self, userId, connect_timestamp, disconnect_timestamp):
		self.userId = userId
		self.connect_timestamp = connect_timestamp
		self.disconnect_timestamp = disconnect_timestamp
		
Base.metadata.create_all(DatabaseManager.dbmanager.engine)

def get_timestamp():
	"Get the current timestamp: the time since epoch in seconds."
	return time.time()

def get_gamemode():
	"Get the current gamemode as its integer representation."
	return Game.currentMode()
		
class StatWriter(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.running = True
		
		self.event_queue = []
		self.flag = threading.Event()
		
		self.max_queue_size = 0
		
	def run(self):
		while self.running or len(self.event_queue) > 0:
			
			self.flag.clear()
			self.flag.wait()
			
			queue_size = len(self.event_queue)
			while queue_size > 0:
				
				if queue_size > self.max_queue_size:
					self.max_queue_size = queue_size
					#print "Hit new max queue size of: %d" % queue_size
				
				event = self.event_queue.pop(0)
				#do something with it
				try:
					event[0](*(event[1]))
				except:
					pass
				
				queue_size = len(self.event_queue)
				
		print "The StatWriter thread hit a max queue size of %d" % self.max_queue_size
				
	def stop(self):
		self.running = False
		self.flag.set()
		
	def on_teamkill(self, cn, tcn):
		if not Users.isLoggedIn(cn):
			teamkillerId = NOTUSER
		else:
			user = Players.player(cn)
			teamkillerId = user.userId
					
		if not Users.isLoggedIn(tcn):
			teamkilleeId = NOTUSER
		else:
			tuser = Players.player(tcn)
			teamkilleeId = tuser.userId
			
		timestamp = get_timestamp()
		mode = get_gamemode()
		
		if teamkillerId != NOTUSER:
			self.event_queue.append((on_frag, (teamkillerId, TEAMKILL, timestamp, mode)))
			self.flag.set()
			
		if teamkilleeId != NOTUSER:
			self.event_queue.append((on_death, (teamkilleeId, TEAMKILL, timestamp, mode)))
			self.flag.set()
	
	def on_frag(self, cn, tcn):
		if not Users.isLoggedIn(cn):
			killerId = NOTUSER
		else:
			user = Players.player(cn)
			killerId = user.userId
					
		if not Users.isLoggedIn(tcn):
			killeeId = NOTUSER
		else:
			tuser = Players.player(tcn)
			killeeId = tuser.userId
			
		timestamp = get_timestamp()
		mode = get_gamemode()
		
		if killerId != NOTUSER:
			self.event_queue.append((on_frag, (killerId, killeeId, timestamp, mode)))
			self.flag.set()
			
		if killeeId != NOTUSER:
			self.event_queue.append((on_death, (killeeId, killerId, timestamp, mode)))
			self.flag.set()
	
	def on_suicide(self, cn):
		if not Users.isLoggedIn(cn):
			return
		else:
			timestamp = get_timestamp()
			mode = get_gamemode()
			user = Players.player(cn)
			self.event_queue.append((on_death, (user.userId, SUICIDE, timestamp, mode)))
			self.flag.set()
	
	def on_shot(self, cn, gun, damage):
		if not Users.isLoggedIn(cn):
			return
		else:
			timestamp = get_timestamp()
			mode = get_gamemode()
			user = Players.player(cn)
			self.event_queue.append((on_shot, (user.userId, timestamp, mode, gun, damage)))
			self.flag.set()
	
	def on_hit(self, cn, gun, damage):
		if not Users.isLoggedIn(cn):
			return
		else:
			timestamp = get_timestamp()
			mode = get_gamemode()
			user = Players.player(cn)
			self.event_queue.append((on_hit, (user.userId, timestamp, mode, gun, damage)))
			self.flag.set()
		
	def on_connect(self, cn):
		p = Players.player(cn)
		p.connect_timestamp = get_timestamp()
	
	def on_disconnect(self, cn):
		if not Users.isLoggedIn(cn):
			return
		else:
			user = Players.player(cn)
			self.event_queue.append((on_disconnect, (user.userId, user.connect_timestamp, get_timestamp() )))
			self.flag.set()

def on_disconnect(userId, connect_timestamp, disconnect_timestamp):
	session = DatabaseManager.dbmanager.session()
	try:
		stat = UserConnection(userId, connect_timestamp, disconnect_timestamp)
		session.add(stat)
		session.commit()
	finally:
		session.close()

def on_death(userId, causeId, timestamp, mode):
	session = DatabaseManager.dbmanager.session()
	try:
		stat = DeathEvent(userId, causeId, timestamp, mode)
		session.add(stat)
		session.commit()
	finally:
		session.close()

def on_frag(userId, targetId, timestamp, mode):
	session = DatabaseManager.dbmanager.session()
	try:
		stat = FragEvent(userId, targetId, timestamp, mode)
		session.add(stat)
		session.commit()
	finally:
		session.close()

def on_shot(userId, timestamp, mode, gun, amount):
	session = DatabaseManager.dbmanager.session()
	try:
		stat = DamageSpentEvent(userId, timestamp, mode, gun, amount)
		session.add(stat)
		session.commit()
	finally:
		session.close()
		
def on_hit(userId, timestamp, mode, gun, amount):
	session = DatabaseManager.dbmanager.session()
	try:
		stat = DamageDealtEvent(userId, timestamp, mode, gun, amount)
		session.add(stat)
		session.commit()
	finally:
		session.close()