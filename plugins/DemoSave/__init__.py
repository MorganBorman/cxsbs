import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global demoDetails
		demoDetails = deque()
		
	def unload(self):
		pass
	
import cxsbs
Events = cxsbs.getResource("Events")
Setting = cxsbs.getResource("Setting")
SettingsManager = cxsbs.getResource("SettingsManager")
ServerCore = cxsbs.getResource("ServerCore")
Game = cxsbs.getResource("Game")

import time, os, datetime
from collections import deque

pluginCategory = 'Demo'

SettingsManager.addSetting(Setting.Setting	(
													category=pluginCategory, 
													subcategory="Save", 
													symbolicName="path", 
													displayName="Path", 
													default="demos", 
													doc="Location to save demos relative to the instance root."
												))

SettingsManager.addSetting(Setting.TemplateSetting	(
												category=pluginCategory, 
												subcategory="Save", 
												symbolicName="filename", 
												displayName="Filename", 
												default='${year}_${month}_${day}_${hour}_${minute}_${second}_server_${demonum}_${mapName}_${modeName}.dmo',
												doc="Filename to store demos under."
											))

settings = SettingsManager.getAccessor(pluginCategory, "Save")

class DemoDetails:
	def __init__(self, mapName, modeName):
		self.mapName = mapName
		self.modeName = modeName

@Events.eventHandler('demo_recorded')
def onDemoRecorded(demonum):
	path = ServerCore.instanceRoot() + "/" + settings['path']
	try:
		os.makedirs(os.path.abspath(path))
	except OSError:
		pass
	
	demoDetail = demoDetails.popleft() 
	
	date = datetime.datetime.today()
	fname = path + "/" + settings['filename'].substitute(	year="%04d" % date.year, 
															month="%02d" % date.month, 
															day="%02d" % date.day, 
															hour="%02d" % date.hour, 
															minute="%02d" % date.minute, 
															second="%02d" % date.second, 
															demonum=demonum, 
															mapName=demoDetail.mapName, 
															modeName=demoDetail.modeName
														)
	
	ServerCore.saveDemoFile(fname)
	
@Events.eventHandler('map_changed')
def onMapChanged(mapName, modeNum):
	modeName = Game.modeName(modeNum)
	demoDetails.append(DemoDetails(mapName, modeName))