import ConfigParser
import Dependency
import Request

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
		
		try:
			self.Provides = manifest.get("Plugin", "Provides")
		except:
			self.Provides = None
			
		self.Version = manifest.get("Plugin", "Version")
		self.Author = manifest.get("Plugin", "Author")
		self.Enabled = manifest.get("Plugin", "Enabled") == "True"
		
		self.Dependencies = []
		dependencies = {}
		try:
			dependencies = manifest.items("Dependencies")
		except:
			pass
		for dependencyName, dependencyString in dependencies:
			dependency = Dependency.Dependency(dependencyName, dependencyString)
			self.Dependencies.append(dependency)
			
		self.Requests = []
		requests = {}
		try:
			requests = manifest.items("Requests")
		except:
			pass
		for requestName, requestString in requests:
			request = Request.Request(requestName, requestString)
			self.Requests.append(request)
		
class MalformedManifest(Exception):
	'''Invalid manifest form'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
