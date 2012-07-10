import pyTensible, org

import operator
from groups.Query import Select, Compare

class manager(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        org.cxsbs.core.clients.client_manager.session_vars_template['credentials'] = {}
        
        self.authentication_manager = AuthenticationManager()
        
        event_manager = org.cxsbs.core.events.manager.event_manager
        
        event_manager.register_handler('client_auth_request', self.authentication_manager.on_client_auth_request)
        event_manager.register_handler('client_auth_challenge_response', self.authentication_manager.on_client_auth_challenge_response)
        event_manager.register_handler('client_auth_timeout', self.authentication_manager.on_client_auth_timeout)
        
        event_manager.register_handler('authority_challenge', self.authentication_manager.on_authority_challenge)
        event_manager.register_handler('authority_authorize', self.authentication_manager.on_authority_authorize)
        event_manager.register_handler('authority_deny', self.authentication_manager.on_authority_deny)
        event_manager.register_handler('authority_timeout', self.authentication_manager.on_authority_timeout)
        
        Interfaces = {}
        Resources = {}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        self.authentication_manager.shutdown()
        
import threading

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.authentication.manager')

@org.cxsbs.core.settings.manager.Setting
def specific_announced_authentication_domains():
    """
    @category authentication
    @display_name Announced authentication domains
    @wbpolicy never
    @doc Which authentication domains should be announced publicly upon success.
    """
    return ["sauerbraten.org"]

@org.cxsbs.core.settings.manager.Setting
def generic_announced_authentication_domains():
    """
    @category authentication
    @display_name Announced authentication domains
    @wbpolicy never
    @doc Which authentication domains should be announced without mentioning the auth name.
    """
    return ["example.com"]

@org.cxsbs.core.messages.Message
def specific_authentication_success_message():
    """
    @fields name ip auth_name domain
    @doc The message broadcasted to the rest of the clients when a client has successfully authenticated.
    """
    return "${info}${green}${name}${white} has authenticated with ${blue}${domain}${white} as ${magenta}${auth_name}${white}."

@org.cxsbs.core.messages.Message
def generic_authentication_success_message():
    """
    @fields name ip domain
    @doc The message broadcasted to the rest of the clients when a client has successfully authenticated.
    """
    return "${info}${green}${name}${white} is verified with ${blue}${domain}${white}."

@org.cxsbs.core.messages.Message
def client_authentication_success_message():
    """
    @fields auth_name domain
    @doc The message sent to a client when they successfully authenticate.
    """
    return "${info}You have authenticated with ${blue}${domain}${white} as ${magenta}${auth_name}${white}."

@org.cxsbs.core.messages.Message
def client_authentication_failure_message():
    """
    @fields auth_name domain reason
    @doc The message sent to a client when their authentication attempt fails.
    """
    return "${denied}You could not be authenticated with ${blue}${domain}${white} as ${magenta}${auth_name}${white}. (${reason})"
    
class AuthenticationEvent(object):
    cn = None
    name = None
    domain = None
    global_id = None
    timeout_timer = None
    display_domain = None
    
    def __init__(self, cn, name, domain, global_id):
        self.cn = cn
        self.name = name
        self.domain = domain
        self.global_id = global_id
        self.display_domain = domain

class AuthenticationManager(object):
    def __init__(self):
        
        self.global_id_counter = 0
        self.global_pending_requests = {}
        self.global_pending_challenges = {}
        self.global_pending_verifications = {}
        
        self.authorities = {}
        
        for authority_class in pyTensible.plugin_loader.get_providers("org.cxsbs.core.authentication.interfaces.IAuthority").values():
            authority = authority_class()
            
            for domain in authority.domains:
                self.authorities[domain] = authority
                
    def shutdown(self):
        for authority in self.authorities.values():
            authority.shutdown()
    
    def on_client_auth_request(self, event):
        '''
        @thread authentication
        '''
        cn = event.args[0]
        name = event.args[1]
        domain = event.args[2]
        
        #see whether we have an authority for this domain
        if not domain in self.authorities.keys():
            #TODO: tell the client that authentication cannot be handled
            pass
        
        #get the global id for this authentication
        global_id = self.global_id_counter
        if self.global_id_counter > 10000:
            self.global_id_counter = 0
        else:
            self.global_id_counter += 1
        
        #initialize the container for this particular authentication attempt
        authEv = AuthenticationEvent(cn, name, domain, global_id)
        self.global_pending_requests[global_id] = authEv
        
        #pass the authentication request over to the correct authority
        self.authorities[domain].request(authEv)
        
         #create timeout timer for the authorities response
        timeout_event = org.cxsbs.core.events.manager.Event('authority_timeout', (authEv,), {})
        timeout_timer = org.cxsbs.core.timers.Timer(5, (timeout_event,))
        authEv.timeout_timer = timeout_timer
        org.cxsbs.core.timers.timer_manager.add_timer(timeout_timer)
        
    def on_authority_challenge(self, event):
        '''
        @thread authentication
        '''
        global_id = event.args[0]
        challenge = event.args[1]
        
        #if there isn't a pending request then don't do anything
        if not global_id in self.global_pending_requests.keys():
            return 
        
        #move the event from the pending_requests to the pending_challenges
        authEv = self.global_pending_requests[global_id]
        self.global_pending_challenges[global_id] = authEv
        del self.global_pending_requests[global_id]
        
        if authEv.timeout_timer != None:
            authEv.timeout_timer.cancel()
            authEv.timeout_timer = None

        #send actual challenge to client
        client = org.cxsbs.core.clients.get_client(authEv.cn)
        client.challengeAuth(global_id, authEv.domain, challenge)
        
         #create timeout timer for the clients response
        timeout_event = org.cxsbs.core.events.manager.Event('client_auth_timeout', (authEv,), {})
        timeout_timer = org.cxsbs.core.timers.Timer(5, (timeout_event,))
        authEv.timeout_timer = timeout_timer
        org.cxsbs.core.timers.timer_manager.add_timer(timeout_timer)
        
    def on_client_auth_timeout(self, event):
        '''
        @thread authentication
        '''
        challEv = event.args[0]
        global_id = challEv.global_id
        
        #remove the pending global challenge
        if global_id in self.global_pending_challenges.keys():
                del self.global_pending_challenges[global_id]
                
        org.cxsbs.core.events.manager.trigger_event('client_auth_finished', (challEv.cn, False))
        
        try:
            client = org.cxsbs.core.clients.get_client(challEv.cn)
        except KeyError:
            return
                
        fields = {'auth_name': challEv.name, 'domain': challEv.display_domain, 'reason': "challenge timed out"}
        client_authentication_failure_message.server(client, fields=fields)
        
    
    def on_client_auth_challenge_response(self, event):
        '''
        @thread authentication
        '''
        cn = event.args[0]
        global_id = event.args[1]
        answer = event.args[2]
        
        #see whether we have a pending global challenge
        if not global_id in self.global_pending_challenges.keys():
            return
        
        #move the event from the pending_requests to the pending_challenges
        authEv = self.global_pending_challenges[global_id]
        self.global_pending_verifications[global_id] = authEv
        del self.global_pending_challenges[global_id]
        
        if authEv.timeout_timer != None:
            authEv.timeout_timer.cancel()
            authEv.timeout_timer = None
        
        #pass the challenge response over to the correct authority
        self.authorities[authEv.domain].validate(authEv, answer)
        
        #create timeout timer for the authorities response
        timeout_event = org.cxsbs.core.events.manager.Event('authority_timeout', (authEv,), {})
        timeout_timer = org.cxsbs.core.timers.Timer(5, (timeout_event,))
        authEv.timeout_timer = timeout_timer
        org.cxsbs.core.timers.timer_manager.add_timer(timeout_timer)
    
    def on_authority_authorize(self, event):
        '''
        @thread authentication
        '''
        global_id = event.args[0]
        credential = event.args[1]
        
        if not global_id in self.global_pending_verifications.keys():
            return
        
        authEv = self.global_pending_verifications[global_id]
        del self.global_pending_verifications[global_id]
        
        if authEv.timeout_timer != None:
            authEv.timeout_timer.cancel()
            authEv.timeout_timer = None
        
        try:
            client = org.cxsbs.core.clients.get_client(authEv.cn)
        except KeyError:
            return
        
        client.sessionvars['credentials'][authEv.domain] = credential
        
        #Get a group for all the players but the individual in question.
        broadcast_group = org.cxsbs.core.clients.AllClientsGroup.query(Select(cn=Compare(client.cn, operator=operator.ne))).all()
        
        if authEv.display_domain in settings['specific_announced_authentication_domains']:
            fields = {'name': client.name, 'ip': client.ip, 'auth_name': authEv.name, 'domain': authEv.display_domain}
            specific_authentication_success_message.server(broadcast_group, fields=fields)
            
        elif authEv.display_domain in settings['generic_announced_authentication_domains']:
            fields = {'name': client.name, 'ip': client.ip, 'domain': authEv.display_domain}
            generic_authentication_success_message.server(broadcast_group, fields=fields)
            
        fields = {'auth_name': authEv.name, 'domain': authEv.display_domain}
        client_authentication_success_message.server(client, fields=fields)
        
        #TODO: tell client that they're verified
        org.cxsbs.core.events.manager.trigger_event('client_auth_finished', (authEv.cn, True))
    
    def on_authority_deny(self, event):
        '''
        @thread authentication
        '''
        global_id = event.args[0]
        
        if not global_id in self.global_pending_verifications.keys():
            return
        
        authEv = self.global_pending_verifications[global_id]
        del self.global_pending_verifications[global_id]
        
        if authEv.timeout_timer != None:
            authEv.timeout_timer.cancel()
            authEv.timeout_timer = None
            
        org.cxsbs.core.events.manager.trigger_event('client_auth_finished', (authEv.cn, False))
                
        try:
            client = org.cxsbs.core.clients.get_client(authEv.cn)
        except KeyError:
            return
            
        fields = {'auth_name': authEv.name, 'domain': authEv.display_domain, 'reason': "credentials refused"}
        client_authentication_failure_message.server(client, fields=fields)
        
    def on_authority_timeout(self, event):
        '''
        @thread authentication
        '''
        authEv = event.args[0]
        global_id = authEv.global_id
        
        #remove the matching auth request from the pending dictionaries
        if global_id in self.global_pending_requests.keys():
                del self.global_pending_requests[global_id]
        
        if global_id in self.global_pending_challenges.keys():
                del self.global_pending_challenges[global_id]
        
        if global_id in self.global_pending_verifications.keys():
                del self.global_pending_verifications[global_id]
                
        org.cxsbs.core.events.manager.trigger_event('client_auth_finished', (authEv.cn, False))
                
        try:
            client = org.cxsbs.core.clients.get_client(authEv.cn)
        except KeyError:
            return
                
        fields = {'auth_name': authEv.name, 'domain': authEv.display_domain, 'reason': "server timed out"}
        client_authentication_failure_message.server(client, fields=fields)