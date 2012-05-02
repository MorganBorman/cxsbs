# Logging.py
# Allows simple configuration of the pyTensible logging
# Copyright (c) 2012 Morgan Borman
# E-mail: morgan.borman@gmail.com

# This software is licensed under the terms of the Zlib license.
# http://en.wikipedia.org/wiki/Zlib_License

"""
TODO: 	This needs to be redone so that custom loggers can be provided assuming 
		they implement the same interface as the Python logging ones do.
"""

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
	
def replace_logger(replacement_logger):
	global logger
	logger = replacement_logger

logger = logging.getLogger('pyTensible')
logger.setLevel(logging.DEBUG)