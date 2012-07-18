#Overview

This protocol document will describe the flow of data between the CommandCenter websocket clients and the services providers which the CommandGateway is connected to.

The basic concept is that the gateway connects to a list of service providers. (like game server and master servers)

All service providers have a common interface which includes the following
* Handle connection requests
* Handle verification requests
* Handle requests for a list of extended interfaces supported
* Handle requests for a list of streams
* Handle requests to subscribe to a stream
* Handle requests to unsubscribe from a stream
* Handle requests which are part of the extended interfaces supported
* Send responses to requests
* Send stream data

The gateway does the following for websocket clients.
* Handle a disconnect control message.
* Handle websocket connections and handshakes
* Send a list of service providers upon connection and resend when it changes.
* Add request identifiers to client requests and forward them to the specified service provider.
* Intercept and store a client identifier upon a successful verification request to a service provider and append that identifier to all further requests.
* Forward response messages and stream messages to the correct client
* Notify service providers which are connected to a websocket when that client disconnects

The websocket clients have the following capabilities
* Handle lists of service providers
* Send connection requests to service providers
* Handle challenges and send verification requests
* Handle lists of extended interfaces
* Open extended interfaces and associated streams
* Pass incoming stream data to the associated open extended interfaces
* Close extended interfaces and associated streams

##Message types

* Services (0) - Used by gateway to tell websocket clients which service providers are available
* Request (1) - Extensively used by the clients to request data and actions by the servers. (challenge requests may come from the servers to the websockets)
* Response (2) - Used by servers to send responses back that have a 1:1 relationship with certain kinds of request subtypes (like 'data' and 'command')
* Stream (3) - Used by server and gateway to send specific streams of data to clients which are subscribed.

##Message subtypes

Each of the message types Request, Response, and Stream will have it's own set of supported subtypes which will dictate the rest of the attributes associated with the message.

##General format

from gateway to websocket:
* {type: 1, subtype: #, data: []}

from websocket to gateway:
* {type: 1, subtype: ...

from gateway to server:
* {type: 1, cn: 300, subtype: ...

from server to gateway:
* {type: 2, cn: 300, subtype: ...

from gateway to websocket:
* {type: 2, subtype: ...

from server to gateway:
* {type: 3, cns: [300], subtype: ...

from gateway to websocket:
* {type: 3, subtype: ...

#Details

* [[Disconnect]]
* [[Services]]
* [[Request]]
* [[Response]]
* [[Stream]]


