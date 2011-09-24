from cxsbs.Plugin import Plugin

class ClanTags(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
		
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from xsbs.ban import ban
from xsbs.colors import red, blue
from xsbs.commands import commandHandler, UsageError
from xsbs.db import dbmanager
from xsbs.events import eventHandler, execLater, registerServerEventHandler
from xsbs.players import player, adminRequired
from xsbs.timers import addTimer
from xsbs.ui import warning, info, error
from xsbs.users.users import isLoggedIn
import logging
import re

regex = '\[.{1,5}\]|<.{1,5}>|\{.{1,5}\}|\}.{1,5}\{|.{1,5}\||\|.{1,5}\|'
regex = re.compile(regex)

Base = declarative_base()

class ClanTag(Base):
	__tablename__ = 'clantags'
	id = Column(Integer, primary_key=True)
	tag = Column(String(16), index=True)
	def __init__(self, tag):
		self.tag = tag

class ClanMember(Base):
	__tablename__ = 'clanmember'
	id = Column(Integer, primary_key=True)
	tag_id = Column(Integer, index=True)
	user_id = Column(Integer, index=True)
	def __init__(self, tag_id, user_id):
		self.tag_id = tag_id
		self.user_id = user_id

def warnTagReserved(cn, count, sessid, nick):
	try:
		p = player(cn)
	except ValueError:
		return
	if p.name() != nick or sessid != p.sessionId():
		return
	if len(p.registered_tags) == 0:
		return
	if count > 4:
		(cn, 0, 'Use of reserved clan tag', -1)
		p.warning_for_login = False
		return
	remaining = 25-(count*5)
	p.message(warning('Your are using a reserved clan tag. You have ' + red('%i') + ' seconds to login or be kicked.') % remaining)
	addTimer(5000, warnTagReserved, (cn, count+1, sessid, nick))

def tagId(tag):
	session = dbmanager.session()
	try:
		return session.query(ClanTag).filter(ClanTag.tag==tag).one().id
	finally:
		session.close()

def setUsedTags(cn):
	try:
		p = player(cn)
	except ValueError:
		return
	nick = p.name()
	potentials = []
	matches = regex.findall(nick)
	for match in matches:
		potentials.append(match)
	p.registered_tags = []
	for potential in potentials:
			try:
				id = tagId(potential)
				p.registered_tags.append(id)
			except NoResultFound:
				pass

def userBelongsTo(user, tag_id):
	session = dbmanager.session()
	try:
		session.query(ClanMember).filter(ClanMember.tag_id==tag_id).filter(ClanMember.user_id==user.id).one()
		return True
	except MultipleResultsFound:
		return True
	except NoResultFound:
		return False
	finally:
		session.close()

def onLogin(cn):
	try:
		p = player(cn)
		u = p.user
	except AttributeError:
		logging.error('Got login event but no user object for player.')
		return
	try:
		for tag in p.registered_tags:
			t = p.registered_tags.pop(0)
			if userBelongsTo(u, t):
				return
			else:
				ban(cn, 0, 'Use of reserved clan tag', -1)
	except AttributeError:
		return

def initCheck(cn):
	if isLoggedIn(cn):
		onLogin(cn)
		return
	p = player(cn)
	try:
		if p.warning_for_login:
			return
	except AttributeError:
		pass
	else:
		warnTagReserved(cn, 0, p.sessionId(), p.name())
	
def justify(width, text):
	return text.ljust(width)[:width] + "    "

def banToString(t):
	#5	[FD]
	
	return_string = "#" + str(t.id).ljust(7) 
	return_string += justify(15, t.tag)
	return return_string
	
def banStringHeader():
	return_string = "#ID".ljust(8)
	return_string += justify(15, "Tag")
	return return_string

@eventHandler('player_connect_delayed')
def onConnect(cn):
	setUsedTags(cn)
	p = player(cn)
	try:
		if len(p.registered_tags) > 0:
			execLater(initCheck, (cn,))
			registerServerEventHandler('player_logged_in', onLogin)
	except AttributeError:
		pass

@eventHandler('player_name_changed')
def onNameChange(cn, oldname, newname):
	onConnect(cn)

@commandHandler('listtags')
def onListTags(cn, args):
	'''@description List available clantags
	   @usage'''
	p = player(cn)
	session = dbmanager.session()
	try:
		tags = session.query(ClanTag).all()
	finally:
		session.close()
	if len(tags) > 0:
		p.message(blue(banStringHeader()))
		for t in tags:
			p.message(banToString(t))
	else:
		p.message(info("There are no clantags to list."))
	
@commandHandler('addtag')
def onAddTag(cn, args):
	'''@description Add a clantag
	   @usage <tag>'''
	p = player(cn)
	session = dbmanager.session()
	try:
		args = args.split()
		if len(args) < 1:
			raise UsageError()
		same = session.query(ClanTag).filter(ClanTag.tag==args[0]).all()
		if len(same) > 0:
			return
	except NoResultFound:
		pass
	finally:
		session.close()
		
	session = dbmanager.session()
	try:
		ent = ClanTag(args[0])
		session.add(ent)
		session.commit()
	finally:
		session.close()
	p.message(info("Added clantag: " + ent.tag))
	
@commandHandler('deltag')
def onDelTag(cn, args):
	'''@description Remove a clantag
	   @usage <tag#>'''
	session = dbmanager.session()
	try:
		p = player(cn)
		args = args.split()
		if len(args) < 1:
			raise UsageError()
		try:
			ident = int(args[0])
		except:
			raise UsageError()
		same = session.query(ClanTag).filter(ClanTag.id==ident).all()
		p.message(info(str(same[0].tag) + " tag removed."))
		session.delete(same[0])
		session.commit()
	except NoResultFound:
		p.message(error("That tag id does not seemt to exist."))
	finally:
		session.close()
	
@commandHandler('linktag')
def onLinkTag(cn, args):
	'''@description Allow a logged in player to use a clantag
	   @usage <cn> <tag#>'''
	args = args.split(' ')
	p = player(cn)
	session = dbmanager.session()
	try:
		tcn = int(args[0])
		q = player(tcn)
		u = q.user
		
		tagId = int(args[1])
		tag = session.query(ClanTag).filter(ClanTag.id==tagId).one()
		
		ent = ClanMember(tag.id, u.id)
		session.add(ent)
		session.commit()
		
		p.message(info("Linked " + str(tag.tag) + " to " + str(u.email)))
		
	except AttributeError:
		p.message(error("That player does not seem to be logged in."))
	except (KeyError):
		raise UsageError()
	except NoResultFound:
		p.message(error("That tag id does not seemt to exist."))
	finally:
		session.close()

Base.metadata.create_all(dbmanager.engine)