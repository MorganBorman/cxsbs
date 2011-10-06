import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
from sqlalchemy import Column, Integer, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound

import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
DatabaseManager = cxsbs.getResource("DatabaseManager")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Commands = cxsbs.getResource("Commands")
Events = cxsbs.getResource("Events")
Messages = cxsbs.getResource("Messages")
Players = cxsbs.getResource("Players")
Colors = cxsbs.getResource("Colors")

pluginCategory = "AliasTracking"

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="table_name", 
												displayName="Table name", 
												default="aliastracking",
												doc="Table name for storing the name-ip associations."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory,
												subcategory="General", 
												symbolicName="max_results", 
												displayName="Max results", 
												default=20,
												doc="Maximum number of names to show for a players' ip."
											))

settings = SettingsManager.getAccessor(pluginCategory, "General")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="names_preamble", 
						displayName="Names preamble", 
						default="${info}Other names: ${namesString}", 
						doc="Message to print when the names command is run."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

Base = declarative_base()

class IpToName(Base):
	__tablename__= tableSettings["table_name"]
	ip = Column(Integer, index=True, primary_key=True)
	name = Column(String(length=16), primary_key=True)
	count = Column(Integer, nullable=False)
	def __init__(self, ip, name):
		self.ip = ip
		self.name = name
		self.count = 1
		
Base.metadata.create_all(DatabaseManager.dbmanager.engine)

@Events.eventHandler('player_connect')
def onConnect(cn):
	session = DatabaseManager.dbmanager.session()
	try:
		entry = session.query(IpToName).filter(IpToName.ip==ServerCore.playerIpLong(cn)).filter(IpToName.name==ServerCore.playerName(cn)).one()
		entry.count = entry.count + 1
		session.add(entry)
		session.commit()
	except NoResultFound:
		entry = IpToName(ServerCore.playerIpLong(cn), ServerCore.playerName(cn))
		session.add(entry)
		session.commit()
	finally:
		session.close()

@Events.eventHandler('player_name_changed')
def onNameChange(cn, oldname, newname):
	if oldname != newname:
		onConnect(cn)

@Commands.commandHandler('names')
def namesCmd(cn, args):
	'''
	@description Display aliases used with this players ip
	@usage <cn>
	@allowGroups __admin__
	@denyGroups
	@doc Display aliases used with the given players ip
	'''
	if args == '':
		raise UsageError()
	
	try:
		tcn = int(args)
		
		session = DatabaseManager.dbmanager.session()
		try:
			totalOccurances = session.query(func.sum(IpToName.count)).filter(IpToName.ip==ServerCore.playerIpLong(tcn)).scalar()
			results = session.query(IpToName).filter(IpToName.ip==ServerCore.playerIpLong(tcn)).order_by(IpToName.count.desc())
		finally:
			session.close()
			
		count = 0
		namestr = ""
		for result in results:
			percent = round(float(result.count)/float(totalOccurances)*100, 2)
			namestr += result.name + Colors.grey('(' + str(percent) + '%) ')
			count += 1
			if count > settings['max_results']:
				break
		if count == 0:
			raise NoResultsFound()
			
		p = Players.player(cn)
		messager.sendPlayerMessage('names_preamble', p, dictionary={'namesString': namestr})
		
	except NoResultFound:
		ServerCore.playerMessage(cn, 'No names found')
		return