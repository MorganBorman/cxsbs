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
	
class NotSpecified:
	pass
	
class Setting(object):
	
	def __init__(self, category, subcategory, symbolicName, displayName, default, writeBackDefault=None, value=NotSpecified, writeBack=NotSpecified, doc=""):
		self.category = category
		self.subcategory = subcategory
		self.symbolicName = symbolicName
		self.displayName = displayName
		
		self.default = default
		if value == NotSpecified:
			self.value = default
		else:
			self.value = value
		
		self.writeBackDefault = writeBackDefault
		if writeBack == NotSpecified:
			self.writeBack = writeBackDefault
		else:
			self.writeBack = writeBack
			
		self.dirty = False
		
		self.doc = doc
		
	def getDisplayName(self):
		"""Get the setting's display name"""
		return self.displayName
		
	def getSymbolicName(self):
		"""Get the setting's symbolicName"""
		return self.symbolicName
		
	def getValue(self):
		"""Get the value of the setting"""
		return self.value
	
	def setValue(self, value):
		"""Set the value of the setting"""
		self.value = value
	
	def getCategory(self):
		"""Get the category of the setting"""
		return self.category
	
	def getSubcategory(self):
		"""Get the subcategory of the setting"""
		return self.subcategory
	
	def getWriteBackDefault(self):
		"""Get the default writeBack boolean for this setting"""
		return self.writeBackDefault
	
	def getWriteBack(self):
		"""Get the value of the writeBack boolean for this setting"""
		return self.writeBack
	
	def setWriteBack(self, writeBack):
		"""Set the value of the boolean writeBack"""
		if writeBack == None:
			self.writeBack = writeBack
		elif type(writeBack) == bool:
			self.writeBack = writeBack
		elif writeBack.lower() in ["yes", "true", "1"]:
			self.writeBack = True
		else:
			self.writeBack = False
	
	def getDefault(self):
		"""Get the default value of the setting"""
		return self.default
	
	def writeDefaultString(self):
		"""Get the string representation of the default value"""
		return str(self.default)
		
	def readString(self, string):
		"""Read a string representation of the value and store it"""
		self.value = str(string)
		
	def writeString(self):
		"""Get the string representation of this value to write back to the config file"""
		return str(self.value)
	
	def isDirty(self):
		"""Get whether or not the value has changed since it was last read from config or instantiated"""
		return self.dirty
	
	def setDirty(self, value):
		"""Set whether or not this setting is dirty"""
		self.dirty = value
		
class BoolSetting(Setting):
	def __init__(self, category, subcategory, symbolicName, displayName, default, writeBackDefault=None, value=NotSpecified, writeBack=NotSpecified, doc=""):
		Setting.__init__(self, category, subcategory, symbolicName, displayName, default, writeBackDefault, value, writeBack, doc)
		
	def readString(self, string):
		if type(string) == bool:
			self.value = string
		elif string.lower() in ["yes", "true", "1"]:
			self.value = True
		else:
			self.value = False
	
class IntSetting(Setting):
	def __init__(self, category, subcategory, symbolicName, displayName, default, writeBackDefault=None, value=NotSpecified, writeBack=NotSpecified, doc=""):
		Setting.__init__(self, category, subcategory, symbolicName, displayName, default, writeBackDefault, value, writeBack, doc)
		
	def readString(self, string):
		self.value = int(string)
	
import string
	
class TemplateSetting(Setting):
	def __init__(self, category, subcategory, symbolicName, displayName, default, writeBackDefault=None, value=NotSpecified, writeBack=NotSpecified, doc=""):
		Setting.__init__(self, category, subcategory, symbolicName, displayName, default, writeBackDefault, value, writeBack, doc)
		self.templateValue = string.Template(self.value)
		
	def getValue(self):
		return self.templateValue
		
	def setValue(self, stringValue):
		self.value = stringValue
		self.templateValue = string.Template(self.value)
		
	def readString(self, stringValue):
		self.value = stringValue
		self.templateValue = string.Template(self.value)
		
class ListSetting(Setting):
	def __init__(self, category, subcategory, symbolicName, displayName, default, writeBackDefault=None, value=NotSpecified, writeBack=NotSpecified, doc=""):
		Setting.__init__(self, category, subcategory, symbolicName, displayName, default, writeBackDefault, value, writeBack, doc)
		
	def writeDefaultString(self):
		return ','.join(self.default)
		
	def readString(self, string):
		self.value = string.split(',')
		
	def writeString(self):
		return ','.join(self.value)