class BlankObject(): pass

"""
* Info (-1) - Used by service providers to send information to the gateway
* Services (0) - Used by gateway to tell websocket clients which service providers are available
* Request (1) - Extensively used by the clients to request data and actions by the servers. (challenge requests may come from the servers to the websockets)
* Response (2) - Used by servers to send responses back that have a 1:1 relationship with certain kinds of request subtypes (like 'data' and 'command')
* Stream (3) - Used by server and gateway to send specific streams of data to clients which are subscribed.
"""

INFO = -1
SERVICES = 0
REQUEST = 1
RESPONSE = 2
STREAM = 3

types = {}
types[INFO] = "info"
types[SERVICES] = "services"
types[REQUEST] = "request"
types[RESPONSE] = "response"
types[STREAM] = "stream"

subtypes = {}

"""
* Connect (0)
* Disconnect (1)
* Authenticate (2)
* Verify (3)
* Interfaces (4)
* Subscribe (5)
* Unsubscribe (6)
"""

REQUESTS = BlankObject()
REQUESTS.CONNECT = 0
REQUESTS.DISCONNECT = 1
REQUESTS.AUTHENTICATE = 2
REQUESTS.VERIFY = 3
REQUESTS.INTERFACES = 4
REQUESTS.SUBSCRIBE = 5
REQUESTS.UNSUBSCRIBE = 6

subtypes[REQUEST] = {}
subtypes[REQUEST][REQUESTS.CONNECT] = "connect"
subtypes[REQUEST][REQUESTS.DISCONNECT] = "disconnect"
subtypes[REQUEST][REQUESTS.AUTHENTICATE] = "authenticate"
subtypes[REQUEST][REQUESTS.VERIFY] = "verify"
subtypes[REQUEST][REQUESTS.INTERFACES] = "interfaces"
subtypes[REQUEST][REQUESTS.SUBSCRIBE] = "subscribe"
subtypes[REQUEST][REQUESTS.UNSUBSCRIBE] = "unsubscribe"

RESPONSES = BlankObject()
RESPONSES.CONNECT = 0
RESPONSES.DISCONNECT = 1
RESPONSES.AUTHENTICATE = 2
RESPONSES.VERIFY = 3
RESPONSES.INTERFACES = 4
RESPONSES.SUBSCRIBE = 5
RESPONSES.UNSUBSCRIBE = 6

subtypes[RESPONSE] = {}
subtypes[RESPONSE][RESPONSES.CONNECT] = "connect"
subtypes[RESPONSE][RESPONSES.DISCONNECT] = "disconnect"
subtypes[RESPONSE][RESPONSES.AUTHENTICATE] = "authenticate"
subtypes[RESPONSE][RESPONSES.VERIFY] = "verify"
subtypes[RESPONSE][RESPONSES.INTERFACES] = "interfaces"
subtypes[RESPONSE][RESPONSES.SUBSCRIBE] = "subscribe"
subtypes[RESPONSE][RESPONSES.UNSUBSCRIBE] = "unsubscribe"
