import os, imp, sys, traceback

from Manifest import Manifest, MalformedManifest
from Plugin import Plugin, MalformedPlugin
from Errors import *
from Logging import logger

manifestFilename = "plugin.manifest"

class PluginLoader:
	def __init__(self):
		self.manifests = {}
		self.pluginObjects = {}
		self.plugins = {}
		self.providers = {}
		self.failed = []
		self.unloaded = False
		self.reloadOrder = [] #Used to reload the plugins in dependency order
			
	def scanManifests(self, pluginPath):
		self.manifests = {}
		
		pluginDirectories = os.listdir(pluginPath)
		
		for directory in pluginDirectories:
			
			pluginDirectory = pluginPath + '/' + directory
			manifestPath = pluginDirectory + '/' + manifestFilename
			
			if os.path.isdir(pluginDirectory) and os.path.exists(manifestPath):
				try:
					manifest = Manifest(pluginDirectory, manifestFilename)
					self.processManifest(manifest)
					
				except MalformedManifest:
					logger.error("Malformed plugin manifest: " + manifestPath)
			else:
				logger.error("Cannot read plugin: " + pluginDirectory)
				
	def processManifest(self, manifest):
		if manifest.Enabled:
	
			if manifest.Provides != None:
			
				if not manifest.Provides in self.providers.keys():
					self.providers[manifest.Provides] = {}
				self.providers[manifest.Provides][manifest.SymbolicName] = manifest
	
			self.manifests[manifest.SymbolicName] = manifest
		else:
			logger.info("Plugin disabled: " + manifest.Name)	
				
	def loadPlugins(self, pluginPath):
		if not os.path.isdir(pluginPath):
			raise InvalidPluginDirectory("Given path is not a directory: " + pluginPath)
		
		sys.path.append(pluginPath)
		
		self.scanManifests(pluginPath)
		
		for SymbolicName in self.manifests.keys():
			self.loadPlugin(SymbolicName, None, [])
		
		sys.path.remove(pluginPath)
		
	def unloadAll(self):
		if not self.unloaded:
			for pluginName, pluginObject in self.pluginObjects.items():
				try:
					pluginObject.unload()
					logger.info("Unloaded plugin: " + pluginName)
				except:
					exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
					logger.error("Uncaught exception occurred while unloading plugin: " + traceback.format_exc())
				
			self.unloaded = True
		
	def loadDependencies(self, manifest, dependList):
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
	
	def loadRequests(self, manifest, dependList):
		for request in manifest.Requests:
			for provider in self.getProviderManifests(request.requestName):
				#check if we have a cycle forming
				if provider.SymbolicName in dependList:
					#append the name here for showing the cycle in the exception
					dependList.append(provider.SymbolicName)
				
					self.failed.append(manifest.SymbolicName)
					raise DependencyCycle(str("->".join(dependList)))
			
				#skip ones that have previously failed to load
				if provider.SymbolicName in self.failed:
					logger.error(provider.Name + " a " + provider.Provides + " provider previously failed to load.")
				#else load the provider
				else: 
					try:
						self.loadPlugin(provider.SymbolicName, request, dependList)
					except UnsatisfiedDependency:
						logger.error(provider.Name + " a " + provider.Provides + " provider failed: missing dependencies.")
					except MalformedPlugin:
						logger.error(provider.Name + " a " + provider.Provides + " provider failed: malformed plugin.")
			
	def loadPlugin(self, symbolicName, dependency, dependList):
		#logger.debug("trying to load plugin: " + symbolicName)
		"""Wrapper to __loadPlugin to provide nested exception handline for all loading of plugins"""
		try:
			self.__loadPlugin(symbolicName, dependency, dependList)
		except UnsatisfiedDependency as e:
			logger.error("Ignore plugin: " + symbolicName + " -- unsatisfied dependency: " + str(e))
		except UnavailableResource as e:
			logger.error("Failed plugin: " + symbolicName + " -- unsatisfied dependency: " + str(e))
		except MalformedPlugin as e:
			logger.error("Failed plugin: " + symbolicName + " -- failed loading dependency: " + str(e))
		except FailedDependency as e:
			logger.error("Failed plugin: " + symbolicName + " -- dependency previously failed to load: " + str(e))
		except InvalidResourceComponent as e:
			logger.error("Failed plugin: " + symbolicName + " Required resource: " + e.resource + " did not provide a valid " + e.componentType + e.component)
		
	def __loadPlugin(self, symbolicName, dependency, dependList):
		#dependList holds the list of dependencies along the depth-first cross section of the tree. Used to find cycles.
		dependList = dependList[:]
		dependList.append(symbolicName)
		
		#get the manifest from the manifest list
		try:
			manifest = self.manifests[symbolicName]
		except KeyError:
			self.failed.append(symbolicName)
			raise UnsatisfiedDependency(symbolicName + ":" + dependency.dependencyString)
		
		#to check whether the dependency can actually be satisfied by loading this plugin
		if dependency != None:
			if dependency.satisfied(manifest.SymbolicName, manifest.Version):
				pass #dependency is satisfied
			else:
				self.failed.append(manifest.SymbolicName)
				raise UnsatisfiedDependency(symbolicName + ":" + dependency.dependencyString + ". Version present is: " + manifest.Version)
		
		#preliminary checks done. Start actually loading the plugin now
		if not manifest.SymbolicName in self.plugins.keys():
			
			#load the dependencies
			self.loadDependencies(manifest, dependList)
			
			#load the requests
			self.loadRequests(manifest, dependList)
			
			#import the plugin
			try:
				pluginModule = __import__(manifest.SymbolicName)
			except ImportError:
				exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
				logger.error('Uncaught exception occured in command handler.')
				logger.error(traceback.format_exc())
				raise MalformedPlugin(manifest.SymbolicName + ": failed to import.")
			
			#get the plugin class from the module
			try:
				#pluginObjectClass = pluginModule.__getattribute__(manifest.SymbolicName)
				pluginObjectClass = pluginModule.__getattribute__("Plugin")
			except AttributeError:
				self.failed.append(manifest.SymbolicName)
				raise MalformedPlugin(manifest.SymbolicName + ": class is not present.")
			
			#check that the plugin class is a subclass of Plugin
			if not issubclass(pluginObjectClass, Plugin):
				self.failed.append(manifest.SymbolicName)
				raise MalformedPlugin(manifest.SymbolicName + ": is not derived from Plugin.")
			
			#add the plugin object and plugin module to the correct dictionaries
			self.pluginObjects[manifest.SymbolicName] = pluginObjectClass()
			self.plugins[manifest.SymbolicName] = pluginModule
			
			#load the actual plugin
			self.pluginObjects[manifest.SymbolicName].load()
			logger.info("Loaded plugin: " + manifest.Name)
			self.reloadOrder.append(manifest.SymbolicName)
		else:
			pass
			#logger.debug("Already loaded: " + manifest.Name)
			
	def getResource(self, symbolicName):
		try:
			return self.plugins[symbolicName]
		except KeyError:
			raise UnavailableResource(symbolicName)
			
	def getProviderManifests(self, provides):
		try:
			return self.providers[provides].values()
		except KeyError:
			return []
