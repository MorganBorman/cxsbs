import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass

from sqlalchemy import Column, Integer, BigInteger, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relation, mapper
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql.expression import func

import datetime

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
												symbolicName="table_name", 
												displayName="Table name", 
												default="user_stats",
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

class UserStat(Base):
	"Store per day stats for each user account"
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["table_name"]
	userId = Column(Integer, index=True)
	date = Column(BigInteger, index=True)
	mode = Column(Integer, index=True)
	
	frags = Column(BigInteger)
	suicides = Column(BigInteger)
	deaths = Column(BigInteger)
	teamkills = Column(BigInteger)
	
	shot_damage = Column(BigInteger)
	hit_damage = Column(BigInteger)
	
	UniqueConstraint('userId', 'date', 'mode', name='uq_userid_date_mode')
	__mapper_args__ = {'primary_key':[userId, date, mode]}
	def __init__(self, userId, date, mode):
		self.userId = userId
		self.date = date
		self.mode = mode
		
		self.frags = 0
		self.suicides = 0
		self.deaths = 0
		self.teamkills = 0
		
		self.shot_damage = 0
		self.hit_damage = 0
		
	def frag(self):
		self.frags += 1
		
	def suicide(self):
		self.suicides += 1
		
	def death(self):
		self.deaths += 1
		
	def teamkill(self):
		self.teamkills += 1
		
	def shot(self, damage):
		self.shot_damage += damage
		
	def hit(self, damage):
		self.hit_damage += damage
		
	def accuracy(self):
		if self.shot_damage != 0:
			return float(self.hit_damage)/float(self.shot_damage)
		else:
			return 1
		
Base.metadata.create_all(DatabaseManager.dbmanager.engine)

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

def onDeath(cn):
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

@Events.eventHandler('player_teamkill')
def onTeamkill(cn, tcn):
	onDeath(tcn)
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
	
@Events.eventHandler('player_frag')
def onFrag(cn, tcn):
	onDeath(tcn)
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

@Events.eventHandler('player_suicide')
def onSuicide(cn):
	onDeath(cn)
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

@Events.eventHandler('player_spend_damage')
def onShot(cn, damage):
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
		
@Events.eventHandler('player_inflict_damage')
def onShotHit(cn, damage):
	if not Users.isLoggedIn(cn):
		return
	
	user = Players.player(cn)
	session = DatabaseManager.dbmanager.session()
	try:
		stat = AccessCurrentStat(session, user.userId)
		stat.hit(damage)
		session.add(stat)
		session.commit()
		ServerCore.message(("Current accuracy: %0.2f" %(stat.accuracy()*100)) + '%')
	finally:
		session.close()

@Events.eventHandler('intermission_begin')
def onIntermission():
	pass