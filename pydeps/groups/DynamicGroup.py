from Group import Group

class DynamicGroup(Group):
	def __init__(self, Class, function, args=()):
		"""Creates a group whose contents is retrieved from a function every time it is queried
		
		
		"""
		Group.__init__(self, Class)
		self.function = function
		self.args = args
		
	def members(self):
		results = self.function(*self.args)
		self.checkCongruity(results)
		return results
	
	def all(self):
		"""Return an ordinary static group
		
		Used to turn a dynamic group into a static group.
		"""
		return Group(self.memberClass(), self.members())
	
	def __iter__(self):
		return iter(self.members())