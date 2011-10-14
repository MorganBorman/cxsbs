import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		banManager = PunitiveManager(BanCore.Ban, "Ban")
		ManageCore.registerManager("ban", banManager)
		
		muteManager = PunitiveManager(MuteCore.Mute, "Mute")
		ManageCore.registerManager("mute", muteManager)
		
		specManager = PunitiveManager(SpectCore.Spect, "Spectate")
		ManageCore.registerManager("spec", specManager)
		
	def unload(self):
		pass
	
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.expression import func

import time
import timestring
import prettytime

import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
Net = cxsbs.getResource("Net")
Messages = cxsbs.getResource("Messages")
ManageCore = cxsbs.getResource("ManageCore")
Colors = cxsbs.getResource("Colors")
Players = cxsbs.getResource("Players")
Commands = cxsbs.getResource("Commands")
DatabaseManager = cxsbs.getResource("DatabaseManager")
PunitiveCommands = cxsbs.getResource("PunitiveCommands")
Logging = cxsbs.getResource("Logging")

BanCore = cxsbs.getResource("BanCore")
MuteCore = cxsbs.getResource("MuteCore")
SpectCore = cxsbs.getResource("SpectCore")

pluginCategory = "ManagePunitive"

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="nothing_found", 
						displayName="Nothing found", 
						default="${info}Nothing matching the given term was found.", 
						doc="Message to print when nothing matching the given term was found."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="nothing_recent", 
						displayName="Nothing recent", 
						default="${info}No recent items were found.", 
						doc="Message to print when no recent items of a type were found."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="item_cleared", 
						displayName="Item cleared", 
						default="${info}${type} on ${ip} set to expired.", 
						doc="Message to print when clear has been executed."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="inserted", 
						displayName="Inserted", 
						default="${info}${red}${action}${white} applied to ${orange}${ip}${white} for ${time} by ${green}${responsible}${white} for ${red}${reason}${white}.", 
						doc="Message to print when a punitive effect has been inserted."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
	
def justify(width, text):
	return text.ljust(width)[:width] + "    "

def itemString(item):
	#5    216.235.22.12:255.255.255.0    TrollDude    [FD]Chasm    Fri, Jul 29, 15:46:33    Wed, Jul 30, 15:46:33
	
	if item.isExpired():
		identifier = Colors.grey("#" + str(item.id))
	else:
		identifier = Colors.green("#" + str(item.id))
		
	return_string = ''.join	(	[
									justify(8, identifier),
									justify(30, Net.ipLongToString(item.ip) + ':' + Net.ipLongToString(item.mask)),
									justify(24, item.reason),
									justify(15, item.name),
									justify(15, item.responsible_nick),
									justify(24, time.ctime(item.time)),
									justify(24, time.ctime(item.expiration)),
								]
							)
	
	return return_string
	
def itemStringHeader():
	#ID    Player IP:Mask    Player name    Moderator name    Time    Expire time
	
	return_string = ''.join	(	[
									justify(8, "#ID"),
									justify(30, "Player IP:Mask"),
									justify(24, "Reason"),
									justify(15, "Player name"),
									justify(18, "Moderator name"),
									justify(24, "Time"),
									justify(24, "Expire time"),
								]
							)
	
	return return_string

def ciStringFindMap(string, term, func):
	"""runs func on case insensitive matches of term in the string and returns the string"""
	
	peices = []
	
	f = 0
	l = len(term)
	
	while l < len(string):
		if string[f:l].lower() == term.lower():
			peices.append(string[:f])
			peices.append(func(string[f:l]))
			string = string[l:]
			
			f = 0
			l = len(term)
		else:
			f += 1
			l += 1
	
	return "".join(peices) + string
	
def highlightMatching(string, term, color):
	return ciStringFindMap(string, term, color)
	
class PunitiveManager(ManageCore.Manager):
	def __init__(self, table, punType):
		self.punType = punType
		self.table = table
		ManageCore.Manager.__init__(self)
		
	def search(self, cn, term):
		matching = []
		session = DatabaseManager.dbmanager.session()
		try:
			items = session.query(self.table).filter('expiration>'+str(time.time())).all()
			for item in items:
				if term in Net.ipLongToString(item.ip):
					matching.append(item)
	
			sterm = "%" + term.lower() + "%"
			
			query = session.query(self.table)
			filtered = query.filter('expiration>'+str(time.time()))
			filtered = filtered.filter	(
													or_(
														func.lower(self.table.name).like(sterm), 
														func.lower(self.table.responsible_nick).like(sterm), 
														func.lower(self.table.reason).like(sterm),
													)
												)
			items = filtered.all()
			
			for item in items:
				matching.append(item)
	
		finally:
			session.close()
		
		p = Players.player(cn)
		if len(matching) > 0:
			p.message(Colors.blue(itemStringHeader()))
			for item in matching:
				string = itemString(item)
				p.message(highlightMatching(string, term, Colors.red))
		else:
			messager.sendPlayerMessage('nothing_found', p)
		
	def searchAction(self, cn, term):
		pass
		
	def clear(self, cn, identifier):
		p = Players.player(cn)
		
		session = DatabaseManager.dbmanager.session()
		try:
			items = session.query(self.table).filter(self.table.id == identifier).all()
			if len(items) > 0:
				for item in items:
					messager.sendPlayerMessage('item_cleared', p, dictionary={'type':self.punType, 'ip':Net.ipLongToString(item.ip)})
					item.expired = True
					session.add(item)
				session.commit()
			else:
				messager.sendPlayerMessage('nothing_found', p)
		finally:
			session.close()
			
	def insert(self, cn, ipString, maskString, actionTime, reason):
		p = Players.player(cn)
		
		if actionTime == None:
			seconds = settings['default_action_interval']
		else:
			try:
				seconds = timestring.parseTimeString(actionTime)[1]
			except timestring.MalformedTimeString:
				raise Commands.ArgumentValueError("That time string does not seem to be valid.")
			
		ip = Net.ipStringToLong(ipString)
		expiration = time.time() + seconds
		nick = "None Inserted"
		theTime = time.time()
		
		responsible_ip = p.ipLong()
		responsible_nick= p.name()
		
		mask = Net.ipStringToLong(maskString)
		
		new = self.table(ip, mask, expiration, reason, nick, responsible_ip, responsible_nick, theTime)
		
		session = DatabaseManager.dbmanager.session()
		try:
			session.add(new)
			session.commit()
		finally:
			session.close()
			
		dictionary = 	{
							'ip': str(ip) + ":" + maskString,
							'time': prettytime.createDurationString(seconds),
							'action': self.punType,
							'responsible': responsible_nick,
							'reason': reason,
						}
		
		messager.sendMessage('inserted', dictionary=dictionary)
		
		logString = str(responsible_nick) + "@" + str(responsible_ip) + " has " + str(self.punType) + " " + str(ip) + ":" + maskString
		Logging.info(logString)
	
	def recent(self, cn, show_expired, count):
		p = Players.player(cn)
		session = DatabaseManager.dbmanager.session()
		try:
			if show_expired:
				recent = session.query(self.table).order_by(self.table.time.asc())
			else:
				recent = session.query(self.table).filter('expiration>'+str(time.time())).order_by(self.table.time.asc())
				
			recent = recent[-count:]
			
		finally:
			session.close()
			
		if len(recent) > 0:
			p.message(Colors.blue(itemStringHeader()))
			for item in recent:
				p.message(itemString(item))
		else:
			messager.sendPlayerMessage('nothing_recent', p)