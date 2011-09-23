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
		
def init():
	config = Config.PluginConfig('mapcheck')
	global spectate_map_modified
	spectate_map_modified = (config.getOption('Config', 'spectate_map_modified', 'yes') == 'yes')
	del config
	
	@Events.eventHandler('player_modified_map')
	def onMapModified(cn):
		p = Players.player(cn)
		ServerCore.message(UI.info(Colors.green(p.name()) + " has a " + Colors.red("modified") + " map."))
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
			
		#TODO: create equivalent functionality for groups
		#if isAtLeastMaster(cn):
		#	return True
			
		if cn == tcn:
			p.message(UI.warning('You cannot play with a ' + Colors.red("modified") + ' map.'))
			
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
			p.message(UI.error('Usage: #mapmodifiedspec (enable/disable)'))