import pyTensible, org

class colors(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		Interfaces = {}
		Resources = 	{
							'colorstring': colorstring,
							'colordict': colordict,
							'green': green,
							'blue': blue,
							'yellow': yellow,
							'red': red,
							'grey': grey,
							'magenta': magenta,
							'orange': orange,
							'white': white,
						}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

def textcolor(color, text):
	if text:
		return '\fs\f' + str(color) + text + '\fr'
	else:
		return '\f' + str(color)
	
def green(text=None):
	return textcolor(0, text)
def blue(text=None):
	return textcolor(1, text)
def yellow(text=None):
	return textcolor(2, text)
def red(text=None):
	return textcolor(3, text)
def grey(text=None):
	return textcolor(4, text)
def magenta(text=None):
	return textcolor(5, text)
def orange(text=None):
	return textcolor(6, text)
def white(text=None):
	return textcolor(7, text)

colordict = {
				'green': green(),
				'blue' : blue(),
				'yellow' : yellow(),
				'red' : red(),
				'grey' : grey(),
				'magenta': magenta(),
				'orange': orange(),
				'white': white(),
			}

def colorstring(str, text):
	try:
		textcolor(colordict[str],text)
	except IndexError:
		raise ValueError("That is not a valid color.")