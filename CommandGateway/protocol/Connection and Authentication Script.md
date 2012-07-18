
#Connecting

* Client connects to gateway
* Gateway sends connect requests to each service provider
    {type: 1, subtype: 0, reqid: 453, data: [ip_address]}
* Service providers respond with cns
    {type: 2, subtype: 0, reqid: 453, data: [5]}
    {type: 2, subtype: 0, reqid: 453, data: [8]}
    {type: 2, subtype: 0, reqid: 453, data: [5]}

#Authenticating

* Client sends authentication request to gateway
    {type: 1, subtype: 2, data: [domain, auth_name]}
* Gateway send the request message out to each service provider
    {type: 1, subtype: 2, reqid: 454, cn: 5, data: [domain, auth_name]}
    {type: 1, subtype: 2, reqid: 454, cn: 8, data: [domain, auth_name]}
    {type: 1, subtype: 2, reqid: 454, cn: 5, data: [domain, auth_name]}
* Each service provider responds with a response message
    {type: 2, subtype: 2, reqid: 454, cn: 5, data: [domain, auth_name, challenge]}
    {type: 2, subtype: 2, reqid: 454, cn: 8, data: [domain, auth_name, challenge]}
    {type: 2, subtype: 2, reqid: 454, cn: 5, data: [domain, auth_name, challenge]}
* The challenges are forwarded to the Client
    {type: 2, subtype: 2, data: [454, domain, auth_name, {service provider id: challenge, service provider id: challenge, service provider id: challenge}]}
* The Client sends a verify request to gateway
    {type: 1, subtype: 3, data: [454, {service provider id: answer, service provider id: answer, service provider id: answer}]}
* Gateway sends the verify request message out to each service provider
    {type: 1, subtype: 3, reqid: 455, cn: 5, data: [454, answer]}
    {type: 1, subtype: 3, reqid: 455, cn: 8, data: [454, answer]}
    {type: 1, subtype: 3, reqid: 455, cn: 5, data: [454, answer]}
* Each service provider response with a response message
    {type: 2, subtype: 3, reqid: 455, cn: 5, data: [True]}
    {type: 2, subtype: 3, reqid: 455, cn: 8, data: [True]}
    {type: 2, subtype: 3, reqid: 455, cn: 5, data: [True]}
* Gateway sends a response message back to client indicating that the authentication attempt is finished
    {type: 2, subtype: 3, data[{service provider id: True, service provider id: True, service provider id: True}]}
    
