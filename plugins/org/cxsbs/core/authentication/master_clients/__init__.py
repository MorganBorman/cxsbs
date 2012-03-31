import pyTensible, org

class master_clients(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        Interfaces = {}
        Resources = {'MasterServerAuthority': MasterServerAuthority}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
import MasterClient

configured_servers =        (
                                ('localhost', 'localhost', 28780, 10),
                            )

configured_aliases =        (
                                ('', 'localhost'),
                            )

class RemoteCredential(org.cxsbs.core.authentication.interfaces.ICredential):
    def __init__(self, domain):
        self._domain = domain
    
    @property
    def groups(self):
        return (self._domain,)
    
    def deauthorize(self):
        pass
    
class MasterServerAuthority(org.cxsbs.core.authentication.interfaces.IAuthority):
    def __init__(self):
        self.master_clients = {}
        
        for server in configured_servers:
            self.master_clients[server[0]] = MasterClient.MasterClient (   self,
                                                                        domain=server[0], 
                                                                        master_host=server[1], 
                                                                        master_port=server[2], 
                                                                        server_port=28785, 
                                                                        update_interval=server[3],
                                                                    )
            self.master_clients[server[0]].start()
            
        for server_alias in configured_aliases:
            self.master_clients[server_alias[0]] = self.master_clients[server_alias[1]]
    
    @property
    def domains(self):
        #TODO:   Make a setting initialized in org.cxsbs.core.server to specify the domain name of this server instance
        #        then use that here.
        return self.master_clients.keys()
    
    def request(self, auth_ev):
        self.master_clients[auth_ev.domain].authentication_request(auth_ev.global_id, auth_ev.name)
    
    def validate(self, auth_ev, answer):
        self.master_clients[auth_ev.domain].authentication_response(auth_ev.global_id, answer)
        
    def shutdown(self):
        for master_client in self.master_clients.values():
            master_client.stop_client()
            
    #call-backs for master clients are below
            
    def on_challenge(self, domain, global_id, challenge):
        org.cxsbs.core.events.manager.trigger_event('authority_challenge', (global_id, challenge))
            
    def on_authorize(self, domain, global_id):
        org.cxsbs.core.events.manager.trigger_event('authority_authorize', (global_id, RemoteCredential(domain)))
    
    def on_deny(self, domain, global_id):
        org.cxsbs.core.events.manager.trigger_event('authority_deny', (global_id,))
        