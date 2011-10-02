from types import FunctionType
import groups.Group
from groups.Errors import InvalidProperty

class Filter:
	pass

class Select(Filter):
	"""
	A filter type which keeps only those items from the origin satisfying a given criteria
	
	Filter(name=Contains("c"))
	
	Filters can be applied on member datum, and functions taking no args (soon we'll get args working)
	
	"""
	def __init__(self, **kwargs):
		self.criteria = kwargs
		
	def isValid(self, origin):
		"""Returns a boolean indicating whether or not the filter is valid with respect to the given origin"""
	
	def apply(self, origin):
		destination = []
		
		for item in origin.all().members():
			keep = True
			for key in self.criteria:
				try:
					func = getattr(item, key)
					if not self.criteria[key].apply(func()):
						keep = False
				except AttributeError:
					if key in item.__dict__.keys():
						if not self.criteria[key].apply(item.__dict__[key]):
							keep = False
					else:
						raise InvalidProperty(key)
			if keep:
				destination.append(item)
				
		return groups.Group(origin.memberClass(), destination)
		
class Cull(Filter):
	"""
	A filter type which keeps those items from the origin not satisfying a given criteria
	
	Cull(name=Contains("c"))
	
	"""
	def __init__(self, **kwargs):
		self.criteria = kwargs
		
	def isValid(self, origin):
		"""Returns a boolean indicating whether or not the filter is valid with respect to the given origin"""
		pass
	
	def apply(self, origin):
		destination = []
		
		for item in origin.all().members():
			keep = True
			for key in self.criteria:
				try:
					func = getattr(item, key)
					if not self.criteria[key].apply(func()):
						keep = False
				except AttributeError:
					if key in item.__dict__.keys():
						if not self.criteria[key].apply(item.__dict__[key]):
							keep = False
					else:
						raise InvalidProperty(key)
			if keep:
				destination.append(item)
				
		return groups.Group(origin.memberClass(), destination)
	

class Order(Filter):
	"""
	A filter type which changes the order of the origin when applied based on a dictionary 
	
	Order(frags=lessThan)
	
	"""
	def __init__(self, **kwargs):
		self.criteria = kwargs
		
	def isValid(self, origin):
		"""Returns a boolean indicating whether or not the filter is valid with respect to the given origin"""
		pass
	
	def apply(self, origin):
		pass
		
class Union(Filter):
	"""A filter type which returns the union of one or more other queries or groups and the origin."""
	def __init__(self, *args):
		self.others = args
		
	def isValid(self, origin):
		"""Returns a boolean indicating whether or not the filter is valid with respect to the given origin"""
		pass
	
	def apply(self, origin):
		origin.append(*self.others)
		
class Intersection(Filter):
	"""A filter type which returns the common elements  of one or more other queries or groups and the origin."""
	def __init__(self, *args):
		self.others = args
		
	def isValid(self, origin):
		"""Returns a boolean indicating whether or not the filter is valid with respect to the given origin"""
		pass
	
	def apply(self, origin):
		destination = []
		
		#buld a list of all the intersecting bits with filters applied to origin and queries and groups left as-is
		others = []
		for other in self.others:
			if issubclass(other.__class__, Filter):
				others.append(other.apply(origin))
			else:
				others.append(other)
		
		for item in origin.all():
			keep = True
			for other in others:
				if not item in other.all():
					keep = False
			if keep:
				destination.append(item)
					
		return groups.Group(origin.memberClass(), destination)
		
class Difference(Filter):
	"""A filter type which returns those elements which are in the origin but not in the supplied queries or groups."""
	def __init__(self, item):
		self.other = item
		
	def isValid(self, origin):
		"""Returns a boolean indicating whether or not the filter is valid with respect to the given origin"""
		pass
	
	def apply(self, origin):
		destination = []
		
		#buld a list of all the intersecting bits with filters applied to origin and queries and groups left as-is
		others = []
		for other in self.others:
			if issubclass(other.__class__, Filter):
				others.append(other.apply(origin))
			else:
				others.append(other)
		
		for item in origin.all():
			keep = True
			for other in others:
				if item in other.all():
					keep = False
			if keep:
				destination.append(item)
					
		return groups.Group(origin.memberClass(), destination)
