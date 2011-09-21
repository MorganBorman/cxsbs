import PluginLoader
import sys, os

pydepsPath = os.path.abspath("pydeps/")
sys.path.append(pydepsPath)

pluginLoader = PluginLoader.PluginLoader()

def loadPlugins(pluginPath):
	pluginLoader.loadPlugins(pluginPath)
		
def getResource(symbolicName):
	return pluginLoader.getResource(symbolicName)
