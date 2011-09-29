import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
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

def insufficientPermissions(cn):
	dictionary = UIDict()
	dictionary.update(Colors.colordict)
	ServerCore.playerMessage(cn, settings['insufficient_permissions'].substitute(dictionary))

def UIDict():
	"""Get the current UIDict
	
	Don't store this if you want to stay in sync with the settings if they get updated from config.
	"""
	dictionary = Colors.colordict
	dictionary['space'] = ' '
	
	return	{
					'notice': settings["notice"].substitute(dictionary),
					'info': settings["info"].substitute(dictionary),
					'warning:': settings["warning"].substitute(dictionary),
					'error': settings["error"].substitute(dictionary),
					'help': settings["help"].substitute(dictionary),
					'denied': settings["denied"].substitute(dictionary),
					'space': ' ',
			}