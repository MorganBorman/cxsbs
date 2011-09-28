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
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")

pluginCategory = 'UserInterface'
	
SettingsManager.addSetting(Setting.TemplateSetting	(
												category=pluginCategory, 
												subcategory="Prefixes", 
												symbolicName="notice", 
												displayName="Notice", 
												default="${blue}Notice:${white}${space}",
												doc="Notice prefix template"
											))

SettingsManager.addSetting(Setting.TemplateSetting	(
												category=pluginCategory, 
												subcategory="Prefixes", 
												symbolicName="info", 
												displayName="Info", 
												default="${yellow}Info:${white}${space}",
												doc="Info prefix template"
											))

SettingsManager.addSetting(Setting.TemplateSetting	(
												category=pluginCategory, 
												subcategory="Prefixes", 
												symbolicName="warning", 
												displayName="Warning", 
												default="${red}Warning:${white}${space}",
												doc="Warning prefix template"
											))

SettingsManager.addSetting(Setting.TemplateSetting	(
												category=pluginCategory, 
												subcategory="Prefixes", 
												symbolicName="error", 
												displayName="Error", 
												default="${red}Error:${white}${space}",
												doc="Error prefix template"
											))

SettingsManager.addSetting(Setting.TemplateSetting	(
												category=pluginCategory, 
												subcategory="Prefixes", 
												symbolicName="help", 
												displayName="Help", 
												default="${grey}Help:${white}${space}",
												doc="Help prefix template"
											))

SettingsManager.addSetting(Setting.TemplateSetting	(
												category=pluginCategory, 
												subcategory="Prefixes", 
												symbolicName="denied", 
												displayName="Denied", 
												default="${red}Denied:${white}${space}",
												doc="Denied prefix template"
											))

SettingsManager.addSetting(Setting.TemplateSetting	(
												category=pluginCategory, 
												subcategory="Prefixes", 
												symbolicName="insufficient_permissions", 
												displayName="Insufficient permissions", 
												default="%(error)s${red}Insufficient permissions.${white}${space}",
												doc="Insufficient permissions message."
											))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="Prefixes")

import string

def notice(message):
	return settings["notice_pre"] + message

def info(message):
	return settings["info_pre"] + message

def warning(message):
	return settings["warning_pre"] + message

def error(message):
	return settings["error_pre"] + message

def help(message):
	return settings["help_pre"] + message

def denied(message):
	return settings["denied_pre"] + message

def insufficientPermissions(cn):
	dictionary = UIDict()
	dictionary.update(Colors.colordict)
	ServerCore.playerMessage(cn, settings['insufficient_permissions'].substitute(dictionary))

def UIDict():
	"""Get the current UIDict
	
	Don't store this if you want to stay in sync with the settings if they get updated from config.
	"""
	return	{
					'notice': settings["notice_pre"],
					'info': settings["info_pre"],
					'warning:': settings["warning_pre"],
					'error': settings["error_pre"],
					'help': settings["help_pre"],
					'denied': settings["denied_pre"],
					'space': ' ',
			}