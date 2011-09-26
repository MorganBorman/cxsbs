import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def reload(self):
		pass
		
	def unload(self):
		pass
		
import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Server = cxsbs.getResource("Server")
Commands = cxsbs.getResource("Commands")

teams = [
	'evil',
	'good',
	'other',
]

def teamName(teamnum):
	'''String representing the team name'''
	return teams[teamnum]
	
def teamNumber(teamname):
	'''Number representing one of the two major teams'''
	i = 0
	for team in teams:
		if teamname == team:
			return i
		i += 1
	raise ValueError('Invalid team')

modes = [
	'ffa',
	'coop',
	'team',
	'insta',
	'instateam',
	'effic',
	'efficteam',
	'tac',
	'tacteam',
	'capture',
	'regencapture',
	'ctf',
	'instactf',
	'protect',
	'instaprotect',
	'hold',
	'instahold',
	'efficctf',
	'efficprotect',
	'effichold',
]

def modeName(modenum):
	'''String representing game mode number'''
	return modes[modenum]

def modeNumber(modename):
	'''Number representing game mode string'''
	i = 0
	for mode in modes:
		if modename == mode:
			return i
		i += 1
	raise ValueError('Invalid mode')

def currentMap():
	'''Name of current map'''
	return ServerCore.mapName()

def currentMode():
	'''Integer value of current game mode'''
	return ServerCore.gameMode()

def setMap(map_name, mode_number):
	'''Set current map and mode'''
	if Server.isFrozen():
		raise Commands.StateError('Server is currently frozen')
	ServerCore.setMap(map_name, mode_number)