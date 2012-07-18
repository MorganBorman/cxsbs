#Overview

This design document will cover the basic structure and function of the CommandCenter then proceed into details.

The structure of the CommandCenter is this;
* A menu bar which contains controls for connecting/disconnecting with gateways and accessing help information. Henceforth refered to as *the menu bar*.
* A tree view on the left which shows an list of service providers and the interfaces which they support. Henceforth refered to as *the nav tree*.
* A tabbed central area in which various interfaces are displayed throughout the operation of the CommandCenter. Henceforth refered to as *the content area*.
* A status bar at the bottom which periodically displays status messages. Henceforth referred to as *the status bar*.

The key to the programmatic structure of the CommandCenter is the idea of user interfaces being atomic units. User interfaces populate the content area with data display and control elements
when a service provider's advertised interfaces is activated. Different users may see different lists of available user interfaces in the nav tree based on their credentials.

Users with limited or no credentials will probably be presented with extremely basic interfaces which primarily just display data from specific data streams, while users with
higher credentials will get versions of the interfaces with controls and more data.

#Structure

* Main view
* Interface template registry
* Data reservoir
* Controller
* Socket manager

##Main view

This encompasses the structure of the overall interface plus an api for managing currently open interfaces and updating available resource providers and their interfaces.

##Interface template registry

This maintains a list of the supported interfaces and provides an api for obtaining these interfaces when a user attempts to access a specific resource providers user interface.

##Data reservoir

This provides a simple api for storing a collection of models representing the data that is received over streams and connecting views to said models.

##Controller

This handles incoming messages from the socket manager and does one of the following;
* updates the overall interface
* passes them to the correct interface
* passes streams to the Data reservoir

##Socket manager

This wraps the actual websocket and provides simple controls and dojo signals to allow easy interfacing.
