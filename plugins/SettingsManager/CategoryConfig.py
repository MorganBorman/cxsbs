"""
Based on PluginConfig.py by Greg Haynes. Heavily modified by Morgan Borman to be underlying
foundation for CXSBS SettingsManager framework.
"""

from ConfigParser import ConfigParser, NoOptionError, NoSectionError

class CategoryConfig:
	'''Allows easy reading of configuration options from configuration files'''
	def __init__(self, path, category, extension):
		'''Creates config reader for file path/category.extension'''
		self.is_modified = False
		self.parser = ConfigParser()
		self.path = path
		self.category = category
		self.extension = extension
		self.read = False
	def __configPath(self):
		return self.path + '/' + self.category + '.' + self.extension
	def __del__(self):
		if self.is_modified:
			f = open(self.__configPath(), 'w')
			self.parser.write(f)
		del self.parser
	def __checkRead(self):
		if not self.read:
			self.read = True
			self.parser.read(self.__configPath())
	def getOption(self, subcategory, symbolicName, default, writeBackDefault=None):
		'''
		Returns value of symbolicName if it is set.
		If the symbolicName does not exist the default value is written and
		returned.
		'''
		self.__checkRead()
		
		value = None
		writeBack = None
		
		if not self.parser.has_section(subcategory):
			self.parser.add_section(subcategory)
		
		try:
			value = self.parser.get(subcategory, symbolicName)
		except NoOptionError:
			value = default
			self.parser.set(subcategory, symbolicName, default)
			self.is_modified = True
		
		
		if writeBackDefault != None:
			try:
				writeBack = self.parser.get(subcategory, "write_back_" + symbolicName)
			except NoOptionError:
				writeBack = writeBackDefault 
				self.parser.set(subcategory, "write_back_" + symbolicName, writeBackDefault)
				self.is_modified = True
		else:
			writeBack = None
			
		return (value, writeBack)
	
	def setOption(self, subcategory, symbolicName, value, writeBack=None):
		'''
		Writes the value to the indicated setting.
		
		if writeBack is None then don't write that setting, otherwise convert to string and write out.
		'''
		if not self.parser.has_section(subcategory):
			self.parser.add_section(subcategory)
			
		self.parser.set(subcategory, symbolicName, value)
		
		if writeBack != None:
			self.parser.set(subcategory, "write_back_" + symbolicName, str(writeBack))
		