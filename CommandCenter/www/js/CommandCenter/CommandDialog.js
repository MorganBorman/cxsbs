//CommandCenter.CommandDialog
define([ "dojo/_base/declare",
         "dojo/_base/connect",
         "dijit/Dialog",
         "dojox/form/BusyButton" 
         ], 
function(declare, connect, Dialog, BusyButton) {
	return declare([ Dialog ], {
		constructor : function(attr) {
			var dialog_inputs = {};

			var dialog_div = document.createElement('div');
			var dialog_table = document.createElement('table');

			for (ix in attr.inputs) {
				var dialog_row = document.createElement('tr');

				var input = attr.inputs[ix];

				var label_cell = document.createElement('td');
				label_cell.innerHTML = input.label;
				dialog_row.appendChild(label_cell);

				var input_cell = document.createElement('td');

				var input_elem = document.createElement('input');
				input_elem.setAttribute('type', 'text');
				input_elem.setAttribute('size', input.size);
				input_elem.value = input.value;

				dialog_inputs[input.id] = input_elem;

				input_cell.appendChild(input_elem);

				dialog_row.appendChild(input_cell);

				dialog_table.appendChild(dialog_row);
			}

			var dialog_buttons = document.createElement('div');
			dialog_buttons.setAttribute('class', "dijitDialogPaneActionBar");
			for (bx in attr.buttons) {
				var button = attr.buttons[bx];

				var bb = BusyButton({
					label : button.normLabel,
					busyLabel : button.busyLabel
				});

				connect.connect(bb, "onClick", function() {
					var arguments = {};
					
					for (ax in dialog_inputs) {
						arguments[ax] = dialog_inputs[ax].value;
					}

					connect.publish('/CommandCenter/dialog/' + attr.dia_id + '/' + button.id, arguments);
				});

				var stopSpinning = function() {
					bb.resetTimeout();
				}

				for (fx in button.finishOn) {
					var finishOn = button.finishOn[fx];

					connect.subscribe(finishOn, stopSpinning);
				}

				bb.placeAt(dialog_buttons);
			}

			dialog_div.appendChild(dialog_table);
			dialog_div.appendChild(dialog_buttons);

			attr.content = dialog_div;

			declare.safeMixin(this, attr);
		}
	});
});