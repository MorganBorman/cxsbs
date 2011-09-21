from cxsbs.Plugin import Plugin

class Logging(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass
		
import logging
import cxsbs
Config = cxsbs.getResource("Config")

def init():
	config = Config.PluginConfig('logging')
	path = config.getOption('Config', 'path', 'cxsbs.log')
	level = config.getOption('Config', 'level', 'error')
	del config
	
	LEVELS = {'debug': logging.DEBUG,
		'info': logging.INFO,
		'warning': logging.WARNING,
		'error': logging.ERROR,
		'critical': logging.CRITICAL}
	
	print "\tLogging to:", path
	
	logging.basicConfig(
		filename = path,
		format = '%(levelname)-10s %(asctime)s %(pathname)s: %(message)s',
		level = LEVELS[level])
	
#make these function available in this resource
warn = logging.warn
error = logging.error
debug = logging.debug
