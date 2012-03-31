import pyTensible, abc

class interfaces(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {'IEventManager': IEventManager, 'IHandlerInformation': IHandlerInformation, 'IEvent': IEvent}
        Resources = {}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
class IEvent:
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def name(self):
        pass
    
    @abc.abstractproperty
    def args(self):
        pass
    
    @abc.abstractproperty
    def kwargs(self):
        pass
    
class IHandlerInformation:
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractproperty
    def name(self):
        pass
    
    @abc.abstractproperty
    def event_name(self):
        pass
    
    @abc.abstractproperty
    def handler(self):
        pass
    
    @abc.abstractproperty
    def thread(self):
        pass
    
    @abc.abstractproperty
    def documentation(self):
        pass

class IEventManager:
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def register_handler(self, name, handler):
        pass
    
    @abc.abstractmethod
    def trigger_event(self, event):
        pass