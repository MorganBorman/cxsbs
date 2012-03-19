"""
Based on PluginConfig.py by Greg Haynes. Heavily modified by Morgan Borman to be underlying
foundation for org.cxsbs.core.settings framework.
"""

from ConfigParser import RawConfigParser, NoOptionError, NoSectionError

class CategoryConfig:
	'''Allows easy reading of configuration options from configuration files'''
	def __init__(self, path, category, extension):
		'''Creates config reader for file path/category.extension'''
		self.is_modified = False
		self.parser = RawConfigParser(allow_no_value=True)
		self.parser.optionxform = str
		self.path = path
		self.category = category
		self.extension = extension
		self.read = False
		
	def __configPath(self):
		return self.path + '/' + self.category + self.extension
	
	def __del__(self):
		if self.is_modified:
			f = open(self.__configPath(), 'w')
			self.parser.write(f)
		del self.parser
		
	def __checkRead(self):
		if not self.read:
			self.read = True
			self.parser.read(self.__configPath())
			
	def getOption(self, symbolic_name, default_value, doc):
		'''
		Returns value of symbolic_name if it is set.
		If the symbolic_name does not exist the doc and default_value are written and
		the default_value is returned.
		'''
		
		self.__checkRead()
		
		value = None
		
		subcategory = '.'.join(symbolic_name.split('.')[:-1])
		
		if not self.parser.has_section(subcategory):
			self.parser.add_section(subcategory)
		
		try:
			value = self.parser.get(subcategory, symbolic_name)
		except NoOptionError:
			value = default_value
			self.parser.set(subcategory, '#' + doc)
			self.parser.set(subcategory, symbolic_name, default_value)
			self.is_modified = True
			
		return value
	
	def setOption(self, symbolic_name, value, doc):
		'''
		Writes the value to the indicated setting.
		'''
		
		subcategory = '.'.join(symbolic_name.split('.')[:-1])
		
		if not self.parser.has_section(subcategory):
			self.parser.add_section(subcategory)
			
		try:
			self.parser.get(subcategory, symbolic_name)
		except NoOptionError:
			self.parser.set(subcategory, '#' + doc)
			self.parser.set(subcategory, symbolic_name, value)
		else:
			self.parser.set(subcategory, symbolic_name, value)
		self.is_modified = True
		