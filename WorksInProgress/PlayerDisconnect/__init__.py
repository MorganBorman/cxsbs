import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		pass
		
	def unload(self):
		pass
	
import cxsbs
ServerCore = cxsbs.getResource("ServerCore")

DISC_NONE = 0
DISC_EOP = 1
DISC_CN = 2
DISC_KICK = 3
DISC_TAGT = 4
DISC_IPBAN = 5
DISC_PRIVATE = 6
DISC_MAXCLIENTS = 7
DISC_TIMEOUT = 8
DISC_OVERFLOW = 9
DISC_NUM = 10

def disconnect(cn, reason):
	"Disconnect a client for a specified reason."
	
	ServerCore.playerDisconnect(cn, reason)