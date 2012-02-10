from cxsbs.Errors import MissingResourceComponent

import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		
		modelModule = cxsbs.getResource(settings['users_model'])
		try:
			modelClass = modelModule.__getattribute__("Model")
		except AttributeError:
			raise MissingResourceComponent(settings['users_model'], "Model", "class")
		
		if not issubclass(modelClass, UserModelBase.Model):
			raise InvalidResourceComponent(settings['users_model'], "Model", "class")
		
		import re
		
		usernameValidator = lambda x: re.match(settings['invalid_username_expression'], x)
		authenticationTokenValidator = lambda x: re.match(settings['invalid_token_seed_expression'], x)
		groupValidator = lambda x: re.match(settings['invalid_group_expression'], x)
		
		global model
		model = modelClass()
		
	def unload(self):
		pass
		
import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
UserModelBase = cxsbs.getResource("UserModelBase")

pluginCategory = 'Users'

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="users_model", 
												displayName="User model", 
												default='UserModelIntegrated',
												doc="User model to use."
											))

SettingsManager.addSetting(Setting.BoolSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="read_only", 
												displayName="Read only", 
												default=False,
												doc="Should the user model be read only. This may have no effect on some user models if they are readonly by nature."
											))

SettingsManager.addSetting(Setting.IntSetting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="max_nicks", 
												displayName="Max nicks", 
												default=2,
												doc="Number of nicknames to restrict users to. Do not set this less than 1."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="invalid_username_expression", 
												displayName="Invalid username expression", 
												default='^$',
												doc="Regular expression used to validate user names."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="invalid_token_seed_expression", 
												displayName="Invalid token seed expression", 
												default='^$',
												doc="Regular expression used to validate token seeds."
											))

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="invalid_group_expression", 
												displayName="Invalid group expression", 
												default='^$',
												doc="Regular expression used to validate group names."
											))

settings = SettingsManager.getAccessor(pluginCategory, "General")