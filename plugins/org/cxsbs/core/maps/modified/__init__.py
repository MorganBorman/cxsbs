import pyTensible, org

class modified(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        Interfaces = {}
        Resources = {'mark': mark}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
def mark(client):
    "Marks a client as having a modified map and notifies other players if conditions are appropriate."
    pass