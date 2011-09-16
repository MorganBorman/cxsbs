import os, imp, sys

from Manifest import Manifest, MalformedManifest
from Plugin import Plugin, MalformedPlugin
from Errors import *

manifestFilename = "plugin.manifest"

class PluginLoader:
	def __init__(self):
		self.manifests = {}
		self.pluginObjects = {}
		self.plugins = {}
		self.failed = []
			
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
				print "Ignore plugin:", manifest.Name, "-- unsatisfied dependency:", e
			except UnavailableResource, e:
				print "Failed plugin:", manifest.Name, "-- unsatisfied dependency:", e
			except MalformedPlugin, e:
				print "Failed plugin:", manifest.Name, "-- failed loading dependency:", e
			except FailedDependency, e:
				print "Failed plugin:", manifest.Name, "-- dependency previously failed to load:", e
			except InvalidResourceComponent, e:
				print "Failed plugin:", manifest.Name, "Required resource:", e.resource, "did not provide a valid", e.componentType, e.component
		
		sys.path.remove(pluginPath)
			
	def loadPlugin(self, symbolicName, version):
		try:
			manifest = self.manifests[symbolicName]
		except KeyError:
			self.failed.append(symbolicName)
			raise UnsatisfiedDependency(symbolicName + ":" + version)
		
		if version != manifest.Version:
			self.failed.append(manifest.SymbolicName)
			raise UnsatisfiedDependency(symbolicName + ":" + version)
		
		if not manifest.SymbolicName in self.plugins.keys():
			#plugin still needs to be loaded
			
			for dependencySymbolicName, dependencyVersion in manifest.Dependencies:
				if dependencySymbolicName in self.failed:
					self.failed.append(manifest.SymbolicName)
					raise FailedDependency(dependencySymbolicName)
				self.loadPlugin(dependencySymbolicName, dependencyVersion)
			
			pluginModule = __import__(manifest.SymbolicName)
			try:
				pluginObjectClass = pluginModule.__getattribute__(manifest.SymbolicName)
			except AttributeError:
				self.failed.append(manifest.SymbolicName)
				raise MalformedPlugin(manifest.SymbolicName + ": class is not present.")
			
			if not issubclass(pluginObjectClass, Plugin):
				self.failed.append(manifest.SymbolicName)
				raise MalformedPlugin(manifest.SymbolicName + ": is not derived from Plugin.")
			
			self.pluginObjects[manifest.SymbolicName] = pluginObjectClass()
			self.plugins[manifest.SymbolicName] = pluginModule
			
			print "Loaded plugin:", manifest.Name
			self.pluginObjects[manifest.SymbolicName].load()
			
	def getResource(self, symbolicName):
		try:
			return self.plugins[symbolicName]
		except KeyError:
			raise UnavailableResource(symbolicName)