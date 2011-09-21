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
				self.loadPlugin(SymbolicName, None, [])
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
			
	def loadPlugin(self, symbolicName, dependency, dependList):
		#dependList holds the list of dependencies along the depth-first cross section of the tree. Used to find cycles.
		dependList = dependList[:]
		dependList.append(symbolicName)
		
		#get the manifest from the manifest list
		try:
			manifest = self.manifests[symbolicName]
		except KeyError:
			self.failed.append(symbolicName)
			raise UnsatisfiedDependency(symbolicName + ":" + dependency.dependencyString)
		
		if dependency != None:
			if dependency.satisfied(manifest.SymbolicName, manifest.Version):
				pass #dependency is satisfied
			else:
				self.failed.append(manifest.SymbolicName)
				raise UnsatisfiedDependency(symbolicName + ":" + dependency.dependencyString + ". Version present is: " + manifest.Version)
		
		#plugin still needs to be loaded
		if not manifest.SymbolicName in self.plugins.keys():
			
			#load the dependencies
			for dependency in manifest.Dependencies:
				#check if we have a cycle forming
				if dependency.dependencyName in dependList:
					#append the name here for showing the cycle in the exception
					dependList.append(dependency.dependencyName)
					
					self.failed.append(manifest.SymbolicName)
					raise DependencyCycle(str("->".join(dependList)))
				
				#skip ones that have previously failed to load
				if dependency.dependencyName in self.failed:
					#add this one to the list of failed
					self.failed.append(manifest.SymbolicName)
					raise FailedDependency(dependency.dependencyName)
				#else load the plugin
				else: 
					self.loadPlugin(dependency.dependencyName, dependency, dependList)
			
			#import the plugin
			pluginModule = __import__(manifest.SymbolicName)
			
			#get the plugin class from the module
			try:
				pluginObjectClass = pluginModule.__getattribute__(manifest.SymbolicName)
			except AttributeError:
				self.failed.append(manifest.SymbolicName)
				raise MalformedPlugin(manifest.SymbolicName + ": class is not present.")
			
			#check that the plugin class is a subclass of Plugin
			if not issubclass(pluginObjectClass, Plugin):
				self.failed.append(manifest.SymbolicName)
				raise MalformedPlugin(manifest.SymbolicName + ": is not derived from Plugin.")
			
			self.pluginObjects[manifest.SymbolicName] = pluginObjectClass()
			self.plugins[manifest.SymbolicName] = pluginModule
			
			self.pluginObjects[manifest.SymbolicName].load()
			print "Loaded plugin:", manifest.Name
			
	def getResource(self, symbolicName):
		try:
			return self.plugins[symbolicName]
		except KeyError:
			raise UnavailableResource(symbolicName)