class InvalidPluginDirectory(Exception):
	'''Invalid plugin directory'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
			
class UnsatisfiedDependency(Exception):
	'''Unsatisfied dependency'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class FailedDependency(Exception):
	'''Unsatisfied dependency'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
			
class UnavailableResource(Exception):
	'''Unsatisfied dependency'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidResourceComponent(Exception):
	def __init__(self, resource, component, componentType):
		self.resource = resource
		self.component = component
		self.componentType = componentType
		
class MissingResourceComponent(InvalidResourceComponent):
	def __init__(self, resource, component, componentType):
		InvalidResourceComponent.__init__(self, resource, component, componentType)