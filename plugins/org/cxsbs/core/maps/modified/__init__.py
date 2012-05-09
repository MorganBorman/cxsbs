import pyTensible, org

import operator
from groups.Query import Select, Compare

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

@org.cxsbs.core.messages.Message
def modified_map_broadcast_message():
    """
    @fields name ip map_name mode_name
    @doc The message broadcasted to the rest of the clients when a client has a modified map.
    """
    return "${warning}${green}${name}${white} has a ${red}modified${white} map."

@org.cxsbs.core.messages.Message
def modified_map_client_message():
    """
    @fields name ip map_name mode_name
    @doc The message sent to the client when a they have a modified map.
    """
    return "${warning}You have a ${red}modified${white} map."

@org.cxsbs.core.messages.Message
def modified_map_client_message_unspectate_denied():
    """
    @fields name ip map_name mode_name
    @doc The message sent to the client when a they have a modified map and are denied from entering the game.
    """
    return "${denied}You have a ${red}modified${white} map. You must use the official maps if you wish to play."
    
def mark(client):
    "Marks a client as having a modified map and notifies other players if conditions are appropriate."
    if not client.gamevars['org.cxsbs.core.maps.modified']:
        client.gamevars['org.cxsbs.core.maps.modified'] = True
        
        fields = {'name': client.name, 'ip': client.ip, 'map_name': org.cxsbs.core.server.state.map_name, 'mode_name': org.cxsbs.core.server.state.game_mode}
        
        #Get a group for all the players but the individual in question.
        broadcast_group = org.cxsbs.core.clients.AllClientsGroup.query(Select(cn=Compare(client.cn, operator=operator.ne))).all()
        
        #send the messages
        modified_map_broadcast_message.server(broadcast_group, fields=fields)
        modified_map_client_message.server(client, fields=fields)
        
        if not client.isActionPermitted("org.cxsbs.core.maps.modified.unspectate"):
            client.spectator = True

@org.cxsbs.core.policies.policy_handler("client_can_unspectate_self")
def on_client_can_unspectate_self(query):
    client = query.args[0]
    
    if client.gamevars['org.cxsbs.core.maps.modified']:
        if not client.isActionPermitted("org.cxsbs.core.maps.modified.unspectate"):
            fields = {'name': client.name, 'ip': client.ip, 'map_name': org.cxsbs.core.server.state.map_name, 'mode_name': org.cxsbs.core.server.state.game_mode}
            modified_map_client_message_unspectate_denied.server(client, fields=fields)
            return False