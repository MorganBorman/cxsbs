import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
from xsbs.events import eventHandler
from xsbs.settings import PluginConfig
import string
import time
import sbserver

config = PluginConfig('demosave')
demo_location = string.Template(config.getOption('Config', 'save_location', 'prefix_${date}_${demonum}.dmo'))
del config

@eventHandler('demo_recorded')
def start_round(demonum):
	date = time.asctime( time.localtime(time.time()) )
	fname = demo_location.substitute(date=date, demonum=demonum)
	sbserver.saveDemoFile(fname)
