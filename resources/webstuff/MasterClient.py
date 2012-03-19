import socket, select, threading, time, os

class MasterClient(threading.Thread):
	def __init__(self, master_name, master_host, master_port, server_port, update_interval):
		
		threading.Thread.__init__(self)
		
		self.master_name = master_name
		self.master_host = master_host
		self.master_port = master_port
		self.server_port = server_port
		self.interval = update_interval
		
		self.response_handlers =	{
										'succreg':		self.handle_registration_success,
										'failreg':		self.handle_registration_failure,
										'succauth':		self.handle_authentication_success,
										'failauth':		self.handle_authentication_failure,
										'chalauth':		self.handle_authentication_challenge,
										'cleargbans':	self.handle_global_ban_clear,
										'addgban':		self.handle_global_ban_add
									}
		
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((master_host, master_port))
		
		self.local_read, self.local_write = os.pipe()
		
		self.local_data_stream = ""
		self.remote_data_stream = ""
		
		self.running = True
		self.next_update = time.time()
	
	def run(self):
		while self.running:
			if time.time() >= self.next_update:
				self.socket.sendall("regserv %s\n" %self.server_port)
				self.next_update = time.time() + self.interval
			
			wait_time = self.next_update - time.time()
			rfds, wfds, efds = select.select([self.socket, self.local_read], [], [], wait_time)
			
			for rfd in rfds:
				if rfd == self.socket:
					self.handle_remote()
				elif rfd == self.local_read:
					self.handle_local()
			
	def handle_local(self):
		"Pass input on to the socket except when the pipe gets closed."
		data = os.read(self.local_read, 1024)
		if len(data) <= 0:
			print "Read end of stream from local side."
			self.stop_client()
		else:
			self.local_data_stream += data
	
		next_nl_pos = self.local_data_stream.find("\n")
		while next_nl_pos != -1:
			datum, self.local_data_stream = self.local_data_stream.split('\n', 1)
			datum += "\n"
			self.socket.sendall(datum)
			next_nl_pos = self.local_data_stream.find("\n")
	
	def handle_remote(self):
		data = self.socket.recv(1024)
		if len(data) <= 0:
			print "Read end of stream from remote side."
			self.stop_client()
		else:
			self.remote_data_stream += data
		
		next_nl_pos = self.remote_data_stream.find("\n")
		while next_nl_pos != -1:
			datum, self.remote_data_stream = self.remote_data_stream.split('\n', 1)
			self.handle_local_datum(datum)
			next_nl_pos = self.remote_data_stream.find("\n")
		
	def handle_local_datum(self, datum):
		args = datum.split()
		if args[0] in self.response_handlers.keys():
			self.response_handlers[args[0]](args)
		else:
			print "Received unknown masterserver command (%s)." % args[0]
			
	def stop_client(self):
		self.running = False
		self.socket.close()
		os.close(self.local_read)
		os.close(self.local_write)
	
	def handle_registration_success(self, args):
		print "Sucessfully Registered with masterserver."
		
	def handle_registration_failure(self, args):
		print "Failed to Register with masterserver."
		
	def handle_authentication_challenge(self, args):
		auth_id = int(args[1])
		auth_chal = args[2]
		print "Got auth challenge (%s)" % str(args)
		
	def handle_authentication_success(self, args):
		auth_id = int(args[1])
		print "Got auth success (%s)" % str(args)
		
	def handle_authentication_failure(self, args):
		auth_id = int(args[1])
		print "Got auth failure (%s)" % str(args)
	
	def handle_global_ban_clear(self, args):
		print "Got gbanclear (%s)" % str(args)
	
	def handle_global_ban_add(self, args):
		ip_string = args[1]
		print "Got gbanadd (%s)" % str(args)
		
	def authentication_request(self, id, name):
		os.write(self.local_write, "reqauth %i %s\n" %(id, name) )
		
	def authentication_response(self, id, response):
		os.write(self.local_write, "confauth %i %s\n" %(id, response) )