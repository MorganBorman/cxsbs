# Namespace.py
# A class which exists at the leaves of the namespace hierarchy and provides access to the itens which are
#  actually available inside each plug-in.
# Copyright (c) 2012 Morgan Borman
# E-mail: morgan.borman@gmail.com

# This software is licensed under the terms of the Zlib license.
# http://en.wikipedia.org/wiki/Zlib_License

'''
Namespace objects live at leaves of the namespace tree.

So 'com.example.Events' would be represented by namespace_dictionary['com']['example']['Events'] = Namespace({},{})
'''

class Namespace:
	__interfaces = {}
	__resources = {}
	
	def __init__(self, interfaces, resources):
		self.__interfaces = interfaces
		self.__resources = resources
		
	def __getattr__(self, name):
		#print self.__interfaces, self.__resources
		if name in self.__interfaces.keys():
			return self.__interfaces[name]
		elif name in self.__resources.keys():
			return self.__resources[name]
		else:
			raise AttributeError(name)
	
	def __setattr__(self, name, value):
		if name in ["_Namespace__interfaces", "_Namespace__resources"]:
			self.__dict__[name] = value
		else:
			raise AttributeError(name)
	
	def __delattr__(self, name):
		raise AttributeError(name)