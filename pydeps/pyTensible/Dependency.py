# Dependency.py
# A class and helper functions encapsulating the functionalities associated with version dependencies
# Copyright (c) 2012 Morgan Borman
# E-mail: morgan.borman@gmail.com

# This software is licensed under the terms of the Zlib license.
# http://en.wikipedia.org/wiki/Zlib_License

"""
Lets assume all version numbers have three numeric parts and an optional
comment part as demonstrated below.
1.2.3
1.2.3.52x2

Keep in mind that the optional part will not get evaluated and is intended
for keeping track of revision numbers or something like that.
so:
1.2.3 equals 1.2.3.52x2

version strings look like this:
"[1.0.0,2.0.0)"
Which means the range from 1.0.0 inclusive to 2.0.0 exclusive is acceptable.
[] = inclusive
() = exclusive
"""

def get_version_parts(version):
	version = version.split('.')
	if len(version) > 3:
		version = version[:3]
	version = map(int, version)
	return version

def version_less(version1, version2):
	version1 = get_version_parts(version1)
	version2 = get_version_parts(version2)
	for i in range(3):
		if version1[i] > version2[i]:
			return False
		elif version1[i] < version2[i]:
			return True
		else: #==
			pass #and look at the next part
	return False
	
def version_greater(version1, version2):
	version1 = get_version_parts(version1)
	version2 = get_version_parts(version2)
	for i in range(3):
		if version1[i] > version2[i]:
			return True
		elif version1[i] < version2[i]:
			return False
		else: #==
			pass #and look at the next part
	return False
	
def version_equal(version1, version2):
	version1 = get_version_parts(version1)
	version2 = get_version_parts(version2)
	for i in range(3):
		if version1[i] != version2[i]:
			return False
		else: #==
			pass #and look at the next part
	return True

def bstrip(string):
	return string.rstrip().lstrip()
	
def satisfies_range(version1, version_range):
	"""checks one parameter against the version given"""
	if not version_range[0] in ['[', '(']:
		raise MalformedVersionRange()
	
	if not version_range[-1] in [']', ')']:
		raise MalformedVersionRange()
	
	values = version_range[1:-1].split(',')
	lower = values[0]
	upper = values[1]
	
	if version_range[0] == '[':
		if version_less(version1, lower):
			return False
	else:
		if version_less(version1, lower) or version_equal(version1, lower):
			return False
		
	if version_range[-1] == ']':
		if version_greater(version1, upper):
			return False
	else:
		if version_greater(version1, upper) or version_equal(version1, upper):
			return False
		
	return True

class Dependency(object):
	"""A class to hold a dependency and encapsulate dependency satisfaction checks"""
	
	dependency_name = ""
	dependency_range = ""
	
	def __init__(self, dependency_name, dependency_string):
		"""takes a dependency name and version string"""
		self.dependency_name = dependency_name
		self.dependency_range = dependency_string
		
	def satisfied(self, dependency_name, version):
		"""Determines whether a dependency would be satisfied by the indicated version of plugin"""
		if dependency_name != self.dependency_name:
			return False
		
		if not satisfies_range(version, self.dependency_range):
			return False
		return True

class MalformedVersionRange(Exception):
	'''Invalid plugin form'''
	def __init__(self, value=''):
		Exception.__init__(self, value)