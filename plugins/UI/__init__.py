from cxsbs.Plugin import Plugin

class UI(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass

import cxsbs
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
Config = cxsbs.getResource("Config")

import string

def notice(message):
	return notice_pre + message

def info(message):
	return info_pre + message

def warning(message):
	return warning_pre + message

def error(message):
	return error_pre + message

def insufficientPermissions(cn):
	ServerCore.playerMessage(cn, error('Insufficient permissions'))

def init():
	global notice_pre, info_pre, warning_pre, error_pre
	
	config = Config.PluginConfig('ui')
	notice_pre = config.getOption('Prefixes', 'notice', '${blue}Notice:')
	info_pre = config.getOption('Prefixes', 'info', '${yellow}Info:')
	warning_pre = config.getOption('Prefixes', 'warning', '${red}Warning:')
	error_pre = config.getOption('Prefixes', 'error', '${red}Error:')
	del config
	
	notice_pre = string.Template(notice_pre).substitute(Colors.colordict) + ' '
	info_pre = string.Template(info_pre).substitute(Colors.colordict) + ' '
	warning_pre = string.Template(warning_pre).substitute(Colors.colordict) + ' '
	error_pre = string.Template(error_pre).substitute(Colors.colordict) + ' '