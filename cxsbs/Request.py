import Dependency

class Request(Dependency.Dependency):
	"""A class to hold a dependency and encapsulate dependency satisfation checks"""
	def __init__(self, requestName, requestString):
		Dependency.Dependency.__init__(self, requestName, requestString)
		self.requestName = requestName
		self.requestString = requestString
		
	def satisfied(self, requestName, version):
		"""Determines whether a dependency would be satisfied by the indicated version of plugin"""		
		for parameter in self.dependencyParameters:
			if not Dependency.satisfiesParameter(version, parameter):
				return False
		return True
