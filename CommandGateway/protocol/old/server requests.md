General
---------------

These are the requests which are sent from the servers to the gateway and are sent on to the correct websocket client based on the cn specified


subtypes
---------------

* chal (0)
* veri (1)
* cred (2)

ws->gw->sv
---------------


	Authentication
	-------------------------
	
	{T: 'R', S: 'auth', D: 'example.com', N: 'foo'}
	{type: 'request', cn: 300, subtype: 'auth', domain: 'example.com', name: 'foo'}
	
	
	Verification
	-------------------------
	
	{T: 'R', S: 'veri', G: 3452, A: 'f373de2d49584e7a16166e76b1bb925f24f0130c63ac9332'}
	{type: 'request', cn: 300, subtype: 'veri', gid: 3452, answer: 'f373de2d49584e7a16166e76b1bb925f24f0130c63ac9332'}
	
	
sv->gw->ws
---------------

	Challenge
	-------------------------
	
	