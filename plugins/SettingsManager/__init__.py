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
	
class Portal:
	def __init__(self, settingsManager, category, subcategory):
		self.settingsManager = settingsManager
		self.category = category
		self.subcategory = subcategory
	
	def __getattr__(self, name):
		pass
	
	def __setattr__(self, name, value):
		pass
	
class SettingsManager(object):
	def __init__(self):
		settings = {}
	
	def addSetting(self, setting):
		pass
	
	def getValue(self, category, subcategory, symbolicName):
		pass
		
	def syncronize(self, write=False):
		pass
	
	