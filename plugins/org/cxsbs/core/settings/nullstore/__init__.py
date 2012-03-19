"""A SettingStore which just provides the default settings when Settings are initialized."""

import pyTensible, org

class nullstore(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		Interfaces = {}
		Resources = {'NullStore': SettingStore}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

class SettingStore(org.cxsbs.core.settings.interfaces.ISettingStore):
	"""
	The interface which a settings storage location must present to be used by the Settings manager.
	"""
	
	_initialized_settings = []
	
	def __init__(self, config_object):
		pass
	
	@staticmethod
	def initialize_config(config_object):
		"""
		Initialize this SettingStore's config options with the main settings config file. This config object will later be passed as an argument to the __init__ method.
		This should be a @staticmethod.
		"""
		doc = "This is the NullStore it doesn't really do anything."
		
		null_option = config_object.getOption('org.cxsbs.settings.manager.nullstore.NullStore.no-options', None, doc)
	
	def initialize(self, setting_object):
		"""
		Initialize a setting in this store.
		Should initialize the setting object if the setting is found, or build an entry in the store and leave the setting object in it's present state.
		"""
		self._initialized_settings.append(setting_object.symbolic_name)
		setting_object.value = setting_object.default
	
	def write(self, setting_object):
		"""
		Write a settings current value to the store. 
		Raises a InvalidSettingUninitialized exception where the setting has not bee initialized with the store.
		"""
		if not setting_object.symbolic_name in self._initialized_settings:
			raise org.cxsbs.core.settings.exceptions.InvalidSettingUninitialized
	
	def read(self, setting_object):
		"""
		Read a settings current value from the store. 
		Raises a InvalidSettingUninitialized exception where the setting has not bee initialized with the store.
		"""
		if not setting_object.symbolic_name in self._initialized_settings:
			raise org.cxsbs.core.settings.exceptions.InvalidSettingUninitialized
		
		setting_object.value = setting_object.default