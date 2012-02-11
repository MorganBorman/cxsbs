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
from twisted.internet import reactor
	
##############################
##	Event loop stuff		##
##############################

exec_queue = []

def execLater(func, args):
	'''Call function at a later time with arguments in tuple args.'''
	exec_queue.append((func, args))

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

def update():
		reactor.runUntilCurrent() #@UndefinedVariable
		reactor.doIteration(0) #@UndefinedVariable
		triggerExecQueue()