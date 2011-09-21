import ConfigParser
import Dependency

class Manifest:
	def __init__(self, manifestPath, manifestFile):
		self.manifestPath = manifestPath
		self.manifestFile = manifestFile
		self.fullManifestFilePath = manifestPath + "/" + manifestFile
		
		manifest = ConfigParser.ConfigParser()
		#Remove case insensitivity from the key part of the ConfigParser
		manifest.optionxform = str
		manifest.read(self.fullManifestFilePath)
		
		self.Name = manifest.get("Plugin", "Name")
		self.SymbolicName = manifest.get("Plugin", "SymbolicName")
		self.Version = manifest.get("Plugin", "Version")
		self.Author = manifest.get("Plugin", "Author")
		self.Enabled = manifest.get("Plugin", "Enabled") == "True"
		
		self.Dependencies = []
		
		for dependencyName, dependencyString in manifest.items("Dependencies"):
			dependency = Dependency.Dependency(dependencyName, dependencyString)
			self.Dependencies.append(dependency)
		
class MalformedManifest(Exception):
	'''Invalid manifest form'''
	def __init__(self, value=''):
		Exception.__init__(self, value)