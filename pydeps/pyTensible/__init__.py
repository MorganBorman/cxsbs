# __init__.py
# Package initializer script for pyTensible
# Copyright (c) 2012 Morgan Borman
# E-mail: morgan.borman@gmail.com

# This software is licensed under the terms of the Zlib license.
# http://en.wikipedia.org/wiki/Zlib_License

__version__ = "1.1.3"

from bootstrap_pyTensible import bootstrap_pyTensible as PluginLoader
from Logging import setup_logging, logger
