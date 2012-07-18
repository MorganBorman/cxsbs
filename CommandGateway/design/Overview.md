#Overview

The CommandGateway is a system which maintains a bunch of connections to service providers like CXSBS servers and CXSBS Main master servers
and facilitates certain kinds of interactions for websocket clients which connect.

It's function is very simple. When a websocket client connects it tell the websocket client which service providers are available.
Then the websocket client may "connect" to one or more of these service providers. 

When a websocket client initiates a connection to a service provider the service provider returns a client identifier to the gateway.
This client identifier is stored along with the connection data for the websocket client and used to route traffic from the service provider
back to the websocket client.

Two kinds of messages get sent from service providers to websocket clients. The first is the response message. The second is the stream message.


#Structure

The command gateway has the following structure.

* main               - Starts up the main GatewayServer class with the correct permissions.
* GatewayServer      - Contains the main logic for managing a collection of UDS sockets and websocket connections.
* GatewayClient      - Contains the main logic for initiating connections with and reading from websockets.
* ServiceProvider    - Contains the main logic for reading from the UDS service provider sockets.
* Controller         - Contains the main application logic concerned with routing and manipulating messages between the GatewayClients and the ServiceProviders
