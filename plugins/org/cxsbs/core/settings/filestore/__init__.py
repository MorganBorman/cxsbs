"""A SettingStore which just provides the default settings when Settings are initialized."""

import pyTensible, org
from CategoryConfig import CategoryConfig
import os

class filestore(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		Interfaces = {}
		Resources = {'FileStore': SettingStore}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

class SettingStore(org.cxsbs.core.settings.interfaces.ISettingStore):
	"""
	The interface which a settings storage location must present to be used by the Settings manager.
	"""
	
	_initialized_settings = []
	_categories = {}
	
	def __init__(self, config_object):
		self._initialized_settings = []
		self._categories = {}
		
		self.extension = config_object.getOption('org.cxsbs.core.settings.filestore.FileStore.extension', ".conf", "")
		self.location = os.path.join(org.cxsbs.core.server.instance.root, config_object.getOption('org.cxsbs.core.settings.filestore.FileStore.location', "settings", ""))
		
		if not os.path.exists(self.location):
			os.makedirs(self.location)
			
	
	@staticmethod
	def initialize_config(config_object):
		"""
		Initialize this SettingStore's config options with the main settings config file. This config object will later be passed as an argument to the __init__ method.
		This should be a @staticmethod.
		"""
		doc = "What extension should be used for the settings files?"
		config_object.getOption('org.cxsbs.core.settings.filestore.FileStore.extension', ".conf", doc)
		
		doc = "Where should the setting files be stored relative to this instance?"
		config_object.getOption('org.cxsbs.core.settings.filestore.FileStore.location', "settings", doc)
		
	def finalize_initialization(self):
		"""
		Called after all settings have been initialized.
		"""
		for category, setting_object in self._categories.items():
			setting_object.flush()
	
	def initialize(self, setting_object):
		"""
		Initialize a setting in this store.
		Should initialize the setting object if the setting is found, or build an entry in the store and leave the setting object in it's present state.
		"""
		
		self._initialized_settings.append(setting_object.symbolic_name)
		if not setting_object.category in self._categories.keys():
			self._categories[setting_object.category] = CategoryConfig(self.location, setting_object.category, self.extension)
		
		setting_object.value = setting_object.default
		
		setting_object.raw_value = self._categories[setting_object.category].getOption(setting_object.symbolic_name, setting_object.raw_value, setting_object.doc)
		
		#self._categories[setting_object.category].flush()
	
	def write(self, setting_object):
		"""
		Write a settings current value to the store. 
		Raises a InvalidSettingUninitialized exception where the setting has not bee initialized with the store.
		"""
		if not setting_object.symbolic_name in self._initialized_settings:
			raise org.cxsbs.core.settings.exceptions.InvalidSettingUninitialized
		
		self._categories[setting_object.category].setOption(setting_object.symbolic_name, setting_object.raw_value, setting_object.doc)
	
	def read(self, setting_object):
		"""
		Read a settings current value from the store. 
		Raises a InvalidSettingUninitialized exception where the setting has not bee initialized with the store.
		"""
		if not setting_object.symbolic_name in self._initialized_settings:
			raise org.cxsbs.core.settings.exceptions.InvalidSettingUninitialized
		
		setting_object.value = setting_object.default
		setting_object.raw_value = self._categories[setting_object.category].getOption(setting_object.symbolic_name, setting_object.raw_value, setting_object.doc)