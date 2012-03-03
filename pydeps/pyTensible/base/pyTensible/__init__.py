import os, sys, traceback, abc

from pyTensible.Manifest import Manifest, MalformedManifest
from pyTensible.Errors import * #@UnusedWildImport
import pyTensible.Logging as Logging
from pyTensible.Accessor import Accessor
from pyTensible.Namespace import Namespace

manifest_filename = "manifest.mf"

class IPlugin:
	"A base class for all plug-in objects."
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def load(self):
		"""Load the plugin."""
		return
	
	@abc.abstractmethod
	def unload(self):
		"""Unload the plugin."""
		return

class pyTensible(IPlugin):
	def __init__(self):
		IPlugin.__init__(self)
		
	def load(self, local_logger):
		
		plugin_loader = PluginLoader(local_logger)
		
		Interfaces = {'Plugin': IPlugin, 'IPluginLoader': IPluginLoader}
		Resources = {'plugin_loader': plugin_loader} #@UndefinedVariable
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass
	
class IPluginLoader:
	"The interface for a plug-in loader."
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractproperty
	def logger(self):
		"Access to the logger"
		pass
	
	@abc.abstractmethod
	def load_suppress_list(self, suppress_list=[]):
		"Provide a list of fully qualified plug-in SymbolicNames which should not be loaded from any plug-in directory."
		pass
	
	@abc.abstractmethod
	def load_plugins(self, plugin_path, local_suppress_list=[]):
		"Load all plug-ins (except those in the suppress list) from the specified directory."
		pass
	
	@abc.abstractmethod
	def get_resource(self, symbolic_name):
		"Get a resource or an Accessor to a namespace containing resources."
		pass
	
	@abc.abstractmethod
	def get_providers(self, interface):
		"Get all resources which implement this interface as a dictionary indexed by fully qualified symbolic_name."
		pass
	
	@abc.abstractmethod
	def unload_all(self):
		"Call the unload method on all plug-ins and remove them from the plug-in registry"
		pass

class PluginLoader(IPluginLoader):
	'''A class which handles loading of plug-directories and their associated class hierarchies.'''
	######################################################################
	######################### Public Attributes ##########################
	######################################################################
	
	@property
	def logger(self):
		return self._logger
	
	######################################################################
	######################### Private Attributes #########################
	######################################################################
	
	#The logger for this instance of the plug-in framework
	_logger = Logging.logger
	
	#This is the global list of symbolic_names which are ignored.
	#each is a fully qualified symbolic_name eg "com.example.Events"
	_suppress_list = []
	
	#This holds all the manifest objects
	#each is keyed by fully qualified symbolic_name eg self._manifests["com.example.Events"] = manifest
	_manifests = {}
	
	#These are the plug0in modules
	#each is keyed by a fully qualified symbolic_name eg self._plugin_modules["com.example.Events"] = plugin_module
	_plugin_modules = {}
	
	#These are the plug-in classes.
	#each is keyed by a fully qualified symbolic_name eg self._plugin_classes["com.example.Events"] = plugin_class
	_plugin_classes = {}
	
	#These are the plug-in objects
	#each is keyed by a fully qualified symbolic_name eg self._plugin_objects["com.example.Events"] = plugin_object
	_plugin_objects = {}
	
	#This dictionary holds the namespaces keyed by namespace components
	#self._namespace_hierarchy['com']['example']['Events'] = Namespace({},{})
	_namespace_hierarchy = {}
	
	#This is the main accessor all other accessors can be retreived from this one
	_namespace_accessor = None
	
	#This holds dictionaries of resources which implement specific interfaces, 
	#keyed as follows: self._provider_hierarchy['com.example.Events.IEventManager']['com.example.Events.event_manager'] = event_manager
	_provider_hierarchy = {}
	
	#this holds the manifests of each provider keyed by the fully qualified symbolic name
	#each is keyed by a fully qualified symbolic_name eg self._provider_manifests["com.example.IEvents"] = manifest
	_provider_manifests = {}
	
	#This is a list of plug-ins which have previously failed to load. Used to save time while loading.
	#each is a fully qualified symbolic_name eg "com.example.Events"
	_failed_list = []
	
	#Keep track of the plug-ins in dependency order. Useful for reloading and unloading in the correct order without recalculating it.
	#each is a fully qualified symbolic_name eg "com.example.Events"
	_load_order = []
	
	def __init__(self, local_logger):
		"If necessary set a local logger for this instance of the pluginLoader."
		
		self._supress_list = []
		self._manifests = {}
		self._plugin_modules = {}
		self._plugin_objects = {}
		self._namespace_hierarchy = {}
		self._namespace_accessor = Accessor([], self._namespace_hierarchy)
		self._providers = {}
		self._failed_list = []
		self._load_order = []
		self._provider_manifests = {}
		
		if local_logger != None:
			self.logger = local_logger
		
	######################################################################
	########################### Public methods ###########################
	######################################################################
	
	def load_suppress_list(self, suppress_list=[]):
		"Provide a list of plug-in SymbolicNames which should not be loaded from any plug-in directory."
		self._suppress_list.append(suppress_list[:])
	
	def load_plugins(self, plugins_path, local_suppress_list=[], ):
		"Load all plug-ins (except those in the suppress list) from the specified directory."
		self.logger.info('Loading plug-ins from: ' + plugins_path)
		
		if not os.path.isdir(plugins_path):
			raise InvalidPluginDirectory("Given path is not a directory: " + plugins_path)
		
		plugin_list = self._preprocess_plugins(plugins_path, [])
		
		self._load_plugins(plugins_path, plugin_list, local_suppress_list)
	
	def get_resource(self, symbolic_name):
		"Get the loaded plug-in object. This is the key to accessing resources provided by plug-ins."
		namespace = symbolic_name.split('.')
		
		if len(namespace) < 1:
			raise InvalidResourceComponent("The given namespace is invalid.")
		
		temp_accessor = self._namespace_accessor
		
		while len(namespace) > 0:
			namespace_component = namespace.pop(0)
			temp_accessor = temp_accessor.__getattr__(namespace_component)
		
		#return Accessor(namespace, self._namespace_hierarchy)
		return temp_accessor
	
	def get_providers(self, interface):
		"Get all loaded plug-in objects which implement this interface as a dictionary indexed by symbolic_name."
		pass
	
	def unload_all(self):
		"Call the unload method on all plug-ins."
		for plugin_namespace in reversed(self._load_order):
			self._plugin_objects[plugin_namespace].unload()
		
	######################################################################
	########################## Private methods ###########################
	######################################################################
	
	def _preprocess_plugins(self, plugins_path, namespace):
		"Finds all the plug-ins, calls _preprocess_plugin on each, and returns a list of the fully qualified symbolic_names"
		new_plugin_list = []
		
		for directory in os.listdir(plugins_path):
			sub_directory = os.path.join(plugins_path, directory)
			manifest_path = os.path.join(sub_directory, manifest_filename)
			
			if os.path.isdir(sub_directory):
				new_namespace = namespace[:]
				new_namespace.append(directory)
				
				if os.path.exists(manifest_path):
					#it's a plug-in
					#initializes the manifest, checks that the namespaces match, then adds the manifest to the manifests dictionary
					if self._preprocess_plugin(manifest_path, new_namespace):
						new_plugin_list.append('.'.join(new_namespace))
				else:
					#it's a sub-directory
					new_plugin_list += self._preprocess_plugins(sub_directory, new_namespace)
			else:
				if directory[:len("__init__.py")] != "__init__.py":
					self.logger.debug("Unknown file in plug-in directory: " + str(os.path.join(plugins_path, directory)))
				
		return new_plugin_list
	
	def _preprocess_plugin(self, manifest_path, new_namespace):
		#try:
		manifest = Manifest(manifest_path, new_namespace)
		if manifest.enabled:
			self._manifests[manifest.symbolic_name] = manifest
			
			for resource in manifest.resources_provided:
				resource_interface = resource['resource_interface']
				
				if resource_interface is not None:
					resource_interface_namespace = resource_interface.split('.')
					
					if len(resource_interface_namespace) < 2:
						fully_qualified_interface = manifest.symbolic_name + '.' + resource_interface
					else:
						fully_qualified_interface = resource_interface
						
					if fully_qualified_interface not in self._provider_manifests.keys():
						self._provider_manifests[fully_qualified_interface] = []
						
					self._provider_manifests[fully_qualified_interface].append(manifest)
			
		else:
			self.logger.info("plug-in disabled: " + manifest.symbolic_name)
		return True
		#except MalformedManifest:
		#	logger.error("Malformed plug-in manifest: " + manifest_path)
		#	return False
			
	def _load_plugins(self, plugins_path, plugin_list, local_suppress_list):
		
		for symbolic_name in plugin_list:
			depend_list = []
			self._load_plugin(plugins_path, symbolic_name, None, depend_list, self._suppress_list + local_suppress_list)
			
	def _load_plugin(self, plugins_path, symbolic_name, dependency, depend_list, suppress_list):
		#logger.debug("trying to load plug-in: " + symbolic_name)
		"""Wrapper to _process_plugin to provide nested exception handling for all loading of interfaces and plug-ins"""
		try:
			if not symbolic_name in suppress_list:
				self._process_plugin(plugins_path, symbolic_name, dependency, depend_list, suppress_list)
			else:
				self.logger.info("Ignore loading: " + symbolic_name + " -- present in suppress list.")
		except UnsatisfiedDependency as e:
			self.logger.error("Ignore loading: " + symbolic_name + " -- unsatisfied dependency: " + str(e))
		except UnavailableResource as e:
			self.logger.error("Failed loading: " + symbolic_name + " -- unsatisfied dependency: " + str(e))
		except MalformedPlugin as e:
			self.logger.error("Failed loading: " + symbolic_name + " -- failed loading dependency: " + str(e))
		except FailedDependency as e:
			self.logger.error("Failed loading: " + symbolic_name + " -- dependency previously failed to load: " + str(e))
		except InvalidResourceComponent as e:
			self.logger.error("Failed loading: " + symbolic_name + " required resource: " + e.resource + " did not provide a valid " + e.componentType + e.component)
			
	def _process_plugin(self, plugins_path, symbolic_name, dependency, depend_list, suppress_list):
		#depend_list holds the list of dependencies along the depth-first cross section of the tree. Used to find cycles.
		depend_list = depend_list[:]
		depend_list.append(symbolic_name)
		
		#get the manifest from the manifest list
		try:
			manifest = self._manifests[symbolic_name]
		except KeyError:
			self._failed_list.append(symbolic_name)
			raise UnsatisfiedDependency(symbolic_name + ":" + str(dependency.dependency_range))
		
		#to check whether the dependency can actually be satisfied by loading this plug-in
		if dependency != None:
			if dependency.satisfied(manifest.symbolic_name, manifest.version):
				pass #dependency is satisfied
			else:
				self._failed_list.append(manifest.symbolic_name)
				raise UnsatisfiedDependency(symbolic_name + ":" + dependency.dependency_range + ". version present is: " + manifest.version)
		
		if not manifest.symbolic_name in self._plugin_modules.keys():
			#load the dependencies
			self._load_dependencies(plugins_path, manifest, depend_list, suppress_list)
			
			#load the requests
			self._load_requests(plugins_path, manifest, depend_list, suppress_list)
			
			#load the interfaces implemented by resources in this plug-in
			interfaces_dictionary = self._load_interfaces(plugins_path, manifest, depend_list, suppress_list)
			
			#this is the dictionary of stuff that we give the plug-in for free at load time
			plugin_environment = {'abc': abc}
			
			plugin_environment.update(interfaces_dictionary)
			
			#import the plug-in
			try:
				#place the interface classes which this module implements into the __builtins__ module so they are available to subclass
				backups = replace_builtins(plugin_environment)
				
				#Actually load the plug-in's module
				plugin_module = self._load_plugin_module(plugins_path, manifest.symbolic_name)
				
				#add the interface classes from which the plug-in object was derived to the global scope of the plug-in
				#this makes it possible for later reference of static methods and things like this.
				plugin_module.__dict__.update(plugin_environment)
				
			except ImportError:
				exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	#@UnusedVariable
				self.logger.error('Uncaught exception occurred in plug-in.')
				self.logger.error(traceback.format_exc())
				raise MalformedPlugin(manifest.symbolic_name + ": failed to import.")
			finally:
				restore_builtins(backups)
				
			#get the plug-in class from the module
			try:
				
				class_name = manifest.symbolic_name.split('.')[-1]
				
				plugin_class = plugin_module.__getattribute__(class_name)
			except AttributeError:
				self._failed_list.append(manifest.symbolic_name)
				raise MalformedPlugin(manifest.symbolic_name + ": class is not present (%s)." % class_name)
			
			#check that the plug-in's class is a subclass of 'Plugin'
			if not issubclass(plugin_class, self.get_resource('pyTensible.Plugin')):
				self._failed_list.append(manifest.symbolic_name)
				raise MalformedPlugin(manifest.symbolic_name + ": is not derived from the pyTensible.Plugin class.")
				
			plugin_object = plugin_class()
			
			exported_resources = plugin_object.load()
			
			self._process_exported_resources(manifest, exported_resources)
			
			self._plugin_modules[manifest.symbolic_name] = plugin_module
			self._plugin_objects[manifest.symbolic_name] = plugin_object
			
			self._load_order.append(manifest.symbolic_name)
			
			self.logger.info("Loaded plug-in: " + manifest.symbolic_name)
		else:
			self.logger.debug("Already loaded: " + manifest.symbolic_name)
			
	def _load_plugin_module(self, plugins_path, symbolic_name):
		module_name = symbolic_name.split('.')[-1]
		sub_path = '/'.join(symbolic_name.split('.')[:-1])

		enclosing_namespace_path = os.path.join(plugins_path, sub_path)

		sys.path.append(enclosing_namespace_path)
		
		try:
			plugin_module = __import__(module_name)
			return plugin_module
		finally:
			sys.path.remove(enclosing_namespace_path)
			
	def _process_exported_resources(self, manifest, exported_resources):
		'''
		Checks that all the stated resources and interfaces have been exported and are of the correct types
		
		Then adds them to the correct hierarchies.
		'''
		
		namespace_hierarchy = manifest.symbolic_name.split('.')
		
		interfaces_exported = exported_resources['Interfaces']
		resources_exported = exported_resources['Resources']
		
		for interface in manifest.interfaces_provided:
			if not interface in interfaces_exported.keys():
				raise MalformedPlugin("The manifest states that the interface '%s' will be exported but it was not." %interface)
			
			#add_to_hierarchical_dictionary(namespace_hierarchy, interfaces_exported[interface], self._interface_hierarchy)
			
		for resource in manifest.resources_provided:
			if not resource['resource_symbolic_name'] in resources_exported.keys():
				raise MalformedPlugin("The manifest states that the resource '%s' will be exported but it was not." %resource['resource_symbolic_name'])
			
			resource_interface = resource['resource_interface']
			
			if resource_interface != None:
				if resource_interface in interfaces_exported.keys():
					interface = interfaces_exported[resource_interface]
				else:
					interface = self.get_resource(resource_interface)
					
				if resource['resource_type'] == type:
					if not issubclass(resources_exported[resource['resource_symbolic_name']], interface):
						raise MalformedPlugin("The manifest states that the resource class '%s' will implement the interface '%s' but it does not." %(resource['resource_symbolic_name'], interface))
				elif resource['resource_type'] == object:
					if not isinstance(resources_exported[resource['resource_symbolic_name']], interface):
						raise MalformedPlugin("The manifest states that the resource object '%s' will implement the interface '%s' but it does not." %(resource['resource_symbolic_name'], interface))
					
				#add_to_hierarchical_dictionary(namespace_hierarchy, resources_exported[resource['resource_symbolic_name']], self._resource_hierarchy)
				
		namespace = Namespace(interfaces_exported, resources_exported)
		add_to_hierarchical_dictionary(namespace_hierarchy, namespace, self._namespace_hierarchy)
				
	def _load_interfaces(self, plugins_path, manifest, depend_list, suppress_list):
		"Load the base plug-ins whose defined interfaces the specified plug-in claims to implement and return the dictionary of them keyed by their symbolicNames."
		interfaces_accessors = {}
		
		for interface_dependency in manifest.interfaces_implemented:
			dependency_namespace = interface_dependency.dependency_name.split('.')
			
			highest_namespace = dependency_namespace[0]
			
			#check if we have a cycle forming
			if interface_dependency.dependency_name in depend_list:
				#append the name here for showing the cycle in the exception
				depend_list.append(interface_dependency.dependency_name)
			
				self._failed_list.append(manifest.symbolic_name)
				raise DependencyCycle(str("->".join(depend_list)))
		
			#skip ones that have previously failed to load
			if interface_dependency.dependency_name in self._failed_list:
				self.logger.error("The plug-in providing the interface, " + interface_dependency.dependency_name + ", previously failed to load.")
			#else load the provider
			else:
				try:
					self._load_plugin(plugins_path, interface_dependency.dependency_name, interface_dependency, depend_list, suppress_list)
					
					interfaces_accessors[highest_namespace] = self.get_resource(highest_namespace)
					
				except KeyError:
					self.logger.error("Loading the interface, " + interface_dependency.dependency_name + " failed: unknown (interface missing from interfaces dictionary).")
					raise UnsatisfiedInterface(interface_dependency.dependency_name + " was not loaded correctly.")
				except UnsatisfiedDependency:
					self.logger.error("Loading the interface, " + interface_dependency.dependency_name + " failed: missing dependencies.")
				except MalformedPlugin:
					self.logger.error("Loading the interface, " + interface_dependency.dependency_name + " failed: malformed plug-in.")
		
		return interfaces_accessors
	
	def _load_dependencies(self, plugins_path, manifest, depend_list, suppress_list):
		for dependency in manifest.dependencies:
			#check if we have a cycle forming
			if dependency.dependency_name in depend_list:
				#append the name here for showing the cycle in the exception
				depend_list.append(dependency.dependency_name)
				
				self._failed_list.append(manifest.symbolic_name)
				raise DependencyCycle(str("->".join(depend_list)))
			
			#skip ones that have previously failed to load
			if dependency.dependency_name in self._failed_list:
				#add this one to the list of failed
				self._failed_list.append(manifest.symbolic_name)
				raise FailedDependency(dependency.dependency_name)
			#else load the plug-in
			else: 
				self._load_plugin(plugins_path, dependency.dependency_name, dependency, depend_list, suppress_list)
	
	def _load_requests(self, plugins_path, manifest, depend_list, suppress_list):
		for request in manifest.requests:
			for provider in self._get_provider_manifests(request.requestName):
				#check if we have a cycle forming
				if provider.symbolic_name in depend_list:
					#append the name here for showing the cycle in the exception
					depend_list.append(provider.symbolic_name)
				
					self._failed_list.append(manifest.symbolic_name)
					raise DependencyCycle(str("->".join(depend_list)))
			
				#skip ones that have previously failed to load
				if provider.symbolic_name in self._failed_list:
					self.logger.error(provider.name + " a " + provider.Provides + " provider previously _failed to load.")
				#else load the provider
				else: 
					try:
						self._load_plugin(plugins_path, provider.symbolic_name, None, depend_list, suppress_list)
					except UnsatisfiedDependency:
						self.logger.error(provider.name + " a " + provider.Provides + " provider failed: missing dependencies.")
					except MalformedPlugin:
						self.logger.error(provider.name + " a " + provider.Provides + " provider failed: malformed plug-in.")
						
	def _get_provider_manifests(self, provides):
		try:
			return self._provider_manifests[provides][:]
		except KeyError:
			return []
					
def add_to_hierarchical_dictionary(hierarchy, item, dictionary):
	hierarchy = hierarchy[:]
	key = hierarchy.pop(0)
	
	if len(hierarchy) > 0:
		if not key in dictionary.keys():
				dictionary[key] = {}
				
		add_to_hierarchical_dictionary(hierarchy, item, dictionary[key])
		
	else:
		dictionary[key] = item

def replace_builtins(replacements={}):
	"Places the items in the replacements dictionary and returns a backup dictionary of the replaced items if any."
	backups = {}
	for key in replacements.keys():
		if key in __builtins__.keys():
			backups[key] = __builtins__[key]
		__builtins__[key] = replacements[key]
			
	return backups

def restore_builtins(backups):
	"Restores the previously replaced __builtins__ with those in the provided backups dictionary."
	for key in backups.keys():
		__builtins__[key] = backups[key]