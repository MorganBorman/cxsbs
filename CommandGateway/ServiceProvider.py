"""

"""

import socket
import encoding
import json

def count_preceeding_matches(string, pos, char):
    "Count the number of matches to character immediately preceding the given position in string"
    count = 0
    pos -= 1
    while pos >= 0 and string[pos] == char:
        count += 1
        pos -= 1
    return count

class ServiceProvider(object):
    def __init__(self, gateway_server, socket_path):
        
        self.gateway_server= gateway_server
        self.socket_path = socket_path
        
        self.name = None
            
        self.connected = False
        self.buffer = ""
        
        #pseudo-client number: GatewayClient
        self.cns = {}
        
    def send(self, datum):
        if not self.connected:
            return
        
        self.socket.send(datum + "\n")
        
    def connect(self):
        if self.connected:
            return True
        
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        
        self.connected = False
        try:
            self.socket.connect(self.socket_path)
            self.connected = True
        except socket.error:
            self.socket.close()
            print "There was an error connecting to the server control socket at", self.socket_path
            
        return self.connected
        
    def handle(self):
        data = self.socket.recv(1024)
        if len(data) <= 0:
            self.gateway_server.service_provider_disconnected(self.socket)
            self.connected = False
        else:
            self.buffer += data
        
        next_nl_pos = self.buffer.find("\n")
        while next_nl_pos != -1:
            pm = count_preceeding_matches(self.buffer, next_nl_pos, "\\")
            #if there is an even number of escape characters then this newline is not escaped
            if pm % 2 == 0:
                datum, self.buffer = self.buffer[:next_nl_pos], self.buffer[next_nl_pos+1:]
                self.handle_datum(json.loads(datum))
            else:
                next_nl_pos = self.buffer.find("\n", next_nl_pos+1)
                
            if len(self.buffer):
                next_nl_pos = self.buffer.find("\n")
            else:
                next_nl_pos = -1
    
    def handle_datum(self, datum):
        if self.name is None:
            if datum['type'] == encoding.INFO:
                self.name = datum['name']
            self.gateway_server.ServiceProviderConnected.emit(self)
        else:
            self.gateway_server.ServiceProviderMessage.emit(self, datum)