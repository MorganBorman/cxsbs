import time

def notStale(generator):
	return not generator.stale

class Generator:
	def __init__(self):
		self.stale = False
		pass
	
	def frame(self, time, frameCount):
		pass
	
	def request(self, time, frame, type, args=()):
		pass
	
class FunctionEvent:
	def __init__(self, func, args):
		self.func = func
		self.args = args
	
	def trigger(self):
		self.func(*self.args)
	
class ServerEvent:
	def __init__(self, type, args):
		self.type = type
		self.args = args
	
	def trigger(self):
		import cxsbs
		Events = cxsbs.getResource("Events")
		Events.triggerServerEvent(self.type, self.args)
		
class PolicyEvent:
	def __init__(self, callback, type, args):
		self.callback = callback
		self.type = type
		self.args = args
		
	def trigger(self):
		import cxsbs
		Events = cxsbs.getResource("Events")
		self.callback(Events.triggerPolicyEvent(self.type, self.args))

class TimedEventGenerator(Generator):
	"""An event generator that triggers an event after a given amount of time for frames have elapsed"""
	def __init__(self, event, waitTime=None, waitFrames=None):
		"""
		waitTime is the number of seconds to wait until firing the event.
		waitFrames is the number of frames to wait until firing the event
		
		Providing both waitTime and waitFrames will cause the generator to fire for whichever comes first but still only fire once.
		
		"""
		Generator.__init__(self)
		
		self.event = event
		
		self.hasFired = False
		self.hasSetTargets = False
		
		#these get set on the first frame
		self.targetTime = None
		self.targetFrame = None
		
		self.waitTime = waitTime
		self.waitFrames = waitFrames
		
	def setTargets(self, time, frame):
		"""sets self.targetTime and self.targetFrame"""
		if self.waitTime != None:
			self.targetTime = time + self.waitTime
			
		if self.waitFrames != None:
			self.targetFrame = frame + self.waitFrames
			
		#causes a timed event to fire immediately and the repeating one to fire on every frame
		if self.waitFrames == None and self.waitTime == None:
			self.targetFrame = frame + 0
			
		self.hasSetTargets = True
		
	def isTime(self, time, frame):
		"""Checks whether or not it is time for the event to fire"""
		if self.targetTime != None:
			if self.targetTime <= time:
				return True
			
		if self.targetFrame != None:
			if self.targetFrame <= frame:
				return True
	
		return False
	
	def frame(self, time, frameCount):
		if not self.hasSetTargets:
			self.setTargets(time, frameCount)

		if not self.hasFired:
			if self.isTime(time, frameCount):
				self.trigger()
				self.hasFired = True
				self.stale = True
				return
			
	def trigger(self):
		self.event.trigger()
	
class RepeatingEventGenerator(TimedEventGenerator):
	"""An event generator that triggers an event at a given interval"""
	def __init__(self, event, waitTime=None, waitFrames=None):
		"""
		waitTime is the number of seconds to wait until firing the event.
		waitFrames is the number of frames to wait until firing the event
		
		Providing both waitTime and waitFrames will cause the generator to fire once for whichever of the two occurs first.
		
		"""
		#just like a TimedEventGenerator except we reset the targets after each trigger
		TimedEventGenerator.__init__(self, event, waitTime, waitFrames)
		
	def frame(self, time, frameCount):
		if (not self.hasSetTargets) or self.hasFired:
			self.setTargets(time, frameCount)
			self.hasFired = False

		if not self.hasFired:
			if self.isTime(time, frameCount):
				self.trigger()
				self.hasFired = True
				return
			
class UnhandledRequest(Exception):
	'''A handler was not present for a particular data request'''
	def __init__(self, value):
		Exception.__init__(self, value)
	
class DataRequestHandler:
	"""A class allowing definition of the correct responses to various data requests"""
	def __init__(self, func):
		self.func = func
	
	def request(self, time, frame, args):
		return self.func(time, frame, args)

class Orchestrator:
	def __init__(self, maxFps=30, maxFrames=None, printFrame=False, printEvents=False, printFps=False, printAverageFps=True):
		self.maxFps = maxFps
		self.secondsPerFrame = 1.00/maxFps
		self.maxFrames = maxFrames
		self.frameCount = 0
		
		self.fpsData = []
		
		self.printFrame = printFrame
		self.printEvents = printEvents
		self.printFps = printFps
		self.printAverageFps = printAverageFps
		
		self.running = False
		
		self.generators = []
		self.handlers = {}
		
	def addEventGenerator(self, generator):
		self.generators.append(generator)
		
	def addRequestHandler(self, type, handler):
		self.handlers[type] = handler
		
	def request(self, type, args):
		if self.printEvents:
			print "orchestrator: request:", type, args
		if type in self.handlers.keys():
			return self.handlers[type].request(time.time(), self.frameCount, args)
		else:
			raise UnhandledRequest(type)
		
	def frame(self):
		if self.printFrame:
			print "Frame %s occurred..." % self.frameCount
		
		import cxsbs
		Events = cxsbs.getResource("Events")
		Events.update()
		
		for generator in self.generators:
			generator.frame(time.time(), self.frameCount)
		
		self.generators = filter(notStale, self.generators)
			
	def keepRunning(self):
		if not self.running:
			return False
		
		if self.maxFrames == None or self.frameCount <= self.maxFrames: 
			return True
		
		return False
	
	def getAverageFps(self):
		return (sum(self.fpsData)/float(len(self.fpsData)))
		
	def run(self):
		self.startTime = time.time()
		
		currentSecond = time.time()
		framesThisSecond = 1
		
		self.running = True
		while self.keepRunning():
			frameStartTime = time.time()
			self.frame()
			self.frameCount += 1
			
			if int(time.time()) == int(currentSecond):
				framesThisSecond += 1
			else:
				self.fpsData.append(framesThisSecond)
				if self.printFps:
					print "fps: %d" % framesThisSecond
				currentSecond = time.time()
				framesThisSecond = 1
			
			frameEndTime = time.time()
			
			#slow things down to the correct fps
			frameDelay = (self.startTime + (self.secondsPerFrame*self.frameCount))-time.time()
			frameLag = self.secondsPerFrame-(frameEndTime - frameStartTime)
			
			if frameLag > 0:
				time.sleep(frameLag)
			
			elif frameDelay > 0:
				time.sleep(frameDelay)
				
		if self.printAverageFps:
			print "The test ran at an average fps of %.2f" % (sum(self.fpsData)/float(len(self.fpsData)))
