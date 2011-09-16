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
	notice_pre = config.getTemplateOption('Prefixes', 'notice', '${blue}Notice: ').substitute(Colors.colordict)
	info_pre = config.getTemplateOption('Prefixes', 'info', '${yellow}Info: ').substitute(Colors.colordict)
	warning_pre = config.getTemplateOption('Prefixes', 'warning', '${red}Warning: ').substitute(Colors.colordict)
	error_pre = config.getTemplateOption('Prefixes', 'error', '${red}Error: ').substitute(Colors.colordict)
	del config