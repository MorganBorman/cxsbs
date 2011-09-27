import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global messagesManager
		messagesManager = MessagesManager()
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
import cxsbs
UI = cxsbs.getResource("UI")
Colors = cxsbs.getResource("Colors")
Players = cxsbs.getResource("Players")
Config = cxsbs.getResource("Config")

import cxsbs.Logging
import sys, traceback

class MessagingModule:
	def __init__(self, config="Messages"):
		self.configHandle = Config.PluginConfig(config)
		self.dictionary = Colors.colordict
		self.dictionary.update(UI.UIDict)
		self.messages = {}
		
	def addMessage(self, name, text, section):
		self.messages[name] = self.configHandle.getTemplateOption(section, name, text)
		
	def finalize(self):
		del self.configHandle
		
	def formMessage(self, name, dictionary):
		if dictionary == None:
			dictionary = self.dictionary
		else:
			dictionary.update(self.dictionary)
		
		try:
			messageTemplate = self.messages[name]
		except KeyError:
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
			cxsbs.Logging.logger.error('MessageFramework: Attempt to send unknown message: ' + str(name))
			cxsbs.Logging.logger.error(traceback.format_exc())
			
		return self.messages[name].substitute(dictionary)
		
	def sendMessage(self, name, group=None, dictionary=None):
		if group == None:
			group = Players.AllPlayersGroup
			
			message = self.formMessage(name, dictionary)
			if message == '':
				return
		group.action("message", (message,))
		
	def sendPlayerMessage(self, name, p, dictionary=None):
		message = self.formMessage(name, dictionary)
		if message == '':
			return
		p.message(message)