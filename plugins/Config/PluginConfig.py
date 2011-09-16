from ConfigParser import ConfigParser, NoOptionError, NoSectionError

import cxsbs
ServerCore = cxsbs.getResource("ServerCore")

import string

configuration_path = ServerCore.configdir()

# Set this to what you want config file names to end with
configuration_extension = '.conf'

##### DONT MODIFY BELOW HERE ######

class PluginConfig:
	'''Allows easy reading of configuration options from configuration files'''
	def __init__(self, plugin_name):
		'''Creates config reader for file plugin_name.conf'''
		self.is_modified = False
		self.parser = ConfigParser()
		self.plugin_name = plugin_name
		self.read = False
	def __del__(self):
		if self.is_modified:
			f = open(self.configPath(), 'w')
			self.parser.write(f)
		del self.parser
	def checkRead(self):
		if not self.read:
			self.read = True
			self.parser.read(self.configPath())
	def getOption(self, section, option, default, write_if_absent=True):
		'''
		Returns value of option if it is set.
		If the option does not exist the default value is written and
		returned.
		'''
		self.checkRead()
		try:
			return self.parser.get(section, option)
		except NoSectionError:
			if write_if_absent:
				self.parser.add_section(section)
		except NoOptionError:
			pass
		if write_if_absent:
			self.parser.set(section, option, default)
			self.is_modified = True
		return default
	def getIntOption(self, section, option, default, write_if_absent=True):
		'''
		Return the value just as getOption does but try and convert to integer
		'''
		return int(self.getOption(section, option, default, write_if_absent))
	def getTemplateOption(self, section, option, default, write_if_absent=True):
		'''
		Return the value just as getOption does but try and convert to template
		'''
		return string.template(self.getOption(section, option, default, write_if_absent))
	def getBoolOption(self, section, option, default, write_if_absent=True):
		'''
		Return the value just as getOption does but try and convert to a boolean
		'''
		option = self.getOption(section, option, default, write_if_absent)
		return option.lower() == "true" or option.lower() == "yes"
	def getAllOptions(self, section):
		'''
		Returns all options and their values in section.
		Returns a list of tuples with two items that are key/value pairs.
		'''
		self.checkRead()
		try:
			return self.parser.items(section)
		except NoSectionError:
			return []
	def configPath(self):
		return configuration_path + self.plugin_name + configuration_extension