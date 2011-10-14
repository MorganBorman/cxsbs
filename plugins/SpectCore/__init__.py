import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
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
Messages = cxsbs.getResource("Messages")
Net = cxsbs.getResource("Net")

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import time, string

Base = declarative_base()

pluginCategory = 'SpectCore'

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="table_name", 
												displayName="Table name", 
												default="spectcore",
												doc="Table name for storing the spectates."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

permissionsCategory = 'Permissions'

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_transcend_spectate",
													displayName="Allow groups transcend spectate", 
													default=['__admin__'],
													doc="Groups which are permitted unspectate despite a force spectate.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="deny_groups_transcend_spectate",
													displayName="Deny groups transcend spectate", 
													default=[],
													doc="Groups which are not permitted to unspectate despite a force spectate.",
												))

groupSettings = SettingsManager.getAccessor(category=permissionsCategory, subcategory=pluginCategory)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="player_spectated", 
						displayName="player spectated", 
						default="${denied}You are currently ${blue}force spectated${white}. You cannot unspectate right now.", 
						doc="Message to print when a force spectated player tries to unspectate."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
		
class Spect(Base):
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["table_name"]
	id = Column(Integer, primary_key=True)
	ip = Column(BigInteger, index=True)
	mask = Column(BigInteger, index=True)
	expiration = Column(Integer, index=True) # Epoch seconds
	reason = Column(String(length=64))
	name = Column(String(length=16))
	responsible_ip = Column(BigInteger)
	responsible_nick= Column(String(length=16))
	time = Column(Integer)
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
		spects = session.query(Spect).filter(Spect.reason==reason).all()
		for s in spects:
			session.delete(s)
		session.commit()
	finally:
		session.close()

def getCurrentSpectByIp(ipaddress):
	session = DatabaseManager.dbmanager.session()
	try:
		return session.query(Spect).filter(Spect.expired == False).filter(Spect.mask.op('&')(Spect.ip)==Spect.mask.op('&')(ipaddress)).filter('expiration>'+str(time.time())).one()
	finally:
		session.close()

def isIpSpectd(ipaddress):
	try:
		b = getCurrentSpectByIp(ipaddress)
		return True
	except NoResultFound:
		return False
	except MultipleResultsFound:
		return True

def insertSpect(ipString, seconds, reason, responsible_cn=-1, maskString="255.255.255.255"):
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
	
	newspec = Spect(ip, mask, expiration, reason, nick, responsible_ip, responsible_nick, theTime)
	
	session = DatabaseManager.dbmanager.session()
	try:
		session.add(newspec)
		session.commit()
	finally:
		session.close()

def addSpect(cn, seconds, reason, responsible_cn=-1, maskString="255.255.255.255"):

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

	session = DatabaseManager.dbmanager.session()
	try:
		newspect = Spect(ip, mask, expiration, reason, nick, responsible_ip, responsible_nick, theTime)
		session.add(newspect)
		session.commit()
	finally:
		session.close()
		
	ServerCore.spectate(cn)
	Events.triggerServerEvent("player_punished", ("force spectated", Net.ipLongToString(ip)+ ":" + maskString, seconds, expiration, reason, nick, responsible_ip, responsible_nick, theTime))

@Events.policyHandler('player_unspectate')
def onUnspectate(cn, tcn):
	if cn != tcn:
				return True
	#try:
	p = Players.player(cn)
	ipAddress = p.ipLong()
	
	if p.isPermitted(groupSettings["allow_groups_transcend_spectate"], groupSettings["deny_groups_transcend_spectate"]):
		return True
	elif isIpSpectd(ipAddress):
		Timers.addTimer(200, messager.sendPlayerMessage, ('player_spectated', p))
		return False
	else:
		return True
	#except (AttributeError, ValueError):
		pass
	return True
	
@Events.eventHandler('player_active')
def onJoin(cn):
	if not onUnspectate(cn, cn):
		ServerCore.spectate(cn)