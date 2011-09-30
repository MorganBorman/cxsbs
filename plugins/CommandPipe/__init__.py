import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		global commandPipe
		commandPipe = CommandPipe()
		commandPipe.start()
		
	def unload(self):
		pass
	
import threading, sys, traceback

import cxsbs
SettingsManager = cxsbs.getResource("SettingsManager")
ServerCore = cxsbs.getResource("ServerCore")
Messages = cxsbs.getResource("Messages")
Players = cxsbs.getResource("Players")

pluginCategory = 'CommandPipe'

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName="on_shutdown", 
						displayName="On shutdown", 
						default="${warning}The server is shutting down, you will be disconnected momentarily.", 
						doc="Message to print when the server has been shutdown via the CommandPipe."
					)

Messages.addMessage	(
						subcategory=pluginCategory, 
						symbolicName='shutdown_imminent', 
						displayName="Shutdown imminent", 
						default="${warning}The server is going down in ${seconds} seconds.", 
						doc="Message to print when a server shutdown has been scheduled via the CommandPipe."
					)

messager = Messages.getAccessor(subcategory=pluginCategory)

def shutdown(waitTime=0):
	commandPipe.running = False
	waitTime = int(waitTime)
	if waitTime <= -1:
		cxsbs.shutdown()
	if waitTime == 0:
		messager.sendMessage('on_shutdown')
		for cn in ServerCore.clients():
			cxsbs.AsyncronousExecutor.dispatch(ServerCore.playerDisc, (cn,))
		cxsbs.AsyncronousExecutor.dispatch(shutdown, (waitTime-1,), time=1)
	else:
		messager.sendMessage('shutdown_imminent', dictionary={'seconds':waitTime})
		messager.printMessage('shutdown_imminent', dictionary={'seconds':waitTime})
		cxsbs.AsyncronousExecutor.dispatch(shutdown, (waitTime-1,), time=1)

def clients():
	for p in Players.all():
		print "(" + str(p.cn) + ")" + p.name() + "@" + p.ipString() + "\t\t" + str(p.groups())

quit = shutdown
reload = SettingsManager.restoreSettings
syncronize = SettingsManager.syncronizeSettings

class cxsbsShellClass:
	"""Wecome to the cxsbs shell.
	
	This is a simple way for you to monitor and control your server, and even learn how it works internally.
	"""
	def shutdown(self, time=0):
		"""This function shuts down the server gently. Unloading all plugins and disconnecting all clients before terminating."""
		pass
		
	def reload(self):
		"""This function loads all settings from the config files on disk."""
		pass
	
	def syncronize(self):
		"""This function syncronizes settings with those on the disk. Only those settings which are designated as writeBack settings will be stored"""
		pass
	
	def clients(self):
		"""This function lists the currently connected clients by Cn, Name, and IP"""
		pass

cxsbsShell = cxsbsShellClass()

localVars = {}

class CommandPipe(threading.Thread):
	def __init__(self):
		self.running = False
		threading.Thread.__init__(self)
		
	def run(self):
		self.running = True
		print "Welcome to CXSBS The Canonical eXtensible SauerBraten Server."
		print "This is the python shell interface, which may be left running and used to control your server."
		print "Use shutdown() to bring the server down."
		print "Run help(cxsbsShell) for more help."
		while self.running:
			input = raw_input(">>")
			try:
				exec(input)
			except:
				exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
				print traceback.format_exc()