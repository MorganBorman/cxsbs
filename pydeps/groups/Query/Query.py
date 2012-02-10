from Filters import Intersection, Union
import copy

class Query:
	"""Holds the sequence of opperations producing a group"""
	def __init__(self, origin, opperations=[]):
		self.origin = origin
		self.opperations = opperations
		
	def memberClass(self):
		return self.origin.memberClass()
		
	def copy(self):
		"""Return a copy of the current query"""
		#item = Query(self.origin, opperations = self.opperations)
		#return item
		return copy.deepcopy(self)
		
	def filter(self, *opperations):
		"""
		Return a copy of the current query with the specified filter applied
		If more than one filter is supplied then the intersection of the queries is taken
		
		"""
	
		theCopy = self.copy()
	
		if len(opperations) == 1:
			theCopy.opperations.append(opperations[0])
		elif len(opperations) > 1:
			theCopy.opperations.append(Intersection(*opperations))
			
		return theCopy
	
	def append(self, *args):
		"""Join the contents of the args with this one"""
		return self.filter(Union(*args))
		
	def apply(self):
		"""Run the query"""
		temp = self.origin.copy()
		for op in self.opperations:
			temp = op.apply(temp)
		return temp
				
	
	def one(self):
		"""Return a single result or raise an error if the number of results is none or > 1"""
		return self.apply()[0]
	
	def all(self):
		"""Return a group consisting of the results of the query"""
		return self.apply()