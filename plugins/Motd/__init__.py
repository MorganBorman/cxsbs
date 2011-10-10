import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
Events = cxsbs.getResource("Events")
Players = cxsbs.getResource("Players")
Messages = cxsbs.getResource("Messages")

pluginCategory = 'Motd'

Messages.addMessage	(
						category=pluginCategory,
						subcategory="General", 
						symbolicName="message_of_the_day", 
						displayName="Message of the day", 
						default="Welcome to a ${red}C${blue}X${green}S${yellow}B${magenta}S${white} server.", 
						doc="Message to say to players on connect."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

@Events.eventHandler('player_connect_delayed')
def greet(cn):
	p = Players.player(cn)
	messager.sendPlayerMessage('message_of_the_day', p)

