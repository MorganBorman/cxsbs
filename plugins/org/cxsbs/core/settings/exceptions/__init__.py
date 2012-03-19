import pyTensible

class exceptions(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = 	{
							'InvalidSettingReference': InvalidSettingReference, 
							'InvalidSettingRepresentation': InvalidSettingRepresentation, 
							'InvalidSettingValue': InvalidSettingValue,
							'InvalidSettingType': InvalidSettingType,
							'InvalidSettingUninitialized': InvalidSettingUninitialized,
						}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
class InvalidSettingReference(Exception):
	'''Invalid Setting Reference. Raised when a setting or setting namespace does not exist.'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidSettingRepresentation(Exception):
	'''Invalid Setting Representation. Raised when a setting raw_value is assigned which cannot be read as expected by the setting object.'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidSettingValue(Exception):
	'''Invalid Setting Representation. Raised when a setting value is assigned a value of the wrong type.'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidSettingType(Exception):
	'''Invalid Setting Representation. Raised when a setting value is assigned a value of the wrong type.'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidSettingUninitialized(Exception):
	'''The setting has not been initialized with this store.'''
	def __init__(self, value=''):
		Exception.__init__(self, value)