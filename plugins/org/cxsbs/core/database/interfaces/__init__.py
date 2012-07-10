import pyTensible, abc

class interfaces(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {'IDataSchema': IDataSchema}
        Resources = {}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
class IDataSchema(object):
    __metaclass__ = abc.ABCMeta