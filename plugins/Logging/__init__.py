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
ServerCore = cxsbs.getResource("ServerCore")
import cxsbs.Logging

def init():
	config = Config.PluginConfig('logging')
	path = ServerCore.instanceRoot() + "/" + config.getOption('Config', 'path', 'gamelog.log')
	level = config.getOption('Config', 'level', 'info')
	del config
	
	global LEVELS
	LEVELS = {'debug': logging.DEBUG,
				'info': logging.INFO,
				'warning': logging.WARNING,
				'error': logging.ERROR,
				'critical': logging.CRITICAL}
	
	cxsbs.Logging.logger.info("Game is now being logged to: " + path + " all messages of level: " + level + " or higher will be logged.")
	
	global gameLogger
	gameLogger = logging.getLogger('gameLogger')
	gameLogger.setLevel(LEVELS[level])
	fh = logging.FileHandler(path)
	fh.setLevel(LEVELS[level])
	
	formatter = logging.Formatter('%(levelname)-10s %(asctime)s %(message)s')
	fh.setFormatter(formatter)
	
	gameLogger.addHandler(fh)
	
	global warn, info, error, debug, critical, exception, log
	#make these function available in this resource
	warn = gameLogger.warn
	error = gameLogger.error
	debug = gameLogger.debug
	info = gameLogger.info
	critical = gameLogger.critical
	exception = gameLogger.exception
	log = gameLogger.log
