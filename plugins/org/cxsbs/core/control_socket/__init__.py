import pyTensible, org

import os
import socket
import threading
import select
import json
import encoding

class control_socket(pyTensible.Plugin):
    def __init__(self):
        pyTensible.Plugin.__init__(self)
        
    def load(self):
        
        self.control_socket = ControlSocket()
        self.control_socket.start()
        
        event_manager = org.cxsbs.core.events.manager.event_manager
        
        event_manager.register_handler('client_connect', self.control_socket.on_client_connect)
        
        Interfaces = {}
        Resources = {}
        
        return {'Interfaces': Interfaces, 'Resources': Resources}
        
    def unload(self):
        self.control_socket.stop()

settings = org.cxsbs.core.settings.manager.Accessor('org.cxsbs.core.control_socket')
    
@org.cxsbs.core.settings.manager.Setting
def uds_path():
    """
    @category control_gateway
    @display_name UDS Path
    @wbpolicy never
    @doc Path to create unix domain socket at.
    """
    return "%s/control.uds" % org.cxsbs.core.server.instance.root
   
@org.cxsbs.core.settings.manager.Setting
def max_clients():
    """
    @category control_gateway
    @display_name Max clients
    @wbpolicy never
    @doc Maximum number of simultaneous client connections.
    """
    return 3
   
def count_preceeding_matches(string, pos, char):
    "Count the number of matches to character immediately preceding the given position in string"
    count = 0
    pos -= 1
    while pos >= 0 and string[pos] == char:
        count += 1
        pos -= 1
    return count

class ControlSocket(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            os.unlink(settings['uds_path'])
        except OSError:
            pass
        self.socket.bind(settings['uds_path'])
        self.socket.listen(settings['max_clients'])
        
        #sock: ControlClient
        self.clients = {}
        
        self.running = True
        
    def run(self):
        while self.running:
            
            wait_socks = [self.socket] + self.clients.keys()

            try:
                rfds, wfds, efds = select.select(wait_socks, [], [])
                if self.running:
                    for rfd in rfds:
                        if rfd == self.socket:
                            self.handle_connect()
                        else:
                            self.clients[rfd].handle()
            except select.error:
                pass
                    
    def stop(self):
        self.running = False
        self.socket.shutdown(2)
                    
    def handle_connect(self):
        sock, address = self.socket.accept()
        self.clients[sock] = ControlClient(self, sock, address)
        
    def on_client_connect(self, event):
        cn = event.args[0]
        client = org.cxsbs.core.clients.get_client(cn)
        
        for control_client in self.clients.values():
            control_client.on_client_connect(client)
    
    def disconnect(self, sock):
        if sock in self.clients.keys():
            del self.clients[sock]
            
class ControlClient(object):
    def __init__(self, control, sock, address):
        self.control = control
        self.socket = sock
        self.address = address
        
        self.buffer = ""
        
        #pcn: PseudoClient
        self.clients = {}
        
        info_message = {"type": encoding.INFO, "name": org.cxsbs.core.server.instance.name}
        self.send(json.dumps(info_message))
        print "control client connected. %s" %str(self.address)

    def disconnect(self):
        for pcn in self.clients.keys():
            org.cxsbs.core.events.manager.trigger_event('client_disc', (pcn,))
        
        self.control.disconnect(self.socket)
        
    def send(self, datum):
        self.socket.send(datum + "\n")

    def handle(self):
        '''handle incoming messages for this client'''
        
        data = self.socket.recv(1024)
        if len(data) <= 0:
            print "control client disconnected."
            self.disconnect()
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
        '''handle an incoming datum for this client'''
        message_handler_name = "on_gateway_message_" + encoding.types[datum['type']]
        if message_handler_name in dir(self):
            self.__getattribute__(message_handler_name)(datum)
        else:
            print "Error (unhandled gateway client message type):", encoding.types[datum['type']]
            
    def on_gateway_message_request(self, datum):
        if datum['subtype'] == encoding.REQUESTS.CONNECT:
            pseudo_client = PseudoClient(self, *datum['data'])
            
            cn = org.cxsbs.core.clients.client_manager.connect_pseudoclient(pseudo_client)
            
            self.clients[cn] = pseudo_client
            
            cr_message = {"type": encoding.RESPONSE, 'subtype': encoding.RESPONSES.CONNECT, "reqid": datum['reqid'], 'data': [cn]}
            self.send(json.dumps(cr_message))
        else:
            pass
        
class PseudoClient(object):
    def __init__(self, control_client, address):
        self.control_client = control_client
        self.address = address
        