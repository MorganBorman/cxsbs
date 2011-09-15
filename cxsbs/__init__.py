import PluginLoader

pluginLoader = PluginLoader.PluginLoader()

def loadPlugins(pluginPath):
	pluginLoader.loadPlugins(pluginPath)
		
def getResource(symbolicName):
	return pluginLoader.getResource(symbolicName)