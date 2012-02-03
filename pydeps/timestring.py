signs = ['+', '-', '=']

#supported units and their second equivalents
units = {
		'y': 60*60*24*365,
		'd': 60*60*24,
		'h': 60*60,
		'm': 60,
		's': 1,
		}

class MalformedTimeString(Exception):
	'''Exception to raise when a malformed string is provided'''
	def __init__(self, value=''):
		Exception.__init__(self, value)

def isStrictToken(token):
	"""See whether a token has the form '<sign><number><unit>'"""
	if not token[0] in signs:
		return False
	
	if not token[-1] in units.keys():
		return False
	
	try:
		float(token[1:-1])
	except ValueError:
		return False
	
	return True

def simplify(tokenList):
	"""Apply one simplification opp to the tokenList"""
	i = 0
	while i < len(tokenList):
		
		#two adjacent integers
		try:
			int(tokenList[i])
			int(tokenList[i+1])
			tokenList[i] = tokenList[i] + tokenList[i+1]
			del tokenList[i+1]
			continue
		except ValueError:
			pass
		except IndexError:
			pass
		
		#an integer followed by a float
		try:
			int(tokenList[i])
			assert(not '.' in tokenList[i])
			float(tokenList[i+1])
			tokenList[i] = tokenList[i] + tokenList[i+1]
			del tokenList[i+1]
			continue
		except AssertionError:
			pass
		except ValueError:
			pass
		except IndexError:
			pass
		
		#an integer followed by a '.'
		try:
			int(tokenList[i])
			assert(not '.' in tokenList[i])
			assert('.' in tokenList[i])
			tokenList[i] = tokenList[i] + tokenList[i+1]
			del tokenList[i+1]
			continue
		except AssertionError:
			pass
		except ValueError:
			pass
		except IndexError:
			pass
		
		#a float followed by an integer
		try:
			float(tokenList[i])
			int(tokenList[i+1])
			assert(not '.' in tokenList[i])
			tokenList[i] = tokenList[i] + tokenList[i+1]
			del tokenList[i+1]
			continue
		except AssertionError:
			pass
		except ValueError:
			pass
		except IndexError:
			pass
		
		#two adjacent signs
		try:
			assert(tokenList[i] in signs)
			assert(tokenList[i+1] in signs)
			if tokenList[i] == '-' and tokenList[i+1] == '-':
				tokenList[i] = '+'
				del tokenList[i+1]
				continue
			elif '-' in [tokenList[i], tokenList[i+1]]:
				tokenList[i] = '-'
				del tokenList[i+1]
				continue
			elif '=' in [tokenList[i], tokenList[i+1]]:
				tokenList[i] = '='
				del tokenList[i+1]
				continue
			else:
				tokenList[i] = '+'
				del tokenList[i+1]
				continue
		except AssertionError:
			pass
		except IndexError:
			pass
		
		i += 1
		
	i = 0
	while i < len(tokenList):
		
		#a float followed by a unit designation
		#this should only happen after we've concatenated all of the integers and float components
		try:
			float(tokenList[i])
			assert(tokenList[i+1] in units.keys())
			tokenList[i] = tokenList[i] + tokenList[i+1]
			del tokenList[i+1]
		except AssertionError:
			pass
		except ValueError:
			pass
		except IndexError:
			pass
		
		i += 1

	i = 0
	while i < len(tokenList):
		
		#a float followed by a unit designation
		try:
			float(tokenList[i])
			assert(tokenList[i+1] in units.keys())
			tokenList[i] = tokenList[i] + tokenList[i+1]
			del tokenList[i+1]
		except AssertionError:
			pass
		except ValueError:
			pass
		except IndexError:
			pass
		
		#a trailing float or followed by a sign
		try:
			float(tokenList[i])
			assert(not tokenList[i+1] in signs)
			pass
		except ValueError:
			pass
		except (IndexError, AssertionError):
			tokenList.insert(i+1, 's')
			continue
		
		#a unit without a number
		try:
			assert(tokenList[i] in units.keys())
			tokenList.insert(i, '1')
			i -= 1
		except ValueError:
			pass
		except AssertionError:
			pass
		except IndexError:
			pass
		
		i += 1

	i = 0
	while i < len(tokenList):
		
		#a float and unit description at the start of a tokenList
		try:
			assert(i == 0)
			float(tokenList[i][:-1])
			assert(tokenList[i][-1] in units.keys())
			tokenList.insert(i, '=')
			i += 1
		except AssertionError:
			pass
		except ValueError:
			pass
		except IndexError:
			pass
		
		#a non-sign followed by a float and unit designation
		try:
			assert(not tokenList[i] in signs)
			float(tokenList[i+1][:-1])
			assert(tokenList[i+1][-1] in units.keys())
			tokenList.insert(i+1, '=')
		except AssertionError:
			pass
		except ValueError:
			pass
		except IndexError:
			pass
		
		i += 1
		
	i = 0
	while i < len(tokenList):
		
		#a sign followed by a a float and unit designation
		try:
			assert(tokenList[i] in signs)
			float(tokenList[i+1][:-1])
			assert(tokenList[i+1][-1] in units.keys())
			tokenList[i] = tokenList[i] + tokenList[i+1]
			del tokenList[i+1]
			continue
		except AssertionError:
			pass
		except ValueError:
			pass
		except IndexError:
			pass
		
		i += 1
		
	return tokenList

def parseStrictToken(token):
	"""given a string in the the format '<sign><number><unit>' return a number of seconds"""
	#get rid of the equals sign if it exists
	#print token
	if token[0] == '=':
		token = token[1:]
	#get the unit
	unit = token[-1]
	#chop the unit off the token
	token = token[:-1]
	
	#use python's eval to turn the possibly signed number string into an integer
	number = float(token)
	
	#get the unit multiplier and if necessary raise an invalid unit error
	try:
		unitMult = units[unit]
	except KeyError:
		raise MalformedTimeString('Invalid Unit')
	
	return int(unitMult*number)

def parseStrictTokenList(tokenList):
	"""given a list of strings each following the format '<sign><number><unit>' return a tuple with the overall sign and number of seconds"""
	secondCount = 0
	overallSign = '+'
	for token in tokenList:
		if token[0] == '=':
			overallSign = '='
		secondCount += parseStrictToken(token)
		
	if overallSign != '=':
		if secondCount < 0:
			overallSign = '-'
		else:
			overallSign = '+'
	else:
		if secondCount < 0:
			raise MalformedTimeString('Absolute negative time')
		
	return (overallSign, abs(secondCount))

def parseTimeString(timeString):
	"""Take a time string in the format specified below and return a tuple consisting of a character from ['+', '-', '='] and a number of seconds
	
	'+5m-3s' returns ('+', 277)
	'5m-3s' returns ('=', 277)
	'h+4' returns ('=', 3604)
	'-5' returns ('-', 5)
	'5m32s' returns ('=', 332)
	
	if the time string contains at least one sign-less number then the sign of the time value returned is '='
	
	valid units are ['h', 'm', 's']
	numbers without units are assumed to be seconds
	numbers without sign are assumed to have a '=' sign
	
	may not return a ('=' <negative>)
	
	"""
	try:
		tokenList = map(str, timeString)
		
		def notWhiteSpace(str):
			return not str.isspace()
		
		tokenList = filter(notWhiteSpace, tokenList)
		tokenList = simplify(tokenList)
			
		return parseStrictTokenList(tokenList)
	except ValueError:
		raise MalformedTimeString("Value error")
	
import unittest

class TestSimplify(unittest.TestCase):
	def test_absolute_hours(self):
		self.assertEqual(simplify(['2h']), ['=2h'])

class TestParseTimeString(unittest.TestCase):
	def test_absolute_hours(self):
		self.assertEqual(parseTimeString('2h'), ('=', 7200))
	
	def test_absolute_minutes(self):
		self.assertEqual(parseTimeString('2m'), ('=', 120))
	
	def test_absolute_seconds(self):
		self.assertEqual(parseTimeString('55s'), ('=', 55))
	
	def test_positive_hours(self):
		self.assertEqual(parseTimeString('+2h'), ('+', 7200))
	
	def test_positive_minutes(self):
		self.assertEqual(parseTimeString('+2m'), ('+', 120))
	
	def test_positive_seconds(self):
		self.assertEqual(parseTimeString('+33s'), ('+', 33))
	
	def test_negative_hours(self):
		self.assertEqual(parseTimeString('-4h'), ('-', 14400))
	
	def test_negative_minutes(self):
		self.assertEqual(parseTimeString('-12m'), ('-', 720))
	
	def test_negative_seconds(self):
		self.assertEqual(parseTimeString('-13s'), ('-', 13))
		
	def test_stacked_signs(self):
		self.assertEqual(parseTimeString('--13s'), ('+', 13))
		self.assertEqual(parseTimeString('---13s'), ('-', 13))
		self.assertEqual(parseTimeString('=+=13s'), ('=', 13))
		self.assertEqual(parseTimeString('-+13s'), ('-', 13))
		self.assertEqual(parseTimeString('-++13s'), ('-', 13))
		
	def test_white_space(self):
		self.assertEqual(parseTimeString('-	13s'), ('-', 13))
		self.assertEqual(parseTimeString('-   -13s'), ('+', 13))
		self.assertEqual(parseTimeString('  =13  s'), ('=', 13))
	
	def test_combinations(self):
		self.assertEqual(parseTimeString('+2m5h'), ('=', 18120))
		self.assertEqual(parseTimeString('+5h-3s'), ('+', 17997))
		self.assertEqual(parseTimeString('34m32s'), ('=', 34*60+32))
		self.assertEqual(parseTimeString('034m032s'), ('=', 34*60+32))
		self.assertEqual(parseTimeString('034m-032s'), ('=', 34*60-32))
	
	def test_no_units(self):
		self.assertEqual(parseTimeString('34'), ('=', 34))
		self.assertEqual(parseTimeString('+34'), ('+', 34))
		self.assertEqual(parseTimeString('-34'), ('-', 34))
	
	def test_no_sign(self):
		self.assertEqual(parseTimeString('3h'), ('=', 10800))
		self.assertEqual(parseTimeString('3m'), ('=', 180))
		self.assertEqual(parseTimeString('3s'), ('=', 3))
	
	def test_just_unit(self):
		self.assertEqual(parseTimeString('h'), ('=', 3600))
		self.assertEqual(parseTimeString('m'), ('=', 60))
		self.assertEqual(parseTimeString('s'), ('=', 1))
	
	def test_signed_unit(self):
		self.assertEqual(parseTimeString('+h'), ('+', 3600))
		self.assertEqual(parseTimeString('+m'), ('+', 60))
		self.assertEqual(parseTimeString('+s'), ('+', 1))
		self.assertEqual(parseTimeString('-h'), ('-', 3600))
		self.assertEqual(parseTimeString('-m'), ('-', 60))
		self.assertEqual(parseTimeString('-s'), ('-', 1))
		self.assertEqual(parseTimeString('=h'), ('=', 3600))
		self.assertEqual(parseTimeString('=m'), ('=', 60))
		self.assertEqual(parseTimeString('=s'), ('=', 1))