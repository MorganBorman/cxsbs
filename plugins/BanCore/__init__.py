import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global gbans
		gbans = {}
		
	def unload(self):
		pass

import cxsbs
Players = cxsbs.getResource("Players")
DatabaseManager = cxsbs.getResource("DatabaseManager")
Events = cxsbs.getResource("Events")
Timers = cxsbs.getResource("Timers")
ServerCore = cxsbs.getResource("ServerCore")
SettingsManager = cxsbs.getResource("SettingsManager")
Setting = cxsbs.getResource("Setting")
Net = cxsbs.getResource("Net")
SetMaster = cxsbs.getResource("SetMaster")
PlayerDisconnect = cxsbs.getResource("PlayerDisconnect")

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.sql.expression import func

import time, string

Base = declarative_base()
		
pluginCategory = 'BanCore'
		
SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="table_name", 
												displayName="Table name", 
												default="bancore",
												doc="Table name for storing the bans."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)
		
class Ban(Base):
	__tablename__= tableSettings["table_name"]
	id = Column(Integer, primary_key=True)
	ip = Column(BigInteger, index=True)
	mask = Column(BigInteger, index=True)
	expiration = Column(BigInteger, index=True) # Epoch seconds
	reason = Column(String(length=64))
	name = Column(String(length=16))
	responsible_ip = Column(BigInteger)
	responsible_nick= Column(String(length=16))
	time = Column(BigInteger)
	expired = Column(Boolean)
	def __init__(self, ip, mask, expiration, reason, name, responsible_ip, responsible_nick, time):
		self.ip = ip
		self.mask = mask
		self.expiration = expiration
		self.reason = reason
		self.name = name
		self.responsible_ip = responsible_ip
		self.responsible_nick= responsible_nick
		self.time = time
		self.expired = False
	def isExpired(self):
		if self.expired:
			return True
		return self.expiration <= time.time()

Base.metadata.create_all(DatabaseManager.dbmanager.engine)

def clearByReason(reason):
	session = DatabaseManager.dbmanager.session()
	try:
		bans = session.query(Ban).filter(Ban.reason==reason).all()
		for b in bans:
			b.expired = True
			session.add(b)
		session.commit()
	finally:
		session.close()

def getCurrentBanByIp(ipaddress):
	session = DatabaseManager.dbmanager.session()
	try:
		return session.query(Ban).filter(Ban.expired == False).filter(Ban.mask.op('&')(Ban.ip)==Ban.mask.op('&')(ipaddress)).filter('expiration>'+str(time.time())).one()
	finally:
		session.close()

def isIpBanned(ipaddress):
	try:
		b = getCurrentBanByIp(ipaddress)
		return True
	except NoResultFound:
		return False
	except MultipleResultsFound:
		return True
	
def insertBan(ipString, seconds, reason, responsible_cn=-1, maskString="255.255.255.255"):
	ip = Net.ipStringToLong(cn)
	expiration = time.time() + seconds
	nick = "None Inserted"
	
	if responsible_cn != -1:
		responsible_ip = ServerCore.playerIpLong(responsible_cn)
		responsible_nick= ServerCore.playerName(responsible_cn)
	else:
		responsible_ip = 0
		responsible_nick= 'the server'
	
	mask = Net.ipStringToLong(maskString)
	
	newban = Ban(ip, mask, expiration, reason, nick, responsible_ip, responsible_nick, theTime)
	
	session = DatabaseManager.dbmanager.session()
	try:
		session.add(newban)
		session.commit()
	finally:
		session.close()

def addBan(cn, seconds, reason, responsible_cn=-1, maskString="255.255.255.255"):
	ip = ServerCore.playerIpLong(cn)
	expiration = time.time() + seconds
	nick = ServerCore.playerName(cn)
	
	if responsible_cn != -1:
		responsible_ip = ServerCore.playerIpLong(responsible_cn)
		responsible_nick= ServerCore.playerName(responsible_cn)
	else:
		responsible_ip = 0
		responsible_nick= 'the server'
		
	theTime = time.time()
	
	mask = Net.ipStringToLong(maskString)
		
	newban = Ban(ip, mask, expiration, reason, nick, responsible_ip, responsible_nick, theTime)

	session = DatabaseManager.dbmanager.session()
	try:
		session.add(newban)
		session.commit()
	finally:
		session.close()
		
	Events.execLater(PlayerDisconnect.disconnect, (cn, PlayerDisconnect.DISC_KICK))
	Events.triggerServerEvent("player_punished", ("banned", Net.ipLongToString(ip)+ ":" + maskString, seconds, expiration, reason, nick, responsible_ip, responsible_nick, theTime))
	
@Events.policyHandler('connect_kick')
def allowClient(cn, pwd):
	connecthash = ServerCore.hashPassword(cn, SetMaster.settings["connect_password"])
	if pwd == connecthash:
		return True
	
	ip = ServerCore.playerIpLong(cn)
	return not isIpBanned(ip)

@Events.policyHandler('connect_kick')
def isNotGBanned(cn, pwd):
	try:
		gbans[Net.ipLongToString(ServerCore.playerIpLong(cn))]
		return False
	except KeyError:
		return True

@Events.eventHandler('master_addgban')
def adGBan(ip_string):
	gbans[ip_string] = True

@Events.eventHandler('master_cleargbans')
def clearGBans():
	gbans.clear()
