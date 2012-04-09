import pyTensible, org

class modified(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        org.cxsbs.core.clients.client_manager.game_vars_template['org.cxsbs.core.maps.modified'] = False
        
        Interfaces = {}
        Resources = {'mark': mark}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.maps.modified')
    
@org.cxsbs.core.settings.manager.Setting
def unspectate_allowed():
    """
    @category permissions
    @display_name Allow unspecate
    @wbpolicy never
    @doc Groups whose members should be allowed to unspectate even if they have modified maps.
    """
    return []

@org.cxsbs.core.settings.manager.Setting
def unspectate_denied():
    """
    @category permissions
    @display_name Deny unspecate
    @wbpolicy never
    @doc Groups whose members should be disallowed to unspectate if they have modified maps.
    """
    return []
    
def mark(client):
    "Marks a client as having a modified map and notifies other players if conditions are appropriate."
    if not client.gamevars['org.cxsbs.core.maps.modified']:
        client.gamevars['org.cxsbs.core.maps.modified'] = True

        org.cxsbs.core.server.state.message("A client has a modified map.")

@org.cxsbs.core.policies.policy_handler("client_can_unspectate_self")
def on_client_can_unspectate_self(query):
    client = query.args[0]
    
    if client.gamevars['org.cxsbs.core.maps.modified']:
        if not client.isActionPermitted("org.cxsbs.core.maps.modified.unspectate"):
            return False