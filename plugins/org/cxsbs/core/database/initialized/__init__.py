import pyTensible, org

class initialized(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        database_manager = org.cxsbs.core.database.manager.database_manager
        
        database_manager.connect()
        org.cxsbs.core.database.manager.SchemaBase.metadata.create_all(database_manager.engine)
        
        Interfaces = {}
        Resources = {}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass