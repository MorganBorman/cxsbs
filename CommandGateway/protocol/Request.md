#Overview

This portion of this protocol document will detail the request message format.

This is how websocket clients make changes to and get data from the service providers.

Requests are messages send by websocket clients which the gateway augments with a request identifier and a client identifier and sends to the correct service provider.

#Subtypes

* Connect (0)
* Disconnect (1)
* Authenticate (2)
* Verify (3)
* Interfaces (4)
* Subscribe (5)
* Unsubscribe (6)
* Extended requests (100...)

#Gateway to Service providers

##Connect

{type: 1, subtype: 0, reqid: #, data: [ip_address]}

##Disconnect

{type: 1, subtype: 1, reqid: #, cn: #, data: []}

##Authenticate

{type: 1, subtype: 2, reqid: #, cn: #, data: [domain, auth_name]}

#Clients to Gateway

##Authenticate

{type: 1, subtype: 2, data: [domain, auth_name]}

##Verify

{type: 
