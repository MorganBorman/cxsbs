import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global messagesManager
		messagesManager = MessagesManager(SettingsManager.settingsManager)
		
	def unload(self):
		pass
	
import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
UI = cxsbs.getResource("UI")
Colors = cxsbs.getResource("Colors")
Players = cxsbs.getResource("Players")

import sys, traceback
	
class Accessor:
	'''Thin interface to the settingsManager to clean up sending of messages for a particular plugin'''
	def __init__(self, messagesManager, category, subcategory):
		self.messagesManager = messagesManager
		self.category = category
		self.subcategory = subcategory
	
	def __str__(self):
		print "<"+"MessagesManager['"+self.category+"']['"+self.subcategory+"'] Accessor>"
	
	def sendMessage(self, symbolicName, group=None, dictionary=None):
		self.messagesManager.sendMessage(self.subcategory, symbolicName, group, dictionary, self.category)
		
	def sendPlayerMessage(self, symbolicName, p, dictionary=None):
		self.messagesManager.sendPlayerMessage(self.subcategory, symbolicName, p, dictionary, self.category)
		
	def printMessage(self, symbolicName, group=None, dictionary=None):
		self.messagesManager.printMessage(self.subcategory, symbolicName, dictionary, self.category)
	
class MessagesManager:
	def __init__(self, settingsManager):
		self.settingsManager = settingsManager
		self.dictionary = Colors.colordict
		
	def addMessage(self, subcategory, symbolicName, displayName, default, doc, category="Messages"):
		template = Setting.TemplateSetting	(
												category=category, 
												subcategory=subcategory, 
												symbolicName=symbolicName, 
												displayName=displayName, 
												default=default, 
												writeBackDefault=None, 
												value=Setting.NotSpecified, 
												writeBack=Setting.NotSpecified, 
												doc=doc,
											)
		self.settingsManager.addSetting(template)
		
	def __formMessage(self, subcategory, symbolicName, dictionary, category="Messages"):
		if dictionary == None:
			dictionary = self.dictionary
		else:
			dictionary.update(self.dictionary)
			
		dictionary.update(UI.UIDict())
		try:
			messageTemplate = self.settingsManager.getValue(category, subcategory, symbolicName)
			return messageTemplate.substitute(dictionary)
		except KeyError:
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
			cxsbs.Logging.logger.error('Messages Framework: Attempt to send unknown message: ' + str(symbolicName) + ' from category: ' + str(category) + ' and subcategory: ' + str(subcategory))
			cxsbs.Logging.logger.error(traceback.format_exc())
	
	def getAccessor(self, category="Messages", subcategory="General"):
		return Accessor(self, category, subcategory)
		
	def sendMessage(self, subcategory, symbolicName, group=None, dictionary=None, category="Messages"):
		if group == None:
			group = Players.AllPlayersGroup
			
		message = self.__formMessage(category=category, subcategory=subcategory, symbolicName=symbolicName, dictionary=dictionary)
		
		if message == '' or message == None:
			return
		
		group.action("message", (message,))
		
	def printMessage(self, subcategory, symbolicName, dictionary=None, category="Messages"):
		message = self.__formMessage(category=category, subcategory=subcategory, symbolicName=symbolicName, dictionary=dictionary)
		if message == '' or message == None:
			return
		print repr(message)
		
	def sendPlayerMessage(self, subcategory, symbolicName, p, dictionary=None, category="Messages"):
		message = self.__formMessage(category=category, subcategory=subcategory, symbolicName=symbolicName, dictionary=dictionary)
		if message == '' or message == None:
			return
		p.message(message)
		
def addMessage(subcategory, symbolicName, displayName, default, doc, category="Messages"):
	"""Add a setting to the manager and read it's current value from the filesystem."""
	messagesManager.addMessage(category=category, subcategory=subcategory, symbolicName=symbolicName, displayName=displayName, default=default, doc=doc)
	
def getAccessor(subcategory, category="Messages"):
	"""Get an accessor for a particular category and subcategory."""
	return messagesManager.getAccessor(category=category, subcategory=subcategory)