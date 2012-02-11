from Query import Query
from Errors import NonCongruentGroup
from types import FunctionType
from Errors import InvalidGroupAction
import copy
import collections

class Group:
	"""Represents a query-able collection of objects (players, Users, etc)
	
	Groups provide a convenient way to hold, query, and perform actions on a collection of objects
	
	"""
	def __init__(self, Class, memberList = []):
		self.Class = Class
		self.List = memberList
		self.checkCongruity(memberList)
		
	def checkCongruity(self, memberList):
		"""Check whether the items in the members are all congruous."""
		for item in memberList:
			if not isinstance(item, self.memberClass()):
				raise NonCongruentGroup()
		
	def memberClass(self):
		return self.Class
		
	def copy(self):
		"""Return a copy of the current group"""
		#return Group(self.memberClass(), self.members())
		return copy.deepcopy(self)
		
	def query(self, *args):
		"""Create a new query with this as the data origin"""
		return Query(self).filter(*args)
		
	def members(self):
		"""Return the list of members"""
		return self.List
	
	def append(self, *others):
		"""Returns a group with the given group or members appended onto the current ones"""
		def appendTo(copy, item):
			if isinstance(item, copy.memberClass()):
				copy.memberList.append(item)
			elif isinstance(item, collections.Iterable):
				for it in item:
					appendTo(copy, it)
			elif isinstance(item, Group):
				members = item.members()
				for member in members:
					appendTo(copy, it)
			else:
				raise NonCongruentGroup()
				
		theCopy = self.copy()
		
		for item in others:
			appendTo(theCopy, item)
		
	def slice(self, start, end=None):
		"""Returns a group using the slicing rules of python lists"""
		if end == None:
			return self.members()[start:]
		else:
			return self.members[start:end]
	
	def first(self):
		"""Return the first item in the list of units"""
		return self.members()[0]
	
	def last(self):
		"""Return the last item in the list of units"""
		return self.members()[-1]
		
	def all(self):
		"""Return this group
		
		.all() may be called on an object which may be either a query or a group to get a group back.
		You can be sure after you call .all() that you have a normal static group.
		"""
		return self
	
	def action(self, methodName, args):
		"""Call a member function of each group member and return the results as a list
		
		functionName -- The name of the member method to be called on each group member.
		args -- A tuple of arguments to be passed to the member method of each group member.
		"""
		members = self.members()
		results = []
		for item in members:
				try:
					func = getattr(item, methodName)
					result = func(*args)
					results.append(result)
				except AttributeError:
					raise InvalidGroupAction(methodName)
		return results
	
	def __contains__(self, value):
		return value in self.members()
	
	def __iter__(self):
		return iter(self.members())
