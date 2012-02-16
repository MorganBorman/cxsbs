totalFrames = 1800
number_of_players = 100
is_instagib = False

##############################################################
##############################################################

from debugServer import orchestrator, server, Player
from debugServerOrchestrator import TimedEventGenerator, DataRequestHandler, RepeatingEventGenerator, ServerEvent, FunctionEvent

orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("server_start", ()), waitFrames=0))

number_of_players += 1
playerObjects = {}

global totalEvents
totalEvents = 0

import random

ips = random.sample(xrange(0, 4294967296), number_of_players)
sessionIds = random.sample(xrange(0000000, 9999999), number_of_players)

weapon_data = {}
weapon_data[0] = {'damage': 50, 'partial': False, 'increment': None, 'reload': 8}
weapon_data[1] = {'damage': 200, 'partial': True, 'increment': 20, 'reload': 42}
weapon_data[2] = {'damage': 30, 'partial': False, 'increment': None, 'reload': 3}
weapon_data[3] = {'damage': 120, 'partial': True, 'increment': 1, 'reload': 24}
weapon_data[4] = {'damage': 100, 'partial': False, 'increment': None, 'reload': 45}
weapon_data[5] = {'damage': 75, 'partial': True, 'increment': 1, 'reload': 15}
weapon_data[6] = {'damage': 25, 'partial': False, 'increment': None, 'reload': 15}

class Weapon:
	"A class holding logic for generating fake weapon use"
	def __init__(self, type):
		self.type = type
		self.weapon_data = weapon_data[type]
		
	def activate(self, cn, frame):
		global totalEvents
		
		for i in range(random.randint(3, 10)):
			orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_spend_damage", (cn, self.weapon_data['damage'])), waitFrames=frame))
			totalEvents += 1
			
			if random.choice([True, False]):
				if self.weapon_data['partial']:
					hits = random.choice(range(self.weapon_data['increment'],self.weapon_data['damage'],self.weapon_data['increment']))
					
					damage = hits * self.weapon_data['increment']
				else:
					damage = self.weapon_data['damage']
			
			
				orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_inflict_damage", (cn, damage)), waitFrames=frame))
				totalEvents += 1
			
			frame += self.weapon_data['reload']
			
		return frame
	
def getWeapon(onlyexploding=False):
	if is_instagib:
		return Weapon(4)
		
	if onlyexploding:
		return Weapon(random.choice([3,5]))
	else:
		return Weapon(random.randint(0,6))

for cn in range(1, number_of_players):
	name = "testing" + str(cn)
	if cn % 2 == 0:
		team = "evil"
	else:
		team = "good"
		
	ip = ips.pop(0)
	
	sessionId = sessionIds.pop(0)
	
	player = Player(cn, name, team, ip, sessionId)
	
	playerObjects[cn] = player
	
	connection_time = random.randint(20, 150)

	orchestrator.addEventGenerator(TimedEventGenerator(FunctionEvent(server.connectPlayer, (player, )), waitFrames=connection_time))
	totalEvents += 1
	
	frame = connection_time + 10
	
	while frame < totalFrames:
		z = random.choice([1,2,3])
		
		if z == 1:
			weapon = getWeapon()
			frame = weapon.activate(cn, frame)
			orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_frag", (player.cn, random.randint(1,number_of_players-1))), waitFrames=frame))
			totalEvents += 1
		elif z == 2:
			weapon = getWeapon()
			frame = weapon.activate(cn, frame)
			orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_teamkill", (player.cn, random.randint(1,number_of_players-1))), waitFrames=frame))
			totalEvents += 1
		elif z == 3:
			if random.choice([True, False]) and not is_instagib:
				weapon = getWeapon(True)
				frame = weapon.activate(cn, frame)
			orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("player_suicide", (player.cn, )), waitFrames=frame))
			totalEvents += 1
		
		frame += random.randint(1, 5)
	
	orchestrator.addEventGenerator(TimedEventGenerator(FunctionEvent(server.disconnectPlayer, (player,)), waitFrames=totalFrames-5))
	totalEvents += 1

print "This test run will execute %d events." % totalEvents

import cxsbs
orchestrator.addEventGenerator(TimedEventGenerator(FunctionEvent(cxsbs.shutdown, ()), waitFrames=totalFrames))

orchestrator.run()