import pyTensible, org

class logger(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		import logging, cube2server

		logging_path = cube2server.serverInstanceRoot() + "/cxsbs.log"
		
		file_level=logging.DEBUG
		console_level=logging.ERROR
		
		log = logging.getLogger('cxsbs')
		log.setLevel(logging.DEBUG)
		
		# create file handler which logs even debug messages
		fh = logging.FileHandler(logging_path)
		fh.setLevel(file_level)
		# create console handler with a higher log level
		ch = logging.StreamHandler()
		ch.setLevel(console_level)
		# create formatter and add it to the handlers
		formatter = logging.Formatter('%(levelname)-10s %(asctime)s %(message)s')
		fh.setFormatter(formatter)
		ch.setFormatter(formatter)
		# add the handlers to the logger
		log.addHandler(fh)
		log.addHandler(ch)
		
		Interfaces = {}
		Resources = {'log': log}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass