import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
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

def help(message):
	return help_pre + message

def denied(message):
	return denied_pre + message

def insufficientPermissions(cn):
	ServerCore.playerMessage(cn, error('Insufficient permissions.'))

def init():
	global notice_pre, info_pre, warning_pre, error_pre, help_pre, denied_pre
	
	config = Config.PluginConfig('ui')
	notice_pre = config.getTemplateOption('Prefixes', 'notice', '${blue}Notice:${white}').substitute(Colors.colordict) + " "
	info_pre = config.getTemplateOption('Prefixes', 'info', '${yellow}Info:${white}').substitute(Colors.colordict) + " "
	warning_pre = config.getTemplateOption('Prefixes', 'warning', '${red}Warning:${white}').substitute(Colors.colordict) + " "
	error_pre = config.getTemplateOption('Prefixes', 'error', '${red}Error:${white}').substitute(Colors.colordict) + " "
	help_pre = config.getTemplateOption('Prefixes', 'help', '${grey}Help:${white}').substitute(Colors.colordict) + " "
	denied_pre = config.getTemplateOption('Prefixes', 'denied', '${red}Denied:${white}').substitute(Colors.colordict) + " "
	
	global UIDict
	UIDict = 	{
					'notice': notice_pre,
					'info': info_pre,
					'warning:': warning_pre,
					'error': error_pre,
					'help': help_pre,
					'denied': denied_pre,
				}
	
	del config