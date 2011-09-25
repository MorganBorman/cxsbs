from cxsbs.Plugin import Plugin

class MapCheck(Plugin):
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
ServerCore = cxsbs.getResource("ServerCore")
Colors = cxsbs.getResource("Colors")
UI = cxsbs.getResource("UI")
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Net = cxsbs.getResource("Net")
Server = cxsbs.getResource("Server")
Commands = cxsbs.getResource("Commands")
MessageFramework = cxsbs.getResource("MessageFramework")
		
def init():
	config = Config.PluginConfig('mapcheck')
	global spectate_map_modified
	spectate_map_modified = config.getBoolOption('Config', 'spectate_map_modified', True)
	del config
	
	config = Config.PluginConfig('Permissions')
	global allowgroups_modified_unspec
	allowgroups_modified_unspec = config.getBoolOption('MapCheck', "allowgroups_modified_unspec", "__admin__ __master__")
	del config
	
	global messageModule
	messageModule = MessageFramework.MessagingModule()
	messageModule.addMessage('map_modified', "${info}${green}${name}${white} has a ${red}modified${white} map.", 'MapCheck')
	messageModule.addMessage('modified_unspec', "${warning}You cannot play with a ${red}modified${white} map.", 'MapCheck')
	messageModule.finalize()
	
	@Events.eventHandler('player_modified_map')
	def onMapModified(cn):
		p = Players.player(cn)
		messageModule.messagePlayer('map_modified', p, dictionary={'name':p.name()})
		p.gamevars['modified_map'] = True
		if not onUnspectate(cn, cn):
			p.spectate()
	
	@Events.policyHandler('player_unspectate')
	def onUnspectate(cn, tcn):
		global spectate_map_modified
		if not spectate_map_modified:
			return True
			
		p = Players.player(cn)
		if not p.gamevars['modified_map']:
			return True
			
		for group in p.groups():
			if group in allowgroups_modified_unspec:
				return True
			
		if cn == tcn:
			messageModule.messagePlayer('modified_unspec', p)
			
		return False
	
	@Events.eventHandler('player_active')
	def checkModified(cn):
		try:
			p = Players.player(cn)
			if not onUnspectate(cn, cn):
				p.spectate()
		except KeyError:
			pass
		except ValueError:
			pass
	
	"""
	@Commands.commandHandler('mapmodifiedspec')
	def mapModifiedSpecCmd(cn, args):
		'''@description Enable or disable spectate clients with modified map
		   @usage enable/disable'''
		p = Players.player(cn)
		global spectate_map_modified
		if args == 'disable':
			spectate_map_modified = False
			p.message(UI.info('Spectate modified maps disabled'))
		elif args == 'enable':
			spectate_map_modified = True
			p.message(UI.info('Spectate modified maps enabled'))
		else:
	
			p.message(UI.error('Usage: #mapmodifiedspec (enable/disable)'))"""