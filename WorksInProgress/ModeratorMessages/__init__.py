import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
DatabaseManager = cxsbs.getResource("DatabaseManager")
SettingsManager = cxsbs.getResource("SettingsManager")
Setting = cxsbs.getResource("Setting")
Players = cxsbs.getResource("Players")
Messages = cxsbs.getResource("Messages")
Commands = cxsbs.getResource("Commands")
	
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import time, string

Base = declarative_base()
	
class ModeratorMessage(Base):
	__table_args__ = {'extend_existing': True}
	__tablename__= tableSettings["table_name"]
	id = Column(Integer, primary_key=True)
	symbolicName = Column(String(24), index=True)
	message = Column(String(length=200))
	
pluginCategory = 'ModeratorMessages'

SettingsManager.addSetting(Setting.Setting	(
												category=DatabaseManager.getDbSettingsCategory(),
												subcategory=pluginCategory, 
												symbolicName="table_name", 
												displayName="Table name", 
												default="moderator_messages",
												doc="Table name for storing the mutes."
											))

tableSettings = SettingsManager.getAccessor(DatabaseManager.getDbSettingsCategory(), pluginCategory)
		
@Commands.commandHandler('addtemplate')
def onAddTemplate(cn, args):
	'''
	@description Add a message template to the stored ones.
	@usage 5m
	@allowGroups __admin__
	@denyGroups
	@doc Add a message template to the stored ones.
	'''
	pass

@Commands.commandHandler('deltemplate')
def onDelTemplate(cn, args):
	'''
	@description Add a message template to the stored ones.
	@usage 5m
	@allowGroups __admin__
	@denyGroups
	@doc Delete a message template from the stored ones.
	'''
	pass
		
@Commands.commandHandler('templatemessage')
def onTemplateMessageCommand(cn, args):
	'''
	@description Send a template message to a specified player.
	@usage <cn> <message name>
	@allowGroups __admin__ __master__
	@denyGroups
	@doc Add a message template to the stored ones.
	'''
	pass

@Commands.commandHandler('templatebroadcast')
def onTemplateBroadcastCommand(cn, args):
	'''
	@description Add a message template to the stored ones.
	@usage 5m
	@allowGroups __admin__
	@denyGroups
	@doc Add a message template to the stored ones.
	'''
	pass