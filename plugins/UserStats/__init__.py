import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):

		statWriter = StatWriter()
		statWriter.start()
		
		Events.registerServerEventHandler('player_teamkill', statWriter.on_teamkill)
		Events.registerServerEventHandler('player_frag', statWriter.on_frag)
		Events.registerServerEventHandler('player_suicide', statWriter.on_suicide)
		Events.registerServerEventHandler('player_spend_damage', statWriter.on_shot)
		Events.registerServerEventHandler('player_inflict_damage', statWriter.on_hit)
		
	def unload(self):
		pass

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import func

import datetime, threading

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
												displayName="Damage Spent Table name", 
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
	__tablename__= tableSettings["damage_spent_table_name"]
	userId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	amount = Column(Integer)
	
	def __init__(self, userId, timestamp, mode, amount):
		self.userId = userId
		self.timestamp = timestamp
		self.mode = mode
		self.amount = amount

class DamageDealtEvent(Base):
	"each damage dealt event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["damage_dealt_table_name"]
	userId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	amount = Column(Integer)
	
	def __init__(self, userId, timestamp, mode, amount):
		self.userId = userId
		self.timestamp = timestamp
		self.mode = mode
		self.amount = amount
	
TEAMKILL = -2
		
class FragEvent(Base):
	"each frag event with a timestamp for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["frag_event_table_name"]
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
	userId = Column(Integer, index=True)
	causeId = Column(Integer, index=True)
	timestamp = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	
	def __init__(self, userId, causeId, timestamp, mode):
		self.userId = userId
		self.causeId = causeId
		self.timestamp = timestamp
		self.mode = mode
		
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
		
	def run(self):
		while self.running:
			
			self.flag.clear()
			self.flag.wait()
			
			while len(self.event_queue) > 0:
				event = self.event_queue.pop(0)
				#do something with it
				try:
					event[0](*(event[1]))
				except:
					pass
				
	def stop(self):
		self.running = False
		self.flag.set()
		
	def on_teamkill(self, cn, tcn):
		self.event_queue.append((on_teamkill, (cn, tcn)))
		self.event_queue.append((on_death, (tcn,)))
		self.flag.set()
	
	def on_frag(self, cn, tcn):
		self.event_queue.append((on_frag, (cn, tcn)))
		self.event_queue.append((on_death, (tcn,)))
		self.flag.set()
	
	def on_suicide(self, cn):
		self.event_queue.append((on_suicide, (cn,)))
		self.flag.set()
	
	def on_shot(self, cn, damage):
		self.event_queue.append((on_shot, (cn, damage)))
		self.flag.set()
	
	def on_hit(self, cn, damage):
		self.event_queue.append((on_hit, (cn, damage)))
		self.flag.set()














def AccessCurrentStat(session, userId):
	"""
	Gets the UserStat object for the given user and the current mode/date
	If one does not exist, initialize one and return that.
	"""
	epoch = datetime.datetime.utcfromtimestamp(0)
	today = datetime.datetime.today()
	d = today - epoch
	
	date = d.days # timedelta object
	mode = Game.currentMode()
	
	try:
		stat = session.query(UserStat).filter(UserStat.userId==userId).filter(UserStat.date==date).filter(UserStat.mode==mode).one()
		return stat
	except NoResultFound:
		stat = UserStat(userId, date, mode)
		session.add(stat)
		session.commit()
		return stat



"""
@Events.eventHandler('player_disconnect')
def onPlayerDisconnect(cn):
	if not Users.isLoggedIn(cn):
		return
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.death()
		session.commit()
	finally:
		session.close()
		
@Events.eventHandler('player_connect')
def onPlayerConnect(cn):
	if not Users.isLoggedIn(cn):
		return
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.death()
		session.commit()
	finally:
		session.close()
"""

def on_death(cn):
	if not Users.isLoggedIn(cn):
		return
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.death()
		session.add(stat)
		session.commit()
	finally:
		session.close()

def on_teamkill(cn, tcn):
	if not Users.isLoggedIn(cn):
		return
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.teamkill()
		session.add(stat)
		session.commit()
	finally:
		session.close()

def on_frag(cn, tcn):
	if not Users.isLoggedIn(cn):
		return
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.frag()
		session.add(stat)
		session.commit()
	finally:
		session.close()

def on_suicide(cn):
	if not Users.isLoggedIn(cn):
		return
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.suicide()
		session.add(stat)
		session.commit()
	finally:
		session.close()

"""
@Events.eventHandler('player_shot')
def onShot(cn, shotid, gun):
	if not Users.isLoggedIn(cn):
		return
	
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.shot()
		session.add(stat)
		session.commit()
	finally:
		session.close()
		
@Events.eventHandler('player_shot_hit')
def onShotHit(cn, tcn, lifesequence, dist, hitrays):
	if not Users.isLoggedIn(cn):
		return
	
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.hit()
		session.add(stat)
		session.commit()
		ServerCore.message(("Current accuracy: %0.2f" %(stat.accuracy()*100)) + '%')
	finally:
		session.close()
"""

def on_shot(cn, damage):
	if not Users.isLoggedIn(cn):
		return
	
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.shot(damage)
		session.add(stat)
		session.commit()
	finally:
		session.close()
		
def on_hit(cn, damage):
	if not Users.isLoggedIn(cn):
		return
	
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.hit(damage)
		session.add(stat)
		session.commit()
		#ServerCore.message(("Current accuracy: %0.2f" %(stat.accuracy()*100)) + '%')
	finally:
		session.close()