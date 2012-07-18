require([
         	 "dojo/_base/json",
	         "dojo/query",
	         "dojo/data/ItemFileWriteStore",
	         "dojo/_base/connect",
	         "dijit/Tree",
	         "dijit/tree/ForestStoreModel",
	         "dijit/Dialog",
	         "CommandCenter/CommandDialog",
	         //unmapped stuff
	         "dijit/layout/BorderContainer",
	         "dijit/layout/TabContainer",
	         "dijit/layout/ContentPane",
	         "dojo/parser",
	         "dojo/domReady!"
         ], 
function(dojo, query, ItemFileWriteStore, connect, Tree, ForestStoreModel, Dialog, CommandDialog, BorderContainer, TabContainer, ContentPane, parser)
{
	//connect.subscribe("foobar", function(message){});
	//connect.publish("foobar", [{item:"one", another:"item", anObject:{ deeper:"data" }}]);
	//connect.connectPublisher("foobar", myObject, "myEvent");
	
	function create_connection(host, port)
	{
		var ws = new WebSocket("ws://" + host + ":" + port + "/");
		ws.onopen = function(){connect.publish("/CommandCenter/socket/open", []);};
		ws.onmessage = function(e){connect.publish("/CommandCenter/socket/message", [e.data]);};
		ws.onclose = function(){connect.publish("/CommandCenter/socket/close", []);};
		ws.onerror = function(e){connect.publish("/CommandCenter/socket/error", [e]);};
		
		var send_subscription = connect.subscribe("/CommandCenter/socket/send", function(message)
		{
			ws.send(message);
		});
		
		var shutdown_subscription = connect.subscribe("/CommandCenter/socket/shutdown", function(message)
		{
			ws.close();
			connect.unsubscribe(send_subscription);
			connect.unsubscribe(shutdown_subscription);
		});
	}
	
	connect.subscribe("/CommandCenter/status", function(message, sprite)
	{
		if(!sprite){ var sprite = "status";}
		
		var status_container = document.getElementById('status-bar');
		
		status_container.innerHTML = "<table class='status-item'><tr><td><div class='memu-icon sprite-" + sprite + "'></div></td><td>" + message + "</td></tr></table>";
	});
	
	connect.subscribe("/CommandCenter/menu/connect", function()
	{
		connect_dialog.show();
	});
	
	connect.subscribe("/CommandCenter/menu/disconnect", function()
	{
		connect.publish("/CommandCenter/socket/shutdown");
	});
	
	connect.subscribe("/CommandCenter/menu/authenticate", function()
	{
		authenticate_dialog.show();
	});
	
	connect.subscribe("/CommandCenter/socket/open", function()
	{
		connect.publish("/CommandCenter/status", ["Connected to server."]);
	});
	
	connect.subscribe("/CommandCenter/socket/close", function()
	{
		connect.publish("/CommandCenter/status", ["Disconnected from server."]);
	});
	
	connect.subscribe("/CommandCenter/socket/error", function()
	{
		connect.publish("/CommandCenter/status", ["Error with server connection."]);
	});
	
	connect.subscribe("/CommandCenter/socket/message", function(message)
	{
		console.log("Received message from server: " + message);
		
		var message_object = dojo.fromJson(message);
		
		if (message_object.type == 2 && message_object.subtype == 0)
		{
			var answer = Module.answerchallenge(pending_key, message_object.challenge);
			
			var request = {type: 2, subtype: 1, gid: message_object.gid, answer: answer};
			connect.publish("/CommandCenter/socket/send", [dojo.toJson(request)]);
		}
		
		if (message_object.type == 4 && message_object.subtype == 0)
		{
			initialize_servers(message_object.servers);
		}
	});
    
    var connect_dialog = CommandDialog(
    	    {
    	    	dia_id: 'connect',
    	    	title: 'Connect',
    	    	inputs: [
    		    	         {
    		    	        	 id: 'host',
    		    	        	 label: 'Host',
    		    	        	 size: 24,
    		    	        	 value: 'localhost'
    		    	         },
    		    	         {
    		    	        	 id: 'port',
    		    	        	 label: 'Port',
    		    	        	 size: 24,
    		    	        	 value: '9999'
    		    	         },
    	    	         ],
    	    	buttons: [
    		    	          {
    		    	          	id: 'connect',
    		    	          	normLabel: 'Connect',
    		    	          	busyLabel: 'Connecting...',
    		    	          	finishOn: ['/CommandCenter/socket/open', '/CommandCenter/socket/close', '/CommandCenter/socket/error']
    		    	          }
    	    	          ]
    	    }
    );
	
	connect.subscribe("/CommandCenter/dialog/connect/connect", function(args)
	{
		create_connection(args.host, args.port);
		connect_dialog.hide();
	});
	
	var pending_key = "";
	
    var authenticate_dialog = CommandDialog(
    	    {
    	    	dia_id: 'authenticate',
    	    	title: 'Authenticate',
    	    	inputs: [
    		    	         {
    		    	        	 id: 'domain',
    		    	        	 label: 'Domain',
    		    	        	 size: 32,
    		    	        	 value: ''
    		    	         },
    		    	         {
    		    	        	 id: 'name',
    		    	        	 label: 'Name',
    		    	        	 size: 16,
    		    	        	 value: ''
    		    	         },
    		    	         {
    		    	        	 id: 'key',
    		    	        	 label: 'Key',
    		    	        	 size: 50,
    		    	        	 value: ''
    		    	         }
    	    	         ],
    	    	buttons: [
    		    	          {
    		    	          	id: 'authenticate',
    		    	          	normLabel: 'Authenticate',
    		    	          	busyLabel: 'Authenticating...',
    		    	          	finishOn: ['/CommandCenter/socket/message']
    		    	          }
    	    	          ]
    	    }
    );
	
	connect.subscribe("/CommandCenter/dialog/authenticate/authenticate", function(args)
	{
		pending_key = args.key;
		var request = {type: 2, subtype: 0, domain: args.domain, name: args.name};
		connect.publish("/CommandCenter/socket/send", [dojo.toJson(request)]);
		authenticate_dialog.hide();
	});
	
	var next_id = 0;
	
	function clear_servers()
	{
        var allData = treeStore._arrayOfAllItems;
        for (i=0;i<allData.length;i++) {
            if (allData[i] != null) {
            	treeStore.deleteItem(allData[i]);
            }
        }
        
        next_id = 0;
	}
	
	function initialize_servers(server_list)
	{
		clear_servers();
		
		for(ix in server_list)
		{
			initialize_server(server_list[ix]);
		}
	}
	
	function initialize_server(server_def)
	{
		var item = {id: next_id, name: server_def.name, root: true, children: []};
		
		next_id++;
		
		treeStore.newItem(item);
	}

	var treeStore = new ItemFileWriteStore(
		{
			data : {
				name : "foobar",
				label : 'name',
				items : []
			}
		});
	
    var treeModel = new ForestStoreModel({
        store: treeStore,
        query: { 'root': true }
     });
    
    var navTree = new Tree({model: treeModel, showRoot: true }, "navTree")
    
    navTree.onClick = function(item){
        /* Get the expression from the clicked item and make sure it is a string, then evaluate it. */
    	var expr = ''+item.callback;
        eval(expr);
    };
	
	//connect the menu entries into the event system
	query(".menuaction").on("click", function(evt){connect.publish("/CommandCenter/menu/" + this.id, []);});
	
	//remove the loading spinner
	dojo.style("preloader", "display", "none");
});