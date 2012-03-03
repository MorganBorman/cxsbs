import logging

logging_path = "pyTensible.log"

def setup_logging(path=logging_path, console_level=logging.ERROR, file_level=logging.DEBUG):
	global logging_path
	logging_path = path

	# create file handler which logs even debug messages
	fh = logging.FileHandler(path)
	fh.setLevel(file_level)
	# create console handler with a higher log level
	ch = logging.StreamHandler()
	ch.setLevel(console_level)
	# create formatter and add it to the handlers
	formatter = logging.Formatter('%(levelname)-10s %(asctime)s %(message)s')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	# add the handlers to the logger
	logger.addHandler(fh)
	logger.addHandler(ch)

logger = logging.getLogger('pyTensible')
logger.setLevel(logging.DEBUG)