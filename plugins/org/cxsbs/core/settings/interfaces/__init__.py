import pyTensible, abc

class interfaces(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {'ISettingsManager': ISettingsManager,'ISettingStore': ISettingStore, 'ISetting': ISetting}
		Resources = {}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

class ISettingsManager:
	"""
	The interface with which settings are managed and accessed.
	"""
	
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def on_started(self, setting_object):
		"Called when the server starts. After all the plug-ins have loaded."
		pass
	
	@abc.abstractmethod
	def add(self, setting_object):
		"Add a setting object as managed and initializes it with the configured SettingStore."
		pass
	
	@abc.abstractmethod
	def reload(self):
		"Reload all added settings from the indicated SettingStore."
		pass
	
	@abc.abstractmethod
	def reset(self):
		"Revert all settings to their defaults. This may cause those settings with 'immediate' writeback policies to be stored."
		pass
	
	@abc.abstractmethod
	def writeback(self):
		"Request that this setting store all dirty settings whose policies do not forbid write-back."
		pass
	
	@abc.abstractmethod
	def notify(self, setting_object):
		"""
		Used by a setting object whose 'possess' feild has been populated, to notify the SettingsManager that a change has occurred.
		And to take action as necessary with respect to the writeback policy of the setting.
		
		Setting objects should do this even if their values never get written back.
		"""
		pass

class ISettingStore:
	"""
	The interface which a settings storage location must present to be used by the Settings manager.
	"""
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def __init__(self, config_object):
		"""
		Read the appropriate settings from the config_object and get ready to read and write settings.
		"""
		pass
	
	@abc.abstractmethod
	def initialize_config(config_object):
		"""
		Initialize this SettingStore's config options with the main settings config file. This config object will later be passed as an argument to the __init__ method.
		This should be a @staticmethod.
		"""
		pass
	
	@abc.abstractmethod
	def finalize_initialization(self):
		"""
		Called after all settings have been initialized.
		"""
		pass
	
	@abc.abstractmethod
	def initialize(self, setting_object):
		"""
		Initialize a setting in this store.
		Should initialize the setting object if the setting is found, or build an entry in the store and leave the setting object in it's present state.
		"""
		pass
	
	@abc.abstractmethod
	def write(self, setting_object):
		"""
		Write a settings current value to the store. 
		Raises a InvalidSettingUninitialized exception where the setting has not bee initialized with the store.
		"""
		pass
	
	@abc.abstractmethod
	def read(self, setting_object):
		"""
		Read a settings current value from the store. 
		Raises a InvalidSettingUninitialized exception where the setting has not bee initialized with the store.
		"""
		pass
	
class ISetting:
	"""
	The interface which a setting must present to be used by the Settings manager.
	"""
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def handles_type(data_type):
		"""
		A staticmethod that returns a boolean indicating whether or not this setting container can store the specified data type.
		"""
		pass
	
	@abc.abstractmethod
	def __init__(self, category, symbolic_name, display_name, default_value, default_wbpolicy, doc):
		"""
		Initialize the Setting object.
		"""
		pass
	
	@abc.abstractproperty
	def possessed(self):
		"""
		Should be set by the SettingsManager when the setting is added.
		"""
		pass
	
	@abc.abstractproperty
	def category(self):
		"""
		Read only property.
		
		The general type of setting that this is.
		This should only be used to control where the setting is stored, not resolve naming conflicts.
		In a file based SettingStore this should map to separate configuration files.
		"""
		pass
	
	@abc.abstractproperty
	def symbolic_name(self):
		"""
		Read only property.
		
		The name of the setting for actually referencing the setting. 
		A namespace should be prepended where appropriate to indicate the association of the setting to the plug-in it belongs to.
		This is used exclusively to access the setting in the SettingStore, therefore it must be globally unique across all the plug-ins.
		"""
		pass
	
	@abc.abstractproperty
	def display_name(self):
		"""
		Read only property.
		
		The name of the setting for printing.
		
		Where necessary this can be stored as another setting under the symbolic name of the setting with "_display" appended.
		"""
		pass
	
	@abc.abstractproperty
	def doc(self):
		"""
		Read only property.
		
		The doc string to be written with the setting if supported by the store and to be printed by a documentation browser if one is loaded.
		
		Where necessary this can be stored as another setting under the symbolic name of the setting with "_doc" appended.
		"""
		pass
	
	@abc.abstractproperty
	def default(self):
		"""
		Read only property.
		
		The default value of the setting."""
		pass
	
	@abc.abstractproperty
	def raw_value(self):
		"""
		The value of the setting ready for storage as a plain string.
		Assigning a plain string to this will update the natural value from that representation if possible
		Or raise InvalidSettingRepresentation defined in org.cxsbs.core.settings.exceptions.
		"""
		pass
	
	@abc.abstractproperty
	def value(self):
		"""
		The current value of the setting in it's natural form.
		Assigning to this will update the natural value directly if the type is compatible 
		Or raise InvalidSettingValue defined in org.cxsbs.core.settings.exceptions.
		
		For performance reasons the value probably should be stored in it's natural form not the string representation.
		"""
		pass
	
	@abc.abstractproperty
	def wbpolicy(self):
		"""
		This is stored along with the setting under the symbolic name of the setting with "_wbpolicy" appended.
		
		The write-back policy is a string indicating when or if changes to this setting should be written back to the store.
		The valid values for this are ('immediate', 'explicit', 'never') Of these the only one needing explanation is 'explicit'
		which means the value is only written back to the store when write() is called explicitly on the manager.
		"""
		pass
	
	@abc.abstractproperty
	def dirty(self):
		"""
		Has the value of the setting changed since it was loaded.
		This cannot be changed directly. It is set to true by setting the value of the "value" property and reset to false by 
		setting the value of the "raw_value" property. (Assuming those attempts succeed of course.)
		"""
		pass