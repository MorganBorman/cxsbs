"""
Connects to all the server unix domain sockets and acts as a multiplexer between the data from them and the websocket clients.
"""

from GatewayServer import GatewayServer
from Controller import Controller
                    
gateway_server = GatewayServer("", 9999, 5, "control_sockets.cfg")
controller = Controller(gateway_server)
gateway_server.run()