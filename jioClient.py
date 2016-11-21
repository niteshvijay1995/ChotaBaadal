import socket
import json
class jioClient:
	'Class for communication'
	def __init__(self,host,port):
		self.port = port
		self.host = host
		self.s = socket.socket()

	def connect(self):
		self.s.connect((self.host, self.port))
		print('Connected to NC')

	def call_func(self,func_name,*args):
		json_msg = {}
		json_msg['func_name'] = func_name
		args_list = []
		for arg in args:
			args_list.append(arg) 
		json_msg['args'] = args_list
		print 'LOG :: Calling function ',json_msg
		self.s.sendall(json.dumps(json_msg))
		rec_msg = self.s.recv(1024)
		return rec_msg

	def close(self):
		print 'LOG :: Closing',self
		self.s.sendall('exit')
		self.s.close

	def __repr__(self):
		return self.host
	
