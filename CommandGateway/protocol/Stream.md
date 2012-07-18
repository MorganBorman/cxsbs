#Overview

This portion of this protocol document will detail the stream message format.

This is how service providers push data to connected and subscribed websocket clients.

Clients are automatically subscribed to two streams when they connect to a server. Which keep the clients up to date on what the service provider is providing.
* streams
* interfaces

#Subtypes

* Start (0)
* Update (1)

#General format

* {type: 3, subtype: 0, ["streams"]}
* {type: 3, subtype: 1, ["streams", {0: "streams", 1: "interfaces", 2: "clients.public", 3: "chat", 4: "match time", 5: "clients.private"}]}

* {type: 3, subtype: 0, ["interfaces"]}
* {type: 3, subtype: 1, ["interfaces", {0: "status", 2: "control", 1: "scoreboard"}]}

* {type: 3, subtype: 0, ["clients.public"]}
* {type: 3, subtype: 1, ["clients.public", {0: {name: "[FD]Chasm", team: "good", frags: 32, deaths: 18, accuracy: 0.37}}]}
* {type: 3, subtype: 1, ["clients.public", {0: {}}]}

* {type: 3, subtype: 0, ["clients.private"]}
* {type: 3, subtype: 1, ["clients.private", {0: {ip: "74.133.166.34", email: "fd.chasm@gmail.com", groups: ["__user__", "__normal__", "__all__"]}}]}
* {type: 3, subtype: 1, ["clients.private", {0: {}}]}
