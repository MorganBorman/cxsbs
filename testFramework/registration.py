from debugServerOrchestrator import TimedEventGenerator, DataRequestHandler, RepeatingEventGenerator, ServerEvent, PolicyEvent, FunctionEvent
from  debugServer import orchestrator, server

def printCallback(args):
	print str(args)

orchestrator.addEventGenerator(TimedEventGenerator(ServerEvent("server_start", (0,)), waitFrames=0))

orchestrator.addEventGenerator(TimedEventGenerator(FunctionEvent(server.connectPlayer, (0, "[FD]Chasm", 16777343)), waitFrames=20))
orchestrator.addEventGenerator(TimedEventGenerator(PolicyEvent(printCallback, "allow_message", (0, "#register fd.chasm@gmail.com foobarbash")), waitFrames=25))
orchestrator.addEventGenerator(TimedEventGenerator(PolicyEvent(printCallback, "allow_message", (0, "#login fd.chasm@gmail.com foobarbash")), waitFrames=30))
orchestrator.addEventGenerator(TimedEventGenerator(PolicyEvent(printCallback, "allow_message", (0, "#linkname")), waitFrames=35))
orchestrator.addEventGenerator(TimedEventGenerator(FunctionEvent(server.disconnectPlayer, (0,)), waitFrames=50))
orchestrator.run()

print 'Server exited normally'