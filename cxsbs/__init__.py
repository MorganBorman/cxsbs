import PluginLoader
import sys, os, signal
import sbserver
import Logging

Logging.logger.info("#"*50)
Logging.logger.info('Server starting...')
Logging.logger.info("#"*50)

pydepsPath = os.path.abspath("pydeps/")
sys.path.append(pydepsPath)

pluginLoader = PluginLoader.PluginLoader()

def loadPlugins(pluginPath):
	Logging.logger.info("#"*50)
	Logging.logger.info('Loading plugins from: ' + pluginPath)
	Logging.logger.info("#"*50)
	pluginLoader.loadPlugins(pluginPath)
		
def getResource(symbolicName):
	return pluginLoader.getResource(symbolicName)

def reload():
	Logging.logger.info("#"*50)
	Logging.logger.info('Reloading all plugins...')
	Logging.logger.info("#"*50)
	pluginLoader.reloadAll()
	sbserver.reinitializeHandlers()

def shutdown():
	pluginLoader.unloadAll()
	sbserver.shutdown(0)
