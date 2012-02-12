"""
A file based settings management infrastructure. With a simple interface.

1) Initialize and add settings objects to the the setting manager
2) Get an accessor for your settings to make accessing the settings simpler in-code
3) Profit :)
"""

############################################################################
"""One might be interested in changing these"""
############################################################################
# Set this to the directory inside each instance folder that you wish to 
# keep your settings files in.
instance_config_foldername = "/config"

# Set this to what you want config file names to end with.
configuration_extension = '.conf'

############################################################################
"""Don't modify below here"""
############################################################################

import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global settingsManager
		settingsManager = SettingsManager()
		
	def reload(self):
		pass
		
	def unload(self):
		pass

import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
Setting = cxsbs.getResource("Setting")

import CategoryConfig
import traceback
import os

configuration_path = ServerCore.instanceRoot() + instance_config_foldername

try:
	os.makedirs(os.path.abspath(configuration_path))
except OSError:
	pass
	
class Accessor:
	'''Thin interface to the settingsManager to clean up getting/setting of settings for a particular plugin'''
	def __init__(self, settingsManager, category, subcategory):
		self.settingsManager = settingsManager
		self.category = category
		self.subcategory = subcategory
	
	def __str__(self):
		print "<"+"SettingsManager['"+self.category+"']['"+self.subcategory+"'] Accessor>"
	
	def __getitem__(self, key):
		return self.settingsManager.getValue(self.category, self.subcategory, key)
	
	def __setitem__(self, key, value):
		self.settingsManager.setValue(self.category, self.subcategory, key, value)
	
class SettingsManager(object):
	def __init__(self):
		#triply nested dictionary
		#[category][subcategory][symbolicName] = setting
		self.categories = {}
	
	def __checkCategories(self, category, subcategory):
		"""Check the the requisite dictionary structure is present so we can add the setting"""
		if not category in self.categories.keys():
			self.categories[category] = {}
			
		if not subcategory in self.categories[category].keys():
			self.categories[category][subcategory] = {}
			
	def __readSetting(self, setting):
		"""Opens configParser and reads a setting immediately then closes it"""
		config = CategoryConfig.CategoryConfig(configuration_path, setting.getCategory(), configuration_extension)
		value, writeBack = config.getOption(setting.getSubcategory(), setting.getSymbolicName(), setting.writeDefaultString(), setting.getWriteBackDefault())
		setting.readString(value)
		setting.setWriteBack(writeBack)
		setting.setDirty(False)
		del config
		
	def __readSettings(self):
		"""Reads all the settings from the files"""
		for category, subcategories in self.categories.items():
			config = CategoryConfig.CategoryConfig(configuration_path, category, configuration_extension)
			for subcategory, settings in subcategories.items():
				for setting in settings.values():
					value, writeBack = config.getOption(subcategory, setting.getSymbolicName(), setting.writeDefaultString(), setting.getWriteBackDefault())
					setting.readString(value)
					setting.setWriteBack(writeBack)
					setting.setDirty(False)
			del config
	
	def __writeSetting(self, setting):
		"""Opens configParser and write a setting immediately. Disregards writeBack and Dirty status'"""
		config = CategoryConfig.CategoryConfig(configuration_path, setting.getCategory(), configuration_extension)
		config.setOption(subcategory, setting.getSymbolicName(), setting.writeString(), setting.getWriteBack())
		del config
		
	def __writeSettings(self):
		"""Writes all settings for which setting.writeBack is True"""
		for category, subcategories in self.categories.items():
			config = CategoryConfig.CategoryConfig(configuration_path, category, configuration_extension)
			for subcategory, settings in subcategories.items():
				for setting in settings.values():
					if setting.getWriteBack() and setting.getDirty():
						config.setOption(subcategory, setting.getSymbolicName(), setting.writeString(), setting.getWriteBack())
						setting.setDirty(False)
			del config
	
	def addSetting(self, setting):
		if not isinstance(setting, Setting.Setting):
			cxsbs.Logging.logger.error("Attempt to add setting which is not an instance of Setting or it's subclasses.\n" + ''.join(traceback.format_stack()))
			
		if setting.doc == "":
			cxsbs.Logging.logger.warning("Setting lacks documentation: " + setting.symbolicName)
			
		self.__checkCategories(setting.getCategory(), setting.getSubcategory())
		self.categories[setting.getCategory()][setting.getSubcategory()][setting.getSymbolicName()] = setting
		
		self.__readSetting(setting)
	
	def getAccessor(self, category, subcategory):
		"""Returns an accessor to particular category and subcategory"""
		return Accessor(self, category, subcategory)
	
	def getValue(self, category, subcategory, symbolicName):
		"""Get the value of a setting by category subcategory and symbolicName"""
		return self.categories[category][subcategory][symbolicName].getValue()
	
	def setValue(self, category, subcategory, symbolicName, value):
		"""Set the value of a setting by category subcategory and symbolicName"""
		self.categories[category][subcategory][symbolicName].setValue(value)
		self.categories[category][subcategory][symbolicName].setDirty(True)
		
	def synchronize(self, write):
		'''Synchronizes the current values of all settings to the config files.
		
		write: If false, re-reads all settings from the configs regardless of writeBack property of the various settings.
		'''
		if write:
			self.__writeSettings()
		
		self.__readSettings()

def addSetting(setting):
	"""Add a setting to the manager and read it's current value from the filesystem."""
	settingsManager.addSetting(setting)
	
def getAccessor(category, subcategory):
	"""Get an accessor for a particular category and subcategory."""
	return settingsManager.getAccessor(category, subcategory)

def restoreSettings():
	"""Reread configuration from filesystem."""
	settingsManager.synchronize(False)
	print "Settings were loaded from filesystem."
	
def syncronizeSettings():
	"""Syncronize those modified writeBack settings with the filesystem and re-read everything"""
	settingsManager.synchronize(True)
	print "Settings have been syncronized with filesystem."