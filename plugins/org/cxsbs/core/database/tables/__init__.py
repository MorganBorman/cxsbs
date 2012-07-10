import pyTensible, org

class tables(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        Interfaces = {}
        Resources = {}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
@org.cxsbs.core.settings.manager.Setting
def prefix():
    """
    @category db_tables
    @display_name Master servers
    @wbpolicy never
    @doc What prefix should all cxsbs database tables have.
    """
    return "cxsbs_rodon_"