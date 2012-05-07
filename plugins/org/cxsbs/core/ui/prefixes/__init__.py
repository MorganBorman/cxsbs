import pyTensible, org
import string

class prefixes(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		Interfaces = {}
		Resources = {'get_prefix_dict': get_prefix_dict}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		pass

@org.cxsbs.core.settings.manager.Setting
def notice():
	"""
	@category prefixes
	@display_name Notice
	@wbpolicy never
	@doc Notice prefix template.
	"""
	return string.Template("${blue}Notice:${white}${space}")

@org.cxsbs.core.settings.manager.Setting
def info():
	"""
	@category prefixes
	@display_name Info
	@wbpolicy never
	@doc Info prefix template.
	"""
	return string.Template("${yellow}Info:${white}${space}")

@org.cxsbs.core.settings.manager.Setting
def warning():
	"""
	@category prefixes
	@display_name Warning
	@wbpolicy never
	@doc Warning prefix template.
	"""
	return string.Template("${red}Warning:${white}${space}")

@org.cxsbs.core.settings.manager.Setting
def error():
	"""
	@category prefixes
	@display_name Error
	@wbpolicy never
	@doc Error prefix template.
	"""
	return string.Template("${red}Error:${white}${space}")

@org.cxsbs.core.settings.manager.Setting
def help():
	"""
	@category prefixes
	@display_name Help
	@wbpolicy never
	@doc Help prefix template.
	"""
	return string.Template("${grey}Help:${white}${space}")

@org.cxsbs.core.settings.manager.Setting
def denied():
	"""
	@category prefixes
	@display_name Denied
	@wbpolicy never
	@doc Denied prefix template.
	"""
	return string.Template("${red}Denied:${white}${space}")

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.ui.prefixes')

def get_prefix_dict():
	"""Get the current dictionary of prefixes
	
	Don't store this if you want to stay in sync with the settings when they get updated from the configs.
	"""
	dictionary = {}
	dictionary.update(org.cxsbs.core.ui.colors.colordict)
	dictionary['space'] = ' '
	
	return	{
					'notice': settings["notice"].substitute(dictionary),
					'info': settings["info"].substitute(dictionary),
					'warning': settings["warning"].substitute(dictionary),
					'error': settings["error"].substitute(dictionary),
					'help': settings["help"].substitute(dictionary),
					'denied': settings["denied"].substitute(dictionary),
					'space': ' ',
			}
	
	