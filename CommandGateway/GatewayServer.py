from GatewayClient import GatewayClient
from ServiceProvider import ServiceProvider

from Signals import SignalObject, Signal

import socket
import select
import os
import json
import time

class GatewayServer(SignalObject):
    
    ServiceProviderConnected = Signal
    GatewayClientConnected = Signal
    
    ServiceProviderMessage = Signal
    GatewayClientMessage = Signal
    
    ServiceProviderDisconnected = Signal
    GatewayClientDisconnected = Signal
    
    def __init__(self, interface, port, maxclients, service_providers_config):
        SignalObject.__init__(self)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((interface, port))
        self.socket.listen(maxclients)
        
        self.service_providers_config = service_providers_config
        
        self.last_service_provider_check = 0
        
        #list of ServiceProvider
        self.disconnected_service_providers = []
        
        #sock: ServiceProvider
        self.service_providers = {}
        
        #sock: GatewayClient
        self.gateway_clients = {}
        
        self.initialize_service_providers()
        
    def initialize_service_providers(self):
        "Reads the control socket list and calls connect_server for each"
        f = open(self.service_providers_config, 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            if len(line) and line[-1] == "\n":
                line = line[:-1]
            uds_socket_path = os.path.abspath(line)
            self.disconnected_service_providers.append(ServiceProvider(self, uds_socket_path))
        
    def check_service_providers(self):
        if time.time() - self.last_service_provider_check < 300:
            return
        
        self.last_service_provider_check = time.time()
        
        temp_disconnected_service_providers = self.disconnected_service_providers
        self.disconnected_service_providers = []
        
        for service_provider in temp_disconnected_service_providers:
            if service_provider.connect():
                self.service_providers[service_provider.socket] = service_provider
            else:
                self.disconnected_service_providers.append(service_provider)
        
    def service_provider_disconnected(self, sock):
        if sock in self.service_providers.keys():
            service_provider = self.service_providers[sock]
            del self.service_providers[sock]
            self.disconnected_service_providers.append(service_provider)
            
            self.ServiceProviderDisconnected.emit(service_provider)
        
    def gateway_client_disconnected(self, sock):
        if sock in self.gateway_clients.keys():
            client = self.gateway_clients[sock]
            del self.gateway_clients[sock]
            
            if client.handshaken:
                self.GatewayClientDisconnected.emit(client)
        
    def run(self):
        while True:
            self.check_service_providers()
            
            rlist = [self.socket] + self.service_providers.keys() + self.gateway_clients.keys() 
            wlist = []
            xlist = []
            
            rfds, wfds, efds = select.select(rlist, wlist, xlist)
            
            for rfd in rfds:
                if rfd == self.socket:
                    sock, address = self.socket.accept()
                    self.gateway_clients[sock] = GatewayClient(self, sock, address)
                    
                elif rfd in self.service_providers.keys():
                    self.service_providers[rfd].handle()
                    
                elif rfd in self.gateway_clients.keys():
                    self.gateway_clients[rfd].handle()

