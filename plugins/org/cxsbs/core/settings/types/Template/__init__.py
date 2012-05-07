import pyTensible, org, string

class Template(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		Interfaces = {}
		Resources = {'Setting': Setting}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

class Setting(org.cxsbs.core.settings.interfaces.ISetting):
	"""
	A string setting class. Should be the base class for all other settings, because it is stipulated that SettingStores deal with strings.
	"""
	
	_possessed_by = None
	_category = ""
	_symbolic_name = ""
	_value = ""
	_wbpolicy = ""
	_default_value = ""
	_default_wbpolicy = "never"
	__doc__ = "This is the default doc string."
	
	def __init__(self, category, symbolic_name, default_value, default_wbpolicy, doc):
		"""
		Initialize the Setting object.
		"""
		self._category = category
		
		self._symbolic_name = symbolic_name
		
		self._value = default_value
		self._wbpolicy = default_wbpolicy
		
		self._default_value = default_value
		self._default_wbpolicy = default_wbpolicy
		
		self._dirty = False
		
		self.__doc__ = doc
		
	@staticmethod
	def handles_type(data_type):
		return data_type == string.Template
	
	@property
	def possessed(self):
		"""
		Should be set by the SettingsManager when the setting is added.
		"""
		return self._possessed_by
	
	@possessed.setter
	def set_possessed(self, value):
		"""
		Set the manager object which will be in charge of this setting.
		"""
		self._possessed_by = value
	
	@property
	def category(self):
		"""
		Read only property.
		
		The general type of setting that this is.
		This should only be used to control where the setting is stored, not resolve naming conflicts.
		In a file based SettingStore this should map to separate configuration files.
		"""
		return self._category
	
	@property
	def symbolic_name(self):
		"""
		Read only property.
		
		The name of the setting for actually referencing the setting. 
		A namespace should be prepended where appropriate to indicate the association of the setting to the plug-in it belongs to.
		This is used exclusively to access the setting in the SettingStore, therefore it must be globally unique across all the plug-ins.
		"""
		return self._symbolic_name
	
	@property
	def doc(self):
		"""
		Read only property.
		
		The doc string to be written with the setting if supported by the store and to be printed by a documentation browser if one is loaded.
		
		Where necessary this can be stored as another setting under the symbolic name of the setting with "_doc" appended.
		"""
		return self.__doc__
	
	@property
	def default(self):
		"""
		Read only property.
		
		The default value of the setting.
		"""
		return self._default_value
	
	@property
	def raw_value(self):
		"""
		Reading or writing to this will clear the dirty flag for this setting.
		
		The value of the setting ready for storage as a plain string.
		Assigning a plain string to this will update the natural value from that representation if possible
		Or raise InvalidSettingRepresentation defined in org.cxsbs.core.settings.exceptions.
		"""
		self._dirty = False
		return self._value.template
	
	@raw_value.setter
	def raw_value(self, value):
		"""
		Set the value and change the dirty flag to False.
		"""
		self._value = string.Template(value)
		self._dirty = False
	
	@property
	def value(self):
		"""
		The current value of the setting in it's natural form.
		Assigning to this will update the natural value directly if the type is compatible 
		Or raise InvalidSettingValue defined in org.cxsbs.core.settings.exceptions.
		
		For performance reasons the value probably should be stored in it's natural form not the string representation.
		"""
		return self._value
	
	@value.setter
	def value(self, value):
		"""
		Set the value, change the dirty flag to True, and notify the manager which possesses this setting.
		"""
		self._value = value
		self._dirty = True
		
		if self._possessed_by != None:
			self._possessed_by.notify(self)
	
	@property
	def wbpolicy(self):
		"""
		This is stored along with the setting under the symbolic name of the setting with "_wbpolicy" appended.
		
		The write-back policy is a string indicating when or if changes to this setting should be written back to the store.
		The valid values for this are ('immediate', 'explicit', 'never') Of these the only one needing explanation is 'explicit'
		which means the value is only written back to the store when write() is called explicitly on the manager.
		"""
		return self._wbpolicy
	
	@wbpolicy.setter
	def set_wbpolicy(self, value):
		"""
		
		"""
		self._wbpolicy = value
	
	@property
	def dirty(self):
		"""
		Has the value of the setting changed since it was loaded.
		This cannot be changed directly. It is set to true by setting the value of the "value" property and reset to false by 
		setting the value of the "raw_value" property. (Assuming those attempts succeed of course.)
		"""
		return self._dirty