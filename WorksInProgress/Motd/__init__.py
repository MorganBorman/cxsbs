import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import sbserver
from xsbs.settings import PluginConfig
from xsbs.colors import colordict
from xsbs.events import registerServerEventHandler
import string


def greet(cn):
	sbserver.playerMessage(cn, motdstring)

config = PluginConfig('motd')
motdstring = config.getOption('Config', 'template', '${orange}Welcome to a ${red}XSBS ${orange}server')
del config

motdstring = string.Template(motdstring).substitute(colordict)
registerServerEventHandler('player_connect_delayed', greet)

