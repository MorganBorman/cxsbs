# Errors.py
# Various exceptions raised by or used in pyTensible
# Copyright (c) 2012 Morgan Borman
# E-mail: morgan.borman@gmail.com

# This software is licensed under the terms of the Zlib license.
# http://en.wikipedia.org/wiki/Zlib_License

"""
TODO: 	Create better doc-strings for these Exceptions and create a clearer
		explanation of which exceptions may be raised by pyTensible.
"""

class InvalidPluginDirectory(Exception):
	'''Invalid plugin directory'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
			
class UnsatisfiedDependency(Exception):
	'''Unsatisfied dependency'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class UnsatisfiedInterface(Exception):
	'''Unsatisfied interface'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class FailedDependency(Exception):
	'''Unsatisfied dependency'''
	def __init__(self, value=''):
		Exception.__init__(self, value)

class MalformedPlugin(Exception):
	'''Unsatisfied dependency'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
			
class DependencyCycle(Exception):
	'''Dependency cycle'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
			
class UnavailableResource(Exception):
	'''Unsatisfied dependency'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidResourceComponent(Exception):
	'''A resource component is invalid'''
	def __init__(self, resource, component, componentType):
		self.resource = resource
		self.component = component
		self.componentType = componentType
		
class MissingResourceComponent(InvalidResourceComponent):
	'''A resource component is missing'''
	def __init__(self, resource, component, componentType):
		InvalidResourceComponent.__init__(self, resource, component, componentType)