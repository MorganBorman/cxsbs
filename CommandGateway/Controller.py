import encoding
import json

class ClientProviderRelation(object):
    def __init__(self, cn, client, provider):
        self.cn = cn
        self.client = client
        self.provider = provider

class ClientProviderRelationTable(object):
    def __init__(self):
        self.clients_providers = {}
        self.providers_cns = {}
        
    def add(self, cn, client, provider):
        print "Adding relation:", cn, client, provider
        
        relation = ClientProviderRelation(cn, client, provider)
        
        self.clients_providers[(client, provider)] = relation
        self.providers_cns[(provider, cn)] = relation

    def remove(self, value1, value2):
        if (value1, value2) in self.clients_providers.keys():
            relation = self.clients_providers[(value1, value2)]
        elif (value1, value2) in self.providers_cns.keys():
            relation = self.providers_cns[(value1, value2)]
        else:
            return
            
        del self.clients_providers[(relation.client, relation.provider)]
        del self.providers_cns[(relation.provider, relation.cn)]
        
    def lookup(self, value1, value2):
        if (value1, value2) in self.clients_providers.keys():
            return self.clients_providers[(value1, value2)]
        elif (value1, value2) in self.providers_cns.keys():
            return self.providers_cns[(value1, value2)]
        else:
            return None

class Controller(object):
    def __init__(self, gateway_server):
        self.gateway_server = gateway_server
        
        self.gateway_server
        
        self.gateway_server.ServiceProviderConnected.connect(self.on_service_provider_connect)
        self.gateway_server.ServiceProviderMessage.connect(self.on_service_provider_message)
        self.gateway_server.ServiceProviderDisconnected.connect(self.on_service_provider_disconnect)
        
        self.gateway_server.GatewayClientConnected.connect(self.on_gateway_client_connect)
        self.gateway_server.GatewayClientMessage.connect(self.on_gateway_client_message)
        self.gateway_server.GatewayClientDisconnected.connect(self.on_gateway_client_disconnect)
        
        self.global_request_id = 0
        
        #reqid: (client, service provider)
        self.pending_client_connect_requests = {}
        
        self.relation_table = ClientProviderRelationTable()
        
    @property
    def next_request_id(self):
        try:
            return self.global_request_id
        finally:
            self.global_request_id += 1
        
    @property
    def service_providers(self):
        return filter(lambda x: x.name != None, self.gateway_server.service_providers.values())
        
    @property
    def gateway_clients(self):
        return filter(lambda x: x.handshaken, self.gateway_server.gateway_clients.values())
    
    def on_service_provider_connect(self, service_provider):
        services = {}
        for service_provider in self.service_providers:
            services[id(service_provider)] = service_provider.name
        
        services_message = {'type': encoding.SERVICES, 'services': services}
        services_message_data = json.dumps(services_message)
            
        for gateway_client in self.gateway_clients:
            
            #connect the each client to the new service provider
            connect_request_id = self.next_request_id
            connect_request_message = {'type': encoding.REQUEST, 'subtype': encoding.REQUESTS.CONNECT, 'reqid': connect_request_id, 'data': [gateway_client.address[0]]}
            connect_request_message_data = json.dumps(connect_request_message)
            service_provider.send(connect_request_message_data)
            self.pending_client_connect_requests[connect_request_id] = (gateway_client, service_provider)
            
            #send each client the new service provider list
            gateway_client.send(services_message_data)
    
    def on_service_provider_message(self, service_provider, datum):
        message_handler_name = "on_service_provider_" + encoding.types[datum['type']]
        if message_handler_name in dir(self):
            self.__getattribute__(message_handler_name)(service_provider, datum)
        else:
            print "Error (unhandled service provider message type):", encoding.types[datum['type']]
            print "Handler:", message_handler_name, "not found."
    
    def on_service_provider_disconnect(self, service_provider):
        for gateway_client in self.gateway_clients:
            relation = self.relation_table.lookup(gateway_client, service_provider)
            
            if relation is None:
                continue
            
            disconnect_message = {'type': encoding.REQUEST, 'subtype': encoding.REQUESTS.DISCONNECT, 'reqid': self.next_request_id, 'cn': relation.cn, 'data': []}
            
            disconnect_request_message_data = json.dumps(disconnect_request_message)
            service_provider.send(disconnect_request_message_data)
    
    def on_gateway_client_connect(self, gateway_client):
        services = {}
        print "Client connected.", gateway_client.address
        for service_provider in self.service_providers:
            #connect the client to each service provider
            connect_request_id = self.next_request_id
            connect_request_message = {'type': encoding.REQUEST, 'subtype': encoding.REQUESTS.CONNECT, 'reqid': connect_request_id, 'data': [gateway_client.address[0]]}
            connect_request_message_data = json.dumps(connect_request_message)
            service_provider.send(connect_request_message_data)
            self.pending_client_connect_requests[connect_request_id] = (gateway_client, service_provider)
            
            services[id(service_provider)] = service_provider.name
        
        services_message = {'type': encoding.SERVICES, 'services': services}
        services_message_data = json.dumps(services_message)
        gateway_client.send(services_message_data)
    
    def on_gateway_client_message(self, gateway_client, datum):
        message_handler_name = "on_gateway_client_" + encoding.types[datum['type']]
        if message_handler_name in dir(self):
            self.__getattribute__(message_handler_name)(gateway_client, datum)
        else:
            print "Error (unhandled gateway client message type):", encoding.types[datum['type']]
            print "Handler:", message_handler_name, "not found."
    
    def on_gateway_client_disconnect(self, gateway_client):
        for service_provider in self.service_providers:
            relation = self.relation_table.lookup(gateway_client, service_provider)
            
            if relation is None:
                continue
            
            disconnect_request_message = {'type': encoding.REQUEST, 'subtype': encoding.REQUESTS.DISCONNECT, 'reqid': self.next_request_id, 'cn': relation.cn, 'data': []}
            
            disconnect_request_message_data = json.dumps(disconnect_request_message)
            service_provider.send(disconnect_request_message_data)
            
    ###########################################################################
    ##                    Service Provider message handlers                  ##
    ###########################################################################
    
    def on_service_provider_response(self, service_provider, datum):
        message_handler_name = "on_service_provider_response_" + encoding.subtypes[datum['type']][datum['subtype']]
        if message_handler_name in dir(self):
            self.__getattribute__(message_handler_name)(service_provider, datum)
        else:
            print "Error (unhandled service provider response message subtype):", encoding.subtypes[datum['type']][datum['subtype']]
            print "Handler:", message_handler_name, "not found."
            
    def on_service_provider_response_connect(self, service_provider, datum):
        #reqid: (client, service provider)
        #self.pending_client_connect_requests
        
        reqid = datum['reqid']
        cn = datum['data'][0]
        
        if not reqid in self.pending_client_connect_requests.keys():
            return
        
        client, pending_service_provider = self.pending_client_connect_requests.pop(reqid)
        
        if pending_service_provider is not service_provider:
            return
        
        self.relation_table.add(cn, client, service_provider)
    
    ###########################################################################
    ##                    Gateway Client message handlers                    ##
    ###########################################################################
    
    
    

