from cxsbs.Plugin import Plugin

class BanCore(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		self.init_tables()
		self.init_handlers()
		
	def reload(self):
		self.init_handlers()
		
	def unload(self):
		pass
	
	def init_tables(self):
		config = Config.PluginConfig('db')
		tableName = config.getOption('Bans', 'table_name', 'bans')
		del config
		
		global Ban
		class Ban(Base):
			__table_args__ = {'extend_existing': True}
			__tablename__= tableName
			id = Column(Integer, primary_key=True)
			ip = Column(Integer, index=True)
			mask = Column(Integer, index=True)
			expiration = Column(Integer, index=True) # Epoch seconds
			reason = Column(String(length=64))
			name = Column(String(length=16))
			banner_ip = Column(Integer)
			banner_nick = Column(String(length=16))
			time = Column(Integer)
			def __init__(self, ip, mask, expiration, reason, name, banner_ip, banner_nick, time):
				self.ip = ip
				self.mask = mask
				self.expiration = expiration
				self.reason = reason
				self.name = name
				self.banner_ip = banner_ip
				self.banner_nick = banner_nick
				self.time = time
			def isExpired(self):
				return self.expiration <= time.time()
		
		Base.metadata.create_all(DatabaseManager.dbmanager.engine)
		
	def init_handlers(self):
		global gbans
		gbans = {}
		
		@Events.policyHandler('connect_kick')
		def allowClient(cn, pwd):
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

import cxsbs
Players = cxsbs.getResource("Players")
DatabaseManager = cxsbs.getResource("DatabaseManager")
Events = cxsbs.getResource("Events")
Timers = cxsbs.getResource("Timers")
ServerCore = cxsbs.getResource("ServerCore")
Config = cxsbs.getResource("Config")
Net = cxsbs.getResource("Net")

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
#from sqlalchemy.types import BIGINT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import time, string

Base = declarative_base()

def getCurrentBanByIp(ipaddress):
	session = DatabaseManager.dbmanager.session()
	try:
		return session.query(Ban).filter(Ban.mask.op('&')(Ban.ip)==Ban.mask.op('&')(ipaddress)).filter('expiration>'+str(time.time())).one()
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

def addBan(cn, seconds, reason, banner_cn, cidr=32):

	ip = ServerCore.playerIpLong(cn)
	expiration = time.time() + seconds
	nick = ServerCore.playerName(cn)
	
	if banner_cn != -1:
		banner_ip = ServerCore.playerIpLong(banner_cn)
		banner_nick = ServerCore.playerName(banner_cn)
	else:
		banner_ip = 0
		banner_nick = 'the server'
		
	theTime = time.time()
	
	mask = Net.makeMask(cidr)
		
	newban = Ban(ip, mask, expiration, reason, nick, banner_ip, banner_nick, theTime)

	session = DatabaseManager.dbmanager.session()
	try:
		session.add(newban)
		session.commit()
	finally:
		session.close()
	
	Timers.addTimer(200, ServerCore.playerKick, (cn,))
	Events.triggerServerEvent("player_banned", (Net.ipLongToString(ip)+ "/" + str(cidr), seconds, expiration, reason, nick, banner_ip, banner_nick, theTime))