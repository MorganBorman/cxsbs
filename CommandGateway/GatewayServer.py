from GatewayClient import GatewayClient
from Server import Server

import socket
import select

import random
import cube2crypto

token = format(random.getrandbits(128), 'X')
SECRET_KEY, PUBLIC_KEY = cube2crypto.genkeypair(token)

print "Private server key:", SECRET_KEY

class GatewayServer(object):
    def __init__(self, interface, port, maxclients):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((interface, port))
        self.socket.listen(maxclients)
        
        #sock: GatewayServer
        self.servers = {}
        
        self.initialize_server_connections("control_sockets.cfg")
        
        self.next_gid = 0;
    
        #sock: GatewayClient
        self.clients = {}
        
    def get_challenges(self, client, domain, name):
        "Forward the request on to the servers or in the case of 'local' create the challenge right here."
        if domain == "gateway" and name == "admin":
            challenge, client.gateway_pending_answer = cube2crypto.genchallenge(PUBLIC_KEY, format(random.getrandbits(64), 'X'))
            client.gateway_pending_gid = self.next_gid;
            self.next_gid += 1;
            challenge_string = "{type: 2, subtype: 0, gid: %d, challenge: '%s'}" % (client.gateway_pending_gid, challenge)
            client.send(challenge_string)
        else:
            pass
        
    def initialize_server_connections(self, filename):
        "Reads the control socket list and calls connect_server for each"
        f = open(filename, 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            self.connect_server(line)
        
    def connect_server(self, path):
        "Connect to a server control socket given its uds path"
        print "Connecting to server control socket at", path
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(path)
            self.servers[sock] = Server(sock)
        except socket.error:
            sock.close()
            print "There was an error connecting to the server control socket at", path
        
    def disconnect(self, sock):
        if sock in self.clients.keys():
            client = self.clients[sock]
            del self.clients[sock]
            
            for server in self.servers.values():
                if server.name in client.credentials.keys():
                    server.close_cds(clients.credentials[server.name])
        
    def run(self):
        while True:
            
            rlist = [self.socket] + self.servers.keys() + self.clients.keys() 
            wlist = []
            xlist = []
            
            rfds, wfds, efds = select.select(rlist, wlist, xlist)
            
            for rfd in rfds:
                if rfd == self.socket:
                    sock, address = self.socket.accept()
                    self.clients[sock] = GatewayClient(self, sock, address)
                    
                elif rfd in self.servers.keys():
                    self.servers[rfd].handle()
                    
                elif rfd in self.clients.keys():
                    self.clients[rfd].handle()