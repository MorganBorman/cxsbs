#Overview

This portion of this protocol document will detail the services message format.

This is how the gateway tells the websocket clients which service providers are available.

The full list is transmitted every time and the websocket clients should replace the previous list with the new one.

{type: 0, services: {0: "Main master", 1: "[FD] Mars"}}

The websocket clients may assume that any service providers which have been removed from the list are no-longer available.
Further if they were connected to any streams provided by said service providers that those streams have ended and any associated extended interfaces should be closed.
