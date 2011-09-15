import os, imp, sys

from Manifest import Manifest, MalformedManifest
from Plugin import Plugin, MalformedPlugin

manifestFilename = "plugin.manifest"

class PluginLoader:
	def __init__(self):
		self.manifests = {}
		self.pluginObjects = {}
		self.plugins = {}
			
	def scanManifests(self, pluginPath):
		self.manifests = {}
		
		pluginDirectories = os.listdir(pluginPath)
		
		for directory in pluginDirectories:
			
			pluginDirectory = pluginPath + '/' + directory
			manifestPath = pluginDirectory + '/' + manifestFilename
			
			if os.path.isdir(pluginDirectory) and os.path.exists(manifestPath):
				try:
					manifest = Manifest(pluginDirectory, manifestFilename)
					if manifest.Enabled:
						self.manifests[manifest.SymbolicName] = manifest
					else:
						print "Plugin disabled:", manifest.Name
				except MalformedManifest:
					print "Malformed plugin manifest:", manifestPath
			else:
				print "Cannot read plugin:", pluginDirectory
				
	def loadPlugins(self, pluginPath):
		if not os.path.isdir(pluginPath):
			raise InvalidPluginDirectory("Given path is not a directory: " + pluginPath)
		
		sys.path.append(pluginPath)
		
		self.scanManifests(pluginPath)
		
		for SymbolicName in self.manifests.keys():
			manifest = self.manifests[SymbolicName]
			try:
				self.loadPlugin(SymbolicName, manifest.Version)
			except UnsatisfiedDependency, e:
				print "Could not load", manifest.Name, "unsatisfied dependency:", e
		
		sys.path.remove(pluginPath)
			
	def loadPlugin(self, symbolicName, version):
		try:
			manifest = self.manifests[symbolicName]
		except KeyError:
			raise UnsatisfiedDependency(symbolicName + ":" + version)
		
		if version != manifest.Version:
			raise UnsatisfiedDependency(symbolicName + ":" + version)
		
		if not manifest.SymbolicName in self.plugins.keys():
			#plugin still needs to be loaded
			
			for dependencySymbolicName, dependencyVersion in manifest.Dependencies:
				self.loadPlugin(dependencySymbolicName, dependencyVersion)
			
			pluginModule = __import__(manifest.SymbolicName)
			try:
				pluginObjectClass = pluginModule.__getattribute__(manifest.SymbolicName)
			except KeyError:
				raise MalformedPlugin("pluginObjectClass missing.")
			
			if not issubclass(pluginObjectClass, Plugin):
				raise MalformedPlugin("pluginObjectClass must be derived from Plugin.")
			
			self.pluginObjects[manifest.SymbolicName] = pluginObjectClass()
			self.plugins[manifest.SymbolicName] = pluginModule
			
			self.pluginObjects[manifest.SymbolicName].load()
			
	def getResource(self, symbolicName):
		try:
			return self.plugins[symbolicName]
		except KeyError:
			raise UnavailableResource(symbolicName)
			
class InvalidPluginDirectory(Exception):
	'''Invalid plugin directory'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
			
class UnsatisfiedDependency(Exception):
	'''Unsatisfied dependency'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
			
class UnavailableResource(Exception):
	'''Unsatisfied dependency'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
			