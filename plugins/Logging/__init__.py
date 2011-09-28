import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		gameLogger.removeHandler(gameLoggerFileHandler)
		init()
		
	def unload(self):
		pass
		
import logging
import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
import cxsbs.Logging

def init():
	SettingsManager.addSetting(Setting.Setting('Logging', 'General', 'path', 'Logging path', 'gamelog.log'))
	SettingsManager.addSetting(Setting.Setting('Logging', 'General', 'level', 'Logging level', 'info'))
	
	settings = SettingsManager.getAccessor("Logging", 'General')
	
	path = ServerCore.instanceRoot() + "/" + settings['path']
	
	global LEVELS
	LEVELS = {'debug': logging.DEBUG,
				'info': logging.INFO,
				'warning': logging.WARNING,
				'error': logging.ERROR,
				'critical': logging.CRITICAL}
	
	cxsbs.Logging.logger.info("Game is now being logged to: " + path + " all messages of level: " + settings['level'] + " or higher will be logged.")
	
	global gameLogger
	gameLogger = logging.getLogger('gameLogger')
	gameLogger.setLevel(LEVELS[settings['level']])
	
	global gameLoggerFileHandler
	gameLoggerFileHandler = logging.FileHandler(path)
	gameLoggerFileHandler.setLevel(LEVELS[settings['level']])
	
	formatter = logging.Formatter('%(levelname)-10s %(asctime)s %(message)s')
	gameLoggerFileHandler.setFormatter(formatter)
	
	gameLogger.addHandler(gameLoggerFileHandler)
	
	global warn, info, error, debug, critical, exception, log
	#make these function available in this resource
	warn = gameLogger.warn
	error = gameLogger.error
	debug = gameLogger.debug
	info = gameLogger.info
	critical = gameLogger.critical
	exception = gameLogger.exception
	log = gameLogger.log
