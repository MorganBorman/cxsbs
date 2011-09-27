import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
	
class Accessor:
	'''Thin interface to the settingsManager to clean up sending of messages for a particular plugin'''
	def __init__(self, messagesManager, category, subcategory):
		self.messagesManager = messagesManager
		self.category = category
		self.subcategory = subcategory
	
	def __str__(self):
		print "<"+"MessagesManager['"+self.category+"']['"+self.subcategory+"'] Accessor>"
	
	def sendMessage(self, symbolicName, group=None, dictionary=None):
		self.messagesManager.sendMessage(self.subcategory, symbolicName, group, dictionary, category)
		
	def sendPlayerMessage(self, symbolicName, p, dictionary=None):
		self.messagesManager.sendPlayerMessage(self.subcategory, symbolicName, p, dictionary, self.category)
	
class MessagesManager():
	def __init__(self, settingsManager):
		self.settingsManager = settingsManager
		self.dictionary = Colors.colordict
		self.dictionary.update(UI.UIDict)
		
	def addMessage(self, subcategory, symbolicName, displayName, default, doc, category="Messages"):
		template = Setting.TemplateSetting(self, category, subcategory, symbolicName, displayName, default, writeBackDefault=None, value=Setting.NotSpecified, writeBack=Setting.NotSpecified, doc)
		
	def __formMessage(self, subcategory, symbolicName, dictionary, category="Messages"):
		if dictionary == None:
			dictionary = self.dictionary
		else:
			dictionary.update(self.dictionary)
		
		try:
			messageTemplate = settingsManager.getValue(category, subcategory, symbolicName, dictionary)
		except KeyError:
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
			cxsbs.Logging.logger.error('Messages Framework: Attempt to send unknown message: ' + str(name))
			cxsbs.Logging.logger.error(traceback.format_exc())
			
		return messageTemplate.substitute(dictionary)
	
	def getAccessor(self, subcategory, category="Messages"):
		return Accessor(self, category, subcategory)
		
	def sendMessage(self, subcategory, symbolicName, group=None, dictionary=None, category="Messages"):
		if group == None:
			group = Players.AllPlayersGroup
			
			message = self.__formMessage(category, subcategory, symbolicName, dictionary)
			if message == '':
				return
		group.action("message", (message,))
		
	def sendPlayerMessage(self, subcategory, symbolicName, p, dictionary=None, category="Messages"):
		message = self.__formMessage(category, subcategory, symbolicName, dictionary)
		if message == '':
			return
		p.message(message)