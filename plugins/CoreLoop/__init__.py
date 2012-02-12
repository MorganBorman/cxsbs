import cxsbs.Plugin

class Plugin(cxsbs.Plugin.Plugin):
	def __init__(self):
		cxsbs.Plugin.Plugin.__init__(self)
		
	def load(self):
		reactor.startRunning() #@UndefinedVariable
		
	def unload(self):
		global dont_iterate
		dont_iterate = True
		reactor.stop()

import traceback
import threading
from twisted.internet import reactor
	
##############################
##	Event loop stuff		##
##############################

flag = threading.Event()
exec_queue = []
exec_sync_queue = []
running = False
main_thread = None

def execLater(func, args):
	'''Call function at a later time with arguments in tuple args.'''
	exec_queue.append((func, args))
	
def execSynchronized(event_flag):
	"""
	Takes an threading.Event() object and adds it to the queue of events to be processed.
	somebody is expected to signal the flag in this module when they're done processing.
	"""
	exec_sync_queue.append(event_flag)

def triggerExecQueue():
	for event in exec_queue:
		try:
			event[0](*event[1])
		except:
			exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
			print 'Uncaught exception execLater queue.'
			print traceback.format_exc()
			print traceback.extract_tb(exceptionTraceback)
	del exec_queue[:]
	
def triggerSyncExecQueue():
	while len(exec_sync_queue) > 0:
		event_flag = exec_sync_queue.pop(0)
		flag.clear()
		event_flag.set()
		#print "Holding main thread while synchronized execution occurs"
		flag.wait()
		#print "Sychronized execution correctly triggered flag."

def update():
		global running
		if not running:
			running = True
	
		global main_thread
		if main_thread == None:
			main_thread = threading.current_thread()
		
		reactor.runUntilCurrent() #@UndefinedVariable
		reactor.doIteration(0) #@UndefinedVariable
		triggerExecQueue()
		triggerSyncExecQueue()