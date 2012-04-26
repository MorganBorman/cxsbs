General
---------------

These are the request messages which the client sends to the gateway and which are multiplexed correctly out to the servers with the added client cn.


subtypes
---------------

* auth (0)
* veri (1)
* data (2)
* frsh (3)

Authentication
-------------------------

{type: 2, subtype: 0, domain: 'example.com', name: 'foo'}
{type: 2, cn: 300, subtype: 0, domain: 'example.com', name: 'foo'}

Verification
-------------------------

gid: 	This is the id of the challenge to which this is an answer.
answer: This is the answer to the challenge request sent by the server.

{type: 2, subtype: 1, gid: 3452, answer: 'f373de2d49584e7a16166e76b1bb925f24f0130c63ac9332'}
{type: 2, cn: 300, subtype: 1, gid: 3452, answer: 'f373de2d49584e7a16166e76b1bb925f24f0130c63ac9332'}	

Data
-------------------------

rqid:	This is the request id. It must be supplied with the 

{type: 2, subtype: 2, rqid: 1253, datatype: "stats", query: "all&age=31&sort=frags&range=(25)0:"}
{type: 2, cn: 300, subtype: 2, rqid: 1253, datatype: "stats", query: "all&age=31&sort=frags&range=(25)0:"}