import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import pygeoip, os
	
import cxsbs
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
Messages = cxsbs.getResource("Messages")
Commands = cxsbs.getResource("Commands")
Players = cxsbs.getResource("Players")
Net = cxsbs.getResource("Net")
Events = cxsbs.getResource("Events")

pluginCategory = "GeoIp"

SettingsManager.addSetting(Setting.Setting	(
												category=pluginCategory, 
												subcategory="General", 
												symbolicName="geoIp_db_path", 
												displayName="GeoIp Database Path", 
												default=os.path.abspath("./resources/GeoIP.dat"),
												doc="Path to the geoIp database."
											))

settings = SettingsManager.getAccessor(category=pluginCategory, subcategory="General")

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="connection_message", 
						displayName="Connection Message", 
						default="${info}${green}${name}${white} connected from ${orange}${country}", 
						doc="Geoip connection message template."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)
	
db = pygeoip.GeoIP(settings["geoIp_db_path"])

def getCountry(ip):
	if Net.ipLongToString(ip) == "127.0.0.1":
		country = "Localhost"
	else:
		country = db.country_name_by_addr(Net.ipLongToString(ip))
		if country == '':
			country = 'Unknown'
	return country

@Events.eventHandler('player_connect_delayed')
def announce(cn):
	p = Players.player(cn)
	messager.sendMessage('connection_message', dictionary={'name':p.name(), 'country':getCountry(p.ipLong())})

@Events.policyHandler('connect_kick')
def allowClient(cn, pwd):
	p = Players.player(cn)
	return getCountry(p.ipLong()) != "Anonymous Proxy"