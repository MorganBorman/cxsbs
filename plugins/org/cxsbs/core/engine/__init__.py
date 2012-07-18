import pyTensible, org
import enet
import sys
import traceback
import threading
from enum import enum

import DataBuffer

class engine(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		
		Interfaces = {}
		Resources = {"Engine": Engine}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		Engine._instance.stop()
		
message_types = enum('N_CONNECT', 'N_SERVINFO', 'N_WELCOME', 'N_INITCLIENT', 'N_POS', 'N_TEXT', 'N_SOUND', 'N_CDIS',
	'N_SHOOT', 'N_EXPLODE', 'N_SUICIDE',
	'N_DIED', 'N_DAMAGE', 'N_HITPUSH', 'N_SHOTFX', 'N_EXPLODEFX',
	'N_TRYSPAWN', 'N_SPAWNSTATE', 'N_SPAWN', 'N_FORCEDEATH',
	'N_GUNSELECT', 'N_TAUNT',
	'N_MAPCHANGE', 'N_MAPVOTE', 'N_ITEMSPAWN', 'N_ITEMPICKUP', 'N_ITEMACC', 'N_TELEPORT', 'N_JUMPPAD',
	'N_PING', 'N_PONG', 'N_CLIENTPING',
	'N_TIMEUP', 'N_MAPRELOAD', 'N_FORCEINTERMISSION',
	'N_SERVMSG', 'N_ITEMLIST', 'N_RESUME',
	'N_EDITMODE', 'N_EDITENT', 'N_EDITF', 'N_EDITT', 'N_EDITM', 'N_FLIP', 'N_COPY', 'N_PASTE', 'N_ROTATE', 'N_REPLACE', 'N_DELCUBE', 'N_REMIP', 'N_NEWMAP', 'N_GETMAP', 'N_SENDMAP', 'N_CLIPBOARD', 'N_EDITVAR',
	'N_MASTERMODE', 'N_KICK', 'N_CLEARBANS', 'N_CURRENTMASTER', 'N_SPECTATOR', 'N_SETMASTER', 'N_SETTEAM',
	'N_BASES', 'N_BASEINFO', 'N_BASESCORE', 'N_REPAMMO', 'N_BASEREGEN', 'N_ANNOUNCE',
	'N_LISTDEMOS', 'N_SENDDEMOLIST', 'N_GETDEMO', 'N_SENDDEMO',
	'N_DEMOPLAYBACK', 'N_RECORDDEMO', 'N_STOPDEMO', 'N_CLEARDEMOS',
	'N_TAKEFLAG', 'N_RETURNFLAG', 'N_RESETFLAG', 'N_INVISFLAG', 'N_TRYDROPFLAG', 'N_DROPFLAG', 'N_SCOREFLAG', 'N_INITFLAGS',
	'N_SAYTEAM',
	'N_CLIENT',
	'N_AUTHTRY', 'N_AUTHCHAL', 'N_AUTHANS', 'N_REQAUTH',
	'N_PAUSEGAME',
	'N_ADDBOT', 'N_DELBOT', 'N_INITAI', 'N_FROMAI', 'N_BOTLIMIT', 'N_BOTBALANCE',
	'N_MAPCRC', 'N_CHECKMAPS',
	'N_SWITCHNAME', 'N_SWITCHMODEL', 'N_SWITCHTEAM',
	'NUMSV')

class EngineClient(object):
	cn = None
	peer = None
	def __init__(self, cn, peer):
		self.cn = cn
		self.peer = peer
		
	def send(self, channel, data, reliable=False):
		if reliable:
			flags = enet.PACKET_FLAG_RELIABLE
		else:
			flags = 0
		
		packet = enet.Packet(data, flags)
		status = self.peer.send(channel, packet)
		if status < 0:
			print("%s: Error sending packet!" % self.peer.address)

class Engine(threading.Thread):
	_instance = None
	def __new__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super(Engine, cls).__new__(cls, *args, **kwargs)
		return cls._instance
	
	def __init__(self, host, port, maxclients, maxdown, maxup):
		threading.Thread.__init__(self)
		
		if port == "*":
			use_port = enet.ENET_PORT_ANY
		else:
			use_port = int(port)
			
		if host == "*":
			use_host = enet.ENET_HOST_ANY
		else:
			use_host = host
			
		address = enet.Address(use_host, use_port)
		maxclients = int(maxclients)
		maxdown = int(maxdown)
		maxup = int(maxup)
			
		self._enet_host = enet.Host(address, maxclients, 3, maxdown, maxup)
		
		self.available_cns = list(range(0,128))
		
		self.clients = {}
		self.clients_by_connect_id = {}
		
		self._running = True
		
	def stop(self):
		self._running = False
		
	def run(self):
		while self._running:
			try:
				org.cxsbs.core.slice.update()
				
				event = self._enet_host.service(5)
				
				if event.type == enet.EVENT_TYPE_CONNECT:
					print("%s: CONNECT" % event.peer.address)
					cn = self.available_cns.pop(0)
					engine_client = EngineClient(cn, event.peer)
					self.clients[cn] = engine_client
					self.clients_by_connect_id[event.peer.connectID] = engine_client
					org.cxsbs.core.events.manager.trigger_event('engine_client_connect', (engine_client,))
					
				elif event.type == enet.EVENT_TYPE_DISCONNECT:
					print("%s: DISCONNECT" % event.peer.address)
					if event.peer.connectID in self.clients_by_connect_id.keys():
						engine_client = self.clients_by_connect_id[event.peer.connectID]
						org.cxsbs.core.events.manager.trigger_event('engine_client_disconnect', (engine_client,))
						cn = event.peer.data.cn
						self.available_cns.append(cn)
						del self.clients[cn]
						del self.clients_by_connect_id[event.peer.connectID]
						
				elif event.type == enet.EVENT_TYPE_RECEIVE:
					if event.peer.connectID in self.clients_by_connect_id.keys():
						engine_client = self.clients_by_connect_id[event.peer.connectID]
						org.cxsbs.core.events.manager.trigger_event('engine_client_data', (engine_client, event.packet.data))
						
			except:
				exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()	
				org.cxsbs.core.logger.log.error("Uncaught exception occurred in server engine mainloop.")
				org.cxsbs.core.logger.log.error(traceback.format_exc())
				
@org.cxsbs.core.events.manager.event_handler("engine_client_connect")
def on_engine_client_connect(event):
	client = event.args[0]
	client.send(1, DataBuffer.pack('iiiiis', [message_types.N_SERVINFO, client.cn, 258, id(client), 0, "my test server"]), True)
	client.send(1, DataBuffer.pack('isii', [message_types.N_MAPCHANGE, "complex", 0, 1]), True)

@org.cxsbs.core.events.manager.event_handler("engine_client_disconnect")
def on_engine_client_disconnect(event):
	client = event.args[0]

unhandled_message_types = []

# math constants
PI = 3.1415927
SQRT2 = 1.4142136
SQRT3 = 1.7320508
RAD = PI / 180.0

# network quantization scale
DMF = 16.0                # for world locations
DNF = 100.0               # for normalized vectors
DVELF = 1.0               # for playerspeed based velocity vectors

import math

class vec(object):
	@staticmethod
	def from_yaw_pitch(yaw, pitch):
		x = (-math.sin(yaw)*math.cos(pitch)) 
		y = (math.cos(yaw)*math.cos(pitch))
		z = (math.sin(pitch))
		return vec(x, y, z)
	
	def __init__(self, x, y, z):
		self.v = [x, y, z]
		
	@property
	def x(self):
		return self.v[0]
	
	@x.setter
	def x(self, value):
		self.v[0] = value
		
	@property
	def y(self):
		return self.v[1]
	
	@y.setter
	def y(self, value):
		self.v[1] = value
		
	@property
	def z(self):
		return self.v[2]
	
	@z.setter
	def z(self, value):
		self.v[2] = value
		
	def mul(self, f):
		self.x *= f
		self.y *= f
		self.z *= f
		return self
		
def clamp(v, min, max):
	if v < min:
		return min
	elif v > max:
		return max
	else:
		return v

@org.cxsbs.core.events.manager.event_handler("engine_client_data")
def on_engine_client_data(event):
	client = event.args[0]
	databuf = DataBuffer.DataBuffer(event.args[1])
	
	while not databuf.empty():
		msg_type = databuf.getint()
		
		if msg_type == message_types.N_POS:
			pcn = databuf.getuint()
			databuf.get()
			flags = databuf.getuint()
			pos = {}
			for k in range(3):
				n = databuf.getchar(); n |= databuf.getchar()<<8
				if flags&(1<<k):
					n |= databuf.getchar()<<16
					if (n&0x800000):
						n |= -1<<24
				pos[k] = n/DMF;
				
			for k in range(3):
				databuf.getchar()
				
			mag = databuf.getchar()
			
			if(flags&(1<<3)):
				mag |= databuf.getchar()<<8
				
			dir = databuf.getchar()
			dir |= databuf.getchar()<<8
			
			vel = vec.from_yaw_pitch((dir%360)*RAD, (clamp(dir/360, 0, 180)-90)*RAD).mul(mag/DVELF)
			
			if(flags&(1<<4)):
				databuf.getchar()
				if(flags&(1<<5)):
					databuf.getchar()
				if(flags&(1<<6)):
					for k in range(2):
						databuf.getchar()
		
		elif msg_type == message_types.N_PING:
			clientmillis = databuf.getint()
			client.send(1, DataBuffer.pack('ii', [message_types.N_PONG, clientmillis]), False)
		
		elif msg_type == message_types.N_CLIENTPING:
			ping = databuf.getint()
			
		elif msg_type == message_types.N_CONNECT:
			name = databuf.getstring()
			pwdhash = databuf.getstring()
			playermodel = databuf.getint()
			print "New connection: '%s' with pwd: '%s' and playermodel: %d" %(name, pwdhash, playermodel)
			
		else:
			if not msg_type in unhandled_message_types:
				unhandled_message_types.append(msg_type)
				print "Unhandled message type:", msg_type
			return