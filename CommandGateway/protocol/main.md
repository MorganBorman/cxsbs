#Overview

One of the goals of this protocol is that the gateway should be able to be stateless for the most part.
There are only a few exceptions to this

* The gateway must keep track of whether or not a websocket handshake has taken place and process one first before proceeding with the rest of it's business for each client.
* The gateway must keep a cn associated with each server for each client. This is then attached to any requests which the gateway forwards on to the servers.


##Message types

* Status (0) - Used by servers to broadcast general status messages. 
* Control (1) - Used by servers and clients to issue commands regarding the connection to the gateway.
* Request (2) - Extensively used by the clients to request data and actions by the servers. Used for a few things like authentication the other way.
* Response (3) - Used by servers to send responses back that have a 1:1 relationship with certain kinds of request subtypes (like 'data' and 'command')
* Update (4) - Used by servers to broadcast data updates regarding the game and public server configuration (like mastermode)

##Message subtypes

Each message type will have it's own set of supported subtypes which will dictate the rest of the attributes associated with the message.

##General format

from websocket to gateway:
*{type: 2, subtype: ...

from gateway to server:
*{type: 2, cn: 300, subtype: ...


##Details

Each message type will have a section below. 
Each message route ie. (Server - Gateway - Client) will have a subsection within that.

#Status

##Server - Gateway - Client

