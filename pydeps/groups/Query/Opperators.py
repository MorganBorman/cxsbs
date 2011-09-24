class Not:
	"""Use this to reverse another Text boolean opperator"""
	def __init__(self, item):
		self.item = item
	
	def apply(self, text):
		return not self.item.apply(text)

class Is:
	"""A boolean opperation which returns whether or not some text and a given term are equal"""
	def __init__(self, term, caseSensitive=True):
		self.term = term
		self.caseSensitive = caseSensitive
	
	def apply(self, text):
		if self.caseSensitive:
			return (text == self.term)
		else:
			return (text.lower() == self.term.lower())

class Contains:
	"""A filter type which changes the order when applied based on the feild list and comparison function"""
	def __init__(self, term, caseSensitive=True):
		self.term = term
		self.caseSensitive = caseSensitive
	
	def apply(self, text):
		if self.caseSensitive:
			return (self.term in text)
		else:
			return (self.term.lower() in text.lower())