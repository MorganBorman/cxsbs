"""
Connects to all the server unix domain sockets and acts as a multiplexer between the data from them and the websocket clients.

When a new client connects notify all connected servers. These will at their leisure return a pseudo-client-number (pcn) which will
be used in future communications to describe where commands are coming from and who to send data back to.
"""

from GatewayServer import GatewayServer
                    
gateway_server = GatewayServer("", 9999, 5)
gateway_server.run()