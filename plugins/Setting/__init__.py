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
	
class Setting(object):
	def __init__(self, symbolicName, type, category, subcategory, default, writeBack, value):
		self.symbolicName = symbolicName
		self.type = type
		self.category = category
		self.subcategory = subcategory
		self.default = default
		self.writeBack = writeBack
		self.value = value