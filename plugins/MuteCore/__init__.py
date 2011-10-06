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

pluginCategory = 'MuteCore'

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="table_name", 
												displayName="Table name", 
												default="mutecore",
												doc="Table name for storing the mutes."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

permissionsCategory = 'Permissions'

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="allow_groups_transcend_mute",
													displayName="Allow groups transcend mute", 
													default=['__admin__'],
													doc="Groups which are permitted speak despite a mute.",
												))

SettingsManager.addSetting(Setting.ListSetting	(
													category=permissionsCategory, 
													subcategory=pluginCategory, 
													symbolicName="deny_groups_transcend_mute",
													displayName="Deny groups transcend mute", 
													default=[],
													doc="Groups which are not permitted to speak despite a mute.",
												))

groupSettings = SettingsManager.getAccessor(category=permissionsCategory, subcategory=pluginCategory)

SettingsManager.addSetting(Setting.BoolSetting	(
													category=pluginCategory, 
													subcategory="General", 
													symbolicName="mute_spectators",
													displayName="Mute spectators", 
													default=False,
													doc="Should spectators be muted by default.",
												))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="spectators_muted_toggled", 
						displayName="Spectators muted toggled", 
						default="${info}Spectators have been ${blue}${action}${white} by ${green}${name}${white}.", 
						doc="Message to print when the status of spectators_muted gets toggled."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="spectators_muted", 
						displayName="Spectators muted", 
						default="${denied}Spectators are currently ${blue}muted${white}. No one will receive your message.", 
						doc="Message to print when a muted spectator tries to speak."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="player_muted", 
						displayName="player muted", 
						default="${denied}You are currently ${blue}muted${white}. No one will receive your message.", 
						doc="Message to print when a muted player tries to speak."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
		
class Mute(Base):
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
	def __init__(self, ip, mask, expiration, reason, name, responsible_ip, responsible_nick, time):
		self.ip = ip
		self.mask = mask
		self.expiration = expiration
		self.reason = reason
		self.name = name
		self.responsible_ip = responsible_ip
		self.responsible_nick= responsible_nick
		self.time = time
	def isExpired(self):
		return self.expiration <= time.time()

Base.metadata.create_all(DatabaseManager.dbmanager.engine)

def clearByReason(reason):
	session = DatabaseManager.dbmanager.session()
	try:
		mutes = session.query(Mute).filter(Mute.reason==reason).all()
		for m in mutes:
			session.delete(m)
		session.commit()
	finally:
		session.close()

def getCurrentMuteByIp(ipaddress):
	session = DatabaseManager.dbmanager.session()
	try:
		return session.query(Mute).filter(Mute.mask.op('&')(Mute.ip)==Mute.mask.op('&')(ipaddress)).filter('expiration>'+str(time.time())).one()
	finally:
		session.close()

def isIpMuted(ipaddress):
	try:
		b = getCurrentMuteByIp(ipaddress)
		return True
	except NoResultFound:
		return False
	except MultipleResultsFound:
		return True

def addMute(cn, seconds, reason, responsible_cn, cidr=32):

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
	
	mask = Net.makeMask(cidr)
		
	newmute = Mute(ip, mask, expiration, reason, nick, responsible_ip, responsible_nick, theTime)

	session = DatabaseManager.dbmanager.session()
	try:
		session.add(newmute)
		session.commit()
	finally:
		session.close()
	
	Events.triggerServerEvent("player_punished", ("muted", Net.ipLongToString(ip)+ "/" + str(cidr), seconds, expiration, reason, nick, responsible_ip, responsible_nick, theTime))
	
@Events.policyHandler('allow_message_team')
@Events.policyHandler('allow_message')
def allowMsg(cn, text):
	try:
		p = Players.player(cn)
		ipAddress = p.ipLong()
		
		if p.isPermitted(groupSettings["allow_groups_transcend_mute"], groupSettings["deny_groups_transcend_mute"]):
			return True
		elif settings['mute_spectators'] and p.isSpectator():
			messenger.sendPlayerMessage('spectators_muted', p)
			return False
		elif isIpMuted(ipAddress):
			messager.sendPlayerMessage('player_muted', p)
			return False
		else:
			return True
	except (AttributeError, ValueError):
		pass
	return True