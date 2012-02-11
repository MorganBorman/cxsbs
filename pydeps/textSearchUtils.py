"""Simple substring match substring search and substring replace with optional case sensitivity"""

#I bet there is a standard way to do these, but I haven't found it yet.

import string

def hasWord(word, text, caseSensitive=False):
	"""Optionally case sensitive containment check for strings"""
	return findWord(word, text, caseSensitive=caseSensitive) != None
	
def findWord(word, text, caseSensitive=False):
	"""Optionally case sensitive search returning start and end index of the word in text"""
	if caseSensitive:
		start = text.find(word)
	else:
		start = text.lower().find(word.lower())
	if start != -1:
		return (start, start+len(word))
	else:
		return None
	
def replaceWord(word, replacement, text, caseSensitive=False):
	"""Optionally case sensitive search and replace. Cannot replace the null character as a whole word"""
	while hasWord(word, text, caseSensitive=caseSensitive):
		coords = findWord(word, text, caseSensitive=caseSensitive)
		text = text[:coords[0]] + "\x00" + text[coords[1]:]
	text = string.replace(text, "\x00", replacement)
	return text

if __name__ == '__main__':
	print replaceWord("[fd]", "", "[FD]Chasm", False)
	print replaceWord("[fd]", "", "[FD]Chasm", True)