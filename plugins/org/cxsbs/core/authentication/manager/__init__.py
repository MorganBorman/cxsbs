import pyTensible, org

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
    
class AuthenticationEvent(object):
    cn = None
    name = None
    domain = None
    global_id = None
    timeout_timer = None
    
    def __init__(self, cn, name, domain, global_id):
        self.cn = cn
        self.name = name
        self.domain = domain
        self.global_id = global_id
        

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
        
        #initialise the container for this particular authentication attempt
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
        global_id = event.args[0]
        challenge = event.args[1]
        
        #if there isn't a pending request then don't do anything
        if not global_id in self.global_pending_requests.keys():
            return 
        
        #move the event from the pending_requests to the pending_challenges
        authEv = self.global_pending_requests[global_id]
        self.global_pending_challenges[global_id] = authEv
        del self.global_pending_requests[global_id]
        
        if authEv.timeout_timer is not None:
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
        challEv = event.args[0]
        global_id = challEv.global_id
        
        #remove the pending global challenge
        if global_id in self.global_pending_challenges.keys():
                del self.global_pending_challenges[global_id]
        
        #TODO: tell the client that an authentication timeout occurred
    
    def on_client_auth_challenge_response(self, event):
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
        
        if authEv.timeout_timer is not None:
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
        global_id = event.args[0]
        credential = event.args[1]
        
        if not global_id in self.global_pending_verifications.keys():
            return
        
        authEv = self.global_pending_verifications[global_id]
        del self.global_pending_verifications[global_id]
        
        if authEv.timeout_timer is not None:
            authEv.timeout_timer.cancel()
            authEv.timeout_timer = None
        
        client = org.cxsbs.core.clients.get_client(authEv.cn)
        
        client.sessionvars['credentials'][authEv.domain] = credential
        
        #TODO: tell client that they're verified
    
    def on_authority_deny(self, event):
        global_id = event.args[0]
        
        if not global_id in self.global_pending_verifications.keys():
            return
        
        authEv = self.global_pending_verifications[global_id]
        del self.global_pending_verifications[global_id]
        
        if authEv.timeout_timer is not None:
            authEv.timeout_timer.cancel()
            authEv.timeout_timer = None
        
        #TODO: tell client that authentication has been denied
        
    def on_authority_timeout(self, event):
        authenticationEvent = event.args[0]
        global_id = authenticationEvent.global_id
        
        #remove the matching auth request from the pending dictionaries
        if global_id in self.global_pending_requests.keys():
                del self.global_pending_requests[global_id]
        
        if global_id in self.global_pending_challenges.keys():
                del self.global_pending_challenges[global_id]
        
        if global_id in self.global_pending_verifications.keys():
                del self.global_pending_verifications[global_id]
                
        #TODO: tell the client which made the auth request that it has been dropped
        
        
        
        