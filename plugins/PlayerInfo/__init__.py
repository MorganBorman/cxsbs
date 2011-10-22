import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
UserModel = cxsbs.getResource("UserModel")
UserModelBase = cxsbs.getResource("UserModelBase")
Players = cxsbs.getResource("Players")
Commands = cxsbs.getResource("Commands")
Messages = cxsbs.getResource("Messages")

pluginCategory = "PlayerInfo"

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="ip_info", 
						displayName="Ip info", 
						default="${info}Ip: ${green}${ip}${white}", 
						doc="Message to print when a players ip is requested."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="ping_info", 
						displayName="Ping info", 
						default="${info}Ping: ${green}${ping}${white}", 
						doc="Message to print when a players ping is requested."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="group_info", 
						displayName="Group info", 
						default="${info}Groups: ${green}${groups}${white}", 
						doc="Message to print when a players groups are requested."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
	
@Commands.commandHandler('ip')
def onIpCommand(cn, args):
	'''
	@description Get a player's Ip.
	@usage <cn>
	@allowGroups __master__ __admin__
	@denyGroups
	@doc Get a player's Ip.
	'''
	try:
		p = Players.player(cn)
		tcn = int(args)
		ip = Players.player(tcn).ipString()
		messager.sendPlayerMessage('ip_info', p, dictionary={'ip':ip})
	except:
		raise
	
@Commands.commandHandler('ping')
def onPingCommand(cn, args):
	'''
	@description Get a player's ping.
	@usage <cn>
	@allowGroups __all__
	@denyGroups
	@doc Get a player's ping.
	'''
	try:
		p = Players.player(cn)
		tcn = int(args)
		ping = Players.player(tcn).ping()
		messager.sendPlayerMessage('ping_info', p, dictionary={'ping':ping})
	except:
		raise
	
@Commands.commandHandler('groups')
def onGroupsCommand(cn, args):
	'''
	@description Get a player's groups.
	@usage <cn>
	@allowGroups __master__ __admin__
	@denyGroups
	@doc Get a player's groups.
	'''
	p = Players.player(cn)
	
	args = args.split()
	if len(args) != 1:
		raise Commands.UsageError()

	try:
		tcn = int(args[0])
		groups = Players.player(tcn).groups()
	except ValueError:
		email = args[0]
		
		try:
			userId = UserModel.model.getUserId(email)
		except UserModelBase.InvalidEmail:
			raise Commands.StateError("That email does not correspond to an account.")
		
		groups = UserModel.model.groups(userId)
	
	try:
		if len(groups) > 0:
			groups = ', '.join(groups)
		else:
			groups = ""
			
		messager.sendPlayerMessage('group_info', p, dictionary={'groups':groups})
	except:
		raise