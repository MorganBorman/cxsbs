from cxsbs.Plugin import Plugin
from cxsbs.Errors import MissingResourceComponent

class UserModel(Plugin):
	def __init__(self):
		Plugin.__init__(self)
		
	def load(self):
		init()
		
	def reload(self):
		init()
		
	def unload(self):
		pass
		
import cxsbs
Config = cxsbs.getResource("Config")
BaseUserModel = cxsbs.getResource("BaseUserModel")

import re
		
def init():
	config = Config.PluginConfig('users')
	modelName = config.getOption('User Model', 'users_model', 'IntegratedUserModel')
	readOnly = config.getBoolOption('User Model', 'read_only', 'False')
	maxNicks = config.getIntOption('User Model', 'max_nicks', '2')
	nickRE = config.getOption('User Model', 'invalid_username_expression', '^$')
	authRE = config.getOption('User Model', 'invalid_token_seed_expression', '^$')
	groupRE = config.getOption('User Model', 'invalid_group_expression', '^$')
	del config
	
	modelModule = cxsbs.getResource(modelName)
	try:
		modelClass = modelModule.__getattribute__(modelName)
	except AttributeError:
		raise MissingResourceComponent(modelName, modelName, "class")
	
	if not issubclass(modelClass, BaseUserModel.Model):
		raise InvalidResourceComponent(modelName, modelName, "class")
	
	usernameValidator = lambda x: re.match(nickRE, x)
	authenticationTokenValidator = lambda x: re.match(authRE, x)
	groupValidator = lambda x: re.match(groupRE, x)
	
	global model
	model = modelClass(readOnly, usernameValidator, authenticationTokenValidator, groupValidator, maxNicks)