from cxsbs.Plugin import Plugin

class MessageFramework(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
import cxsbs
Colors = cxsbs.getResource("Colors")
Players = cxsbs.getResource("Players")
Config = cxsbs.getResource("Config")

class MessagingModule:
	def __init__(self, config="Messages"):
		self.configHandle = Config.PluginConfig(config)
		self.dictionary = Colors.colordict
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
			
		return self.messages[name].substitute(dictionary)
		
	def sendMessage(self, name, group=None, dictionary=None):
		if group == None:
			group = Players.AllPlayersGroup
			
			message = self.formMessage(name, dictionary)
			
		group.action("message", (message,))
		
	def sendPlayerMessage(self, name, p, dictionary=None):
		message = self.formMessage(name, dictionary)
		p.message(message)