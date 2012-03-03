import sys, os

from pyTensible.Namespace import Namespace

def bootstrap_pyTensible(local_logger=None):
	"""
	Bootstraps the pyTensible plug-in and returns the plugin_loader resource.
	"""
	base_path = os.path.join(os.path.dirname(__file__), 'base')
	
	import base.pyTensible as plugin_module
	plugin_class = plugin_module.pyTensible
	plugin_object = plugin_class()
	
	exported_resources = plugin_object.load(local_logger)
	
	plugin_loader = exported_resources['Resources']['plugin_loader']
	
	#insert the loaded plug-in stuff into the right dictionaries
	plugin_loader._plugin_modules['pyTensible'] = plugin_module
	plugin_loader._plugin_classes['pyTensible'] = plugin_class
	plugin_loader._plugin_objects['pyTensible'] = plugin_object
	
	plugin_loader._preprocess_plugins(base_path, [])
	
	plugin_loader._namespace_hierarchy['pyTensible'] = Namespace(exported_resources['Interfaces'], exported_resources['Resources'])
	
	plugin_loader._provider_hierarchy['pyTensible.IPluginLoader'] = {}
	plugin_loader._provider_hierarchy['pyTensible.IPluginLoader']['pyTensible.plugin_loader'] = plugin_loader
	
	plugin_loader._load_order.append('pyTensible')
	
	return plugin_loader