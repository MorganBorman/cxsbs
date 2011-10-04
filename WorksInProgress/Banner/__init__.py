import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
from xsbs.settings import PluginConfig
from xsbs.timers import addTimer
from xsbs.colors import colordict
from xsbs.ui import notice
from xsbs.server import message
from xsbs.commands import commandHandler
from xsbs.players import player
import string

class Banner:
	def __init__(self, msg, delay):
		self.msg = string.Template(msg).substitute(colordict)
		self.delay = delay
		addTimer(delay, self.sendMessage, ())
	def sendMessage(self):
		message(notice(self.msg))
		addTimer(self.delay, self.sendMessage, ())

banners = []
info_msg = ['']

@commandHandler('info')
def infoCmd(cn, args):
	player(cn).message(info_msg[0])

def setup():
	config = PluginConfig('banner')
	default_timeout = config.getOption('Config', 'default_timeout', 180000)
	for option in config.getAllOptions('Banners'):
		msg = option[1]
		delay = config.getOption('Timeouts', option[0], default_timeout, False)
		banners.append(Banner(msg, int(delay)))
	info_msg[0] = string.Template(config.getOption('Config', 'serverinfo', 'XSBS Version 2.0')).substitute(colordict)
	del config

setup()

