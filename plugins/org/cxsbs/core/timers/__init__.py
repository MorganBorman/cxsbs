import pyTensible, abc, org

class timers(pyTensible.Plugin):
	def __init__(self):
		pyTensible.Plugin.__init__(self)
		
	def load(self):
		self.timerManager = RTimerManager()
		self.timerManager.start()
		
		Interfaces = {'ITimerManager': ITimerManager, 'ITimer': ITimer}
		Resources = {'timer_manager': self.timerManager, 'Timer': RTimer}
		
		return {'Interfaces': Interfaces, 'Resources': Resources}
		
	def unload(self):
		self.timerManager.stop()
		self.timerManager.join()
	
import threading, time

class ITimer:
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def cancel(self):
		pass
	
	@abc.abstractproperty
	def timeleft(self):
		pass
	
	@abc.abstractproperty
	def events(self):
		pass
	
class ITimerManager:
	__metaclass__ = abc.ABCMeta
	
	@abc.abstractmethod
	def add_timer(self, timer):
		pass
	
class RTimer(ITimer):
	_canceled = False
	_expired_time = -1
	_events = []
	
	def __init__(self, how_long, *events):
		events = org.cxsbs.core.events.manager
		
		start_time = time.time()
		
		ITimer.__init__(self)
		self._expired_time = start_time + how_long
		for event in events:
			if not isinstance(event, events.IEvent):
				raise TypeError("Expected an event object implementing the IEvent interface. Got an object of %s class." %event.__class__.__name__)
		self._events = events[:]
		
	def cancel(self):
		self._canceled = True
		
	@property
	def timeleft(self):
		if not self._canceled:
			timeleft = self._expired_time - time.time()
			if timeleft <= 0.0:
				return 0
			else:
				return timeleft
		else:
			return None
		
	@property
	def events(self):
		return self._events[:]
	
class RTimerManager(ITimerManager, threading.Thread):
	_timers = []
	_running = False
	
	def __init__(self):
		ITimerManager.__init__(self)
		threading.Thread.__init__(self)
		self._event = threading.Event()
		self._semaphore = threading.Semaphore()
		self._timers = []
		self._running = True
		
	def _calc_wait_time(self):
		min_wait = None
		
		for timer in self._timers:
			if min_wait is None:
				min_wait = timer.timeleft
			elif min_wait > timer.timeleft:
				min_wait = timer.timeleft
			else:
				pass #it's not sooner
			
		return min_wait
		
	def run(self):
		while self._running or len(self._timers) > 0:
			
			self._event.wait(self._calc_wait_time())
			self._event.clear()
			
			self._semaphore.acquire()
			old_timer_list = self._timers
			self._timers = []
			self._semaphore.release()
			
			for timer in old_timer_list:
				if timer.timeleft == None:
					pass #discard this timer
				elif timer.timeleft <= 0:
					self._fire_off(timer.events)
				else:
					self._timers.append(timer)
					
	def stop(self):
		self._running = False
		self._event.set()
					
	def _fire_off(self, events):
		events = org.cxsbs.core.events.manager
		
		for event in events:
			events.event_manager.trigger_event(event)
		
	def add_timer(self, timer):
		if not isinstance(timer, ITimer):
			raise TypeError("Expected a timer object implementing the ITimer interface. Got an object of %s class." %timer.__class__.__name__)
		
		self._semaphore.acquire()
		self._timers.append(timer)
		self._semaphore.release()
		
		self._event.set()
		