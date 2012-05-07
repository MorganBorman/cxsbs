import pyTensible, org

class main_master(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        Interfaces = {}
        Resources = {'MasterServerAuthority': MasterServerAuthority}
        
        org.cxsbs.core.threads.thread_manager.start('user_stats')
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        pass
    
import MainMaster

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.main_master')

@org.cxsbs.core.settings.manager.Setting
def master_enabled():
    """
    @category main_master
    @display_name Main master enabled
    @wbpolicy never
    @doc Should this server connect to a main master server.
    """
    return True

@org.cxsbs.core.settings.manager.Setting
def master_domain():
    """
    @category main_master
    @display_name Main master domain
    @wbpolicy never
    @doc Domain for which the main master is an authority.
    """
    return "cxsbs.org"
   
@org.cxsbs.core.settings.manager.Setting
def master_host():
    """
    @category main_master
    @display_name Main master host
    @wbpolicy never
    @doc Host at which the main master can be found.
    """
    return "localhost"

@org.cxsbs.core.settings.manager.Setting
def master_port():
    """
    @category main_master
    @display_name Main master port
    @wbpolicy never
    @doc Port at which the main master can be found.
    """
    return 28787

class RemoteCredential(org.cxsbs.core.authentication.interfaces.ICredential):
    def __init__(self, domain, groups, names):
        self._domain = domain
        self._groups = []
        for group in groups:
            self._groups.append('.'.join((group, self._domain)))
        self._names = names
    
    @property
    def groups(self):
        return self._groups[:]
    
    def deauthorize(self):
        pass
    
class MasterServerAuthority(org.cxsbs.core.authentication.interfaces.IAuthority):
    def __init__(self):
        self.master_client = MainMaster.MasterClient (  self,
                                                        domain          = settings['master_domain'], 
                                                        master_host     = settings['master_host'], 
                                                        master_port     = settings['master_port'], 
                                                        server_port     = org.cxsbs.core.server.instance.port, 
                                                        update_interval = 60*10,
                                                     )
        self.master_client.start()
        
        event_manager = org.cxsbs.core.events.manager.event_manager
        event_manager.register_handler('client_stat_events_recorded', self.on_client_stat_events_recorded)
    
    @property
    def domains(self):
        return [settings['master_domain']]
    
    def request(self, auth_ev):
        self.master_client.authentication_request(auth_ev.global_id, auth_ev.name)
    
    def validate(self, auth_ev, answer):
        self.master_client.authentication_response(auth_ev.global_id, answer)
        
    def shutdown(self):
        self.master_client.stop_client()
            
    #call-backs for master clients are below
            
    def on_challenge(self, domain, global_id, challenge):
        org.cxsbs.core.events.manager.trigger_event('authority_challenge', (global_id, challenge))
            
    def on_authorize(self, domain, global_id, groups, names):
        org.cxsbs.core.events.manager.trigger_event('authority_authorize', (global_id, RemoteCredential(domain, groups, names)))
    
    def on_deny(self, domain, global_id):
        org.cxsbs.core.events.manager.trigger_event('authority_deny', (global_id,))
        
    def on_client_stat_events_recorded(self, event):
        '''
        @thread user_stats
        '''
        
        if not self.master_client.connected:
            return
        
        stat_events = event.args[0]
        
        def format_line(stat_event):
            return "su %s\n" % " ".join(map(str, stat_event))
        
        message = "".join(map(format_line, stat_events))
        
        self.master_client.stats_update(message)

