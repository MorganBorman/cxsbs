"""
Lets assume all version numbers have three numeric parts and an optional
comment part as demonstrated below.
1.2.3
1.2.3.52x2

But keep in mind that the optional part will not get evaluated and is intended
for keeping track of revision numbers or something like that.
so:
1.2.3 equals 1.2.3.52x2

version strings look like this:
">0.0.0,<0.0.4,!0.0.2,0.0.6"
This means that the following version are acceptable;
0.0.1
0.0.3
0.0.6
"""

def getVersionParts(version):
	version = version.split('.')
	if len(version) > 3:
		version = version[:3]
	version = map(int, version)
	return version

def versionLess(version1, version2):
	version1 = getVersionParts(version1)
	version2 = getVersionParts(version2)
	for i in range(3):
		if version1[i] > version2[i]:
			return False
		elif version1[i] < version2[i]:
			return True
		else: #==
			pass #and look at the next part
	return False
	
def versionGreater(version1, version2):
	version1 = getVersionParts(version1)
	version2 = getVersionParts(version2)
	for i in range(3):
		if version1[i] > version2[i]:
			return True
		elif version1[i] < version2[i]:
			return False
		else: #==
			pass #and look at the next part
	return False
	
def versionEqual(version1, version2):
	version1 = getVersionParts(version1)
	version2 = getVersionParts(version2)
	for i in range(3):
		if version1[i] != version2[i]:
			return False
		else: #==
			pass #and look at the next part
	return True
	
def satisfiesParameter(version1, parameter):
	"""checks one parameter against the version given"""
	if parameter[0] in "><!":
		qualifier = parameter[0]
		version2 = parameter[1:]
		if qualifier == ">":
			return versionGreater(version1, version2)
		elif qualifier == "<":
			return versionLess(version1, version2)
		elif qualifier == "!":
			return not versionEqual(version1, version2)
	else:
		return versionEqual(version1, parameter)

class Dependency:
	"""A class to hold a dependency and encapsulate dependency satisfation checks"""
	def __init__(self, dependencyName, dependencyString):
		"""takes a dependency name and version string"""
		self.dependencyName = dependencyName
		self.dependencyString = dependencyString
		self.dependencyParameters = dependencyString.split(',')
		
	def satisfied(self, dependencyName, version):
		"""Determines whether a dependency would be satisfied by the indicated version of plugin"""
		if dependencyName != self.dependencyName:
			return False
		
		for parameter in self.dependencyParameters:
			if not satisfiesParameter(version, parameter):
				return False
		return True
