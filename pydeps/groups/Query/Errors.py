class MultipleResults(Exception):
	"""..."""
	def __init__(self, value=''):
		Exception.__init__(self, value)

class NoResults(Exception):
	"""..."""
	def __init__(self, value=''):
		Exception.__init__(self, value)