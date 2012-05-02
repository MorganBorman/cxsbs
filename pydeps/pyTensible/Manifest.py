# Manifest.py
# A class which deals with loading of plug-in manifests.
# Copyright (c) 2012 Morgan Borman
# E-mail: morgan.borman@gmail.com

# This software is licensed under the terms of the Zlib license.
# http://en.wikipedia.org/wiki/Zlib_License

"""
TODO: 	This class needs to have an interface defined and have the properties
		of the Manifest objects provided using the @property decorator to make
		them read only.
"""

import ConfigParser
import Dependency

filename = "manifest.mf"

class MalformedManifest(Exception):
	'''Invalid manifest form'''
	def __init__(self, value=''):
		Exception.__init__(self, value)

class Manifest(object):
	'''
	A class which pulls the fields out of the manifests and stores them as public class attributes.
	It is expected that these attributes will be read but not modified.
	'''
	symbolic_name = ""
	defines = False
	version = None
	author = None
	enabled = False
	
	requests = None
	interfaces_provided = None
	resources_provided = None
	interfaces_implemented = None
	dependencies = None
	
	def __init__(self, manifest_path, expected_namespace):
		
		self.requests = []
		self.interfaces_provided = []
		self.resources_provided = []
		self.interfaces_implemented = []
		self.dependencies = []
		
		self.manifest_path = manifest_path
		
		manifest = ConfigParser.RawConfigParser(allow_no_value=True)

		#Remove case insensitivity from the key part of the ConfigParser
		manifest.optionxform = str
		manifest.read(self.manifest_path)
		
		self.symbolic_name = manifest.get("Plug-in", "SymbolicName")
		
		if self.symbolic_name != '.'.join(expected_namespace):
			raise MalformedManifest("Plug-in stated SymbolicName, '%s', does match expected namespace of '%s'." % (self.symbolic_name, '.'.join(expected_namespace)))
		
		self.version = manifest.get("Plug-in", "Version")
		self.author = manifest.get("Plug-in", "Author")
		self.enabled = manifest.get("Plug-in", "Enabled") == "True"
		
		######################################################################
		########################## Read Interfaces ###########################
		######################################################################
		'''
		These specify which interfaces this plug-in will provide.
		'''
		try:
			interfaces_provided = manifest.items("Interfaces")
		except:
			interfaces_provided = {}
		
		for interface_name, temp in interfaces_provided: #@UnusedVariable
			if '.' in interface_name:
				raise MalformedManifest("Names of interfaces provided may not have '.' in them.")
			self.interfaces_provided.append(interface_name)
			
		######################################################################
		########################## Read Resources ############################
		######################################################################
		'''
		These specify which resources this plug-in will provide and possibly which 
		interfaces each implements.
		'''
		try:
			resources_provided = manifest.items("Resources")
		except:
			resources_provided = {}
		
		for resource_description, temp in resources_provided: #@UnusedVariable
			
			#returns a dictionary {'resource_symbolic_name': resource_symbolic_name, 'resource_interface': resource_interface, 'resource_type': resource_type}
			resource_provided = self._process_resource_provided(resource_description)
			
			if '.' in resource_provided['resource_symbolic_name']:
				raise MalformedManifest("Names of resources provided may not have '.' in them.")
			
			self.resources_provided.append(resource_provided)
			
		######################################################################
		########################## Read Implements ###########################
		######################################################################
		'''
		These specify which externally provided interfaces the resources
		provided by this plug-in will implement.
		
		This tells the plug_in loader to make Accessors available for these
		prior to actually importing the plug-in.
		'''
		try:
			interfaces_implemented = manifest.items("Implements")
		except:
			interfaces_implemented = {}
		
		for dependency_name, dependency_string in interfaces_implemented:
			dependency_namespace = dependency_name.split('.')
		
			if len(dependency_namespace) < 2:
				raise MalformedManifest("The interface dependency specified '%s' is to short to have an enclosing namespace and an interface name." %dependency_name)
			
			enclosing_namespace = dependency_namespace[:-1]
			
			dependency_name = '.'.join(enclosing_namespace)
			
			dependency = Dependency.Dependency(dependency_name, dependency_string)
			self.interfaces_implemented.append(dependency)
		
		######################################################################
		######################### Read Dependencies ##########################
		######################################################################
		'''
		These specify basic single plug-in dependencies.
	
		Used when a plug-in will use pluginLoader.get_resource(symbolic_name)
		'''
		try:
			dependencies = manifest.items("Dependencies")
		except:
			dependencies = {}
		
		for dependency_name, dependency_string in dependencies:
			dependency = Dependency.Dependency(dependency_name, dependency_string)
			self.dependencies.append(dependency)
			
		######################################################################
		########################### Read Requests ############################
		######################################################################
		'''
		These specify that we want things which implement the given interface 
		to be loaded before this plug-in is.
		
		Used when a plug-in will use pluginLoader.get_providers(interface)
		'''
		try:
			requests = manifest.items("Requests")
		except:
			requests = {}
		
		for request_name, request_string in requests:
			request = Dependency.Dependency(request_name, request_string)
			self.requests.append(request)
		
	def _process_resource_provided(self, description):
		'''returns a dictionary {'resource_symbolic_name': resource_symbolic_name, 'resource_interface': resource_interface, 'resource_type': resource_type}'''
		
		resource_symbolic_name = ""
		resource_interface = None
		resource_type = None
		
		if description.find('(') != -1:
			resource_type = object
			
			interface_start = description.find('(')
			interface_end = description.find(')')
			
			if interface_start == 0:
				raise MalformedManifest("Found zero length resource name in resource description '%s'" % description)
			
			resource_symbolic_name = description[:interface_start]
			
			if interface_end == -1:
				raise MalformedManifest("Found no closing parenthesis in resource description '%s'" % description)
			
			resource_interface = description[interface_start+1:interface_end]
			
		elif description.find('[') != -1:
			resource_type = type
			
			interface_start = description.find('[')
			interface_end = description.find(']')
			
			if interface_start == 0:
				raise MalformedManifest("Found zero length resource name in resource description '%s'" % description)
			
			resource_symbolic_name = description[:interface_start]
			
			if interface_end == -1:
				raise MalformedManifest("Found no closing parenthesis in resource description '%s'" % description)
			
			resource_interface = description[interface_start+1:interface_end]
		else:
			resource_symbolic_name = description
		
		return {'resource_symbolic_name': resource_symbolic_name, 'resource_interface': resource_interface, 'resource_type': resource_type}