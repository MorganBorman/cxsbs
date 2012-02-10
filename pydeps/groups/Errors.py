class NonCongruentGroup(Exception):
	'''Group contains types other than that which it was initialized with.'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidGroupAction(Exception):
	'''Action called on a group or query whose result members do not have the target function as a member function.'''
	def __init__(self, value=''):
		Exception.__init__(self, value)
		
class InvalidProperty(Exception):
	"""..."""
	def __init__(self, value=''):
		Exception.__init__(self, value)