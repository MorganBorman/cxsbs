#Overview

This portion of this protocol document will detail the response message format.

This is how service providers give websocket clients feedback about requests.

Responses are messages which have a 1:1 correspondance with requests and contain a the status or data associated with a request.
The request identifier and client identifier are stripped by the gateway and used to determine which websocket client to return the request to.

#Subtypes

* Connect (0)
* Disconnect (1)
* Authenticate (2)
* Verify (3)
* Interfaces (4)
* Subscribe (5)
* Unsubscribe (6)
* Extended responses (100...)
