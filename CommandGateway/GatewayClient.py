import struct
import hashlib
import base64
import json

def unmask(data, mask):
    "return the data unmasked"
    
    data = map(ord, data)
    mask = map(ord, mask)
    
    i = 0
    while i < len(data):
        data[i] = data[i] ^ mask[i % 4]
        i += 1
        
    return ''.join(map(chr, data))

class GatewayClient(object):
    def __init__(self, gateway_server, sock, address):
        self.gateway_server = gateway_server
        self.socket = sock
        self.address = address
        self.buffer = ""
        self.handshaken = False
        
        #ServiceProvider: pseudo-client number
        self.cns = {}
        
    def send(self, msg):
        if len(msg) <= 125:
            data = struct.pack('!BB', 0x81, len(msg)) + msg
        elif len(msg) <= 2**16:
            data = struct.pack('!BBH', 0x81, 0x7E, len(msg)) + msg
        elif len(msg) <= 2**64:
            data = struct.pack('!BBQ', 0x81, 0x7F, len(msg)) + msg
        
        self.socket.send(data)
        
    def read(self):
        '''
        Returns the next complete message from the buffer including unmasking said message.
        
        If no complete message is available then the buffer is left untouched and None is returned.
        '''
        #pre-header length. the amount of stuff before we get to the mask or the data
        phl = 2
        dl = 0
        
        if len(self.buffer) <= phl:
            return None
        
        if self.buffer[0] == '\x81':
            pass
        elif self.buffer[0] == '\x88':
            self.socket.close()
            self.gateway_server.gateway_client_disconnected(self.socket)
            print "Client disconnected."
            return None
        else:
            raise Exception("Received non text data from client")
        
        masked = (0x80 & ord(self.buffer[1])) != 0x00
        size = (0x7F & ord(self.buffer[1]))
        
        if size <= 125:
            total_size = 2 + size + 4*int(masked)
            
            if len(self.buffer) < total_size:
                return None
            
            dl = size
                
        elif size == 126:
            if len(self.buffer) < 4:
                return None
            
            size = struct.unpack("!H", self.buffer[2:4])[0]
            
            print size
            
            total_size = 4 + size + 4*int(masked)
            
            if len(self.buffer) < total_size:
                return None
            
            phl += 2
            dl = size
            
        elif size == 127:
            if len(self.buffer) < 10:
                return None
            
            size = struct.unpack("!Q", self.buffer[2:10])[0]
            
            total_size = 4 + size + 4*int(masked)
            
            if len(self.buffer) < total_size:
                return None
            
            phl += 8
            dl = size
        
        hl = phl + 4*int(masked)
        
        data = self.buffer[hl:hl+dl]
        
        if masked:
            mask = self.buffer[phl:hl]
            data = unmask(data, mask)
        
        self.buffer = self.buffer[hl+dl:]
        
        return data
        
    def handle(self):
        data = self.socket.recv(1024)
        self.buffer += data
        
        if not self.handshaken:
            #buffer until we hit '\r\n\r\n' then pass it to handshake()
            pos = self.buffer.find('\r\n\r\n')
            if pos != -1:
                data, self.buffer = self.buffer.split('\r\n\r\n', 1)
                self.handshake(data)
        else:
            datum = self.read()
            if datum != None:
                self.handle_datum(json.loads(datum))
                
    def handshake(self, data):
        lines = data.split('\r\n')
        
        data = {}
        
        location = lines[0].split(' ')[1]
        
        for line in lines:
            if ': ' in line:
                key, value = line.split(': ', 1)
                data[key] = value
                
        sha1 = hashlib.sha1()
        sha1.update(data['Sec-WebSocket-Key'] + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11")
        
        response = []
        
        line = "HTTP/1.1 101 Switching Protocols"
        response.append(line)
        line = "Upgrade: %s" % data['Upgrade']
        response.append(line)
        line = "Connection: %s" % data['Connection']
        response.append(line)
        line = "Sec-WebSocket-Accept: %s" % base64.b64encode(sha1.digest())
        response.append(line) 
        line = "WebSocket-Origin: %s" % data['Origin']
        response.append(line) 
        line = "WebSocket-Location: ws://%s%s" % (data['Host'], location)
        response.append(line)
        #line = "WebSocket-Protocol: %s" % protocol
        #response.append(line)
        
        response = '\r\n'.join(response) + '\r\n\r\n'
        
        self.socket.send(response)
        
        self.handshaken = True
        
        self.gateway_server.GatewayClientConnected.emit(self)
            
    def handle_datum(self, datum):
        self.gateway_server.GatewayClientMessage.emit(self, datum)

