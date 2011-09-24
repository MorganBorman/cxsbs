import PluginLoader
import sys, os, signal
import sbserver

pydepsPath = os.path.abspath("pydeps/")
sys.path.append(pydepsPath)

pluginLoader = PluginLoader.PluginLoader()

def loadPlugins(pluginPath):
	pluginLoader.loadPlugins(pluginPath)
		
def getResource(symbolicName):
	return pluginLoader.getResource(symbolicName)

def shutdown():
	pluginLoader.unloadAll()
	sbserver.shutdown(0)
