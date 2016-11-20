import socket
class jioClient:
	'Class for communication between NC and CC'
	def __init__(self,host,port):
		self.port = port
		self.host = host
		self.s = socket.socket()
	def connect(self):
		self.s.connect((self.host, self.port))
		print('Connected to NC')
	def call_func(self,func_name,args=''):
		if args=='':
			self.s.sendall(func_name)
		else:
			self.s.sendall(func_name+' '+args)
		rec_msg = self.s.recv(1024)
		return rec_msg
	def close(self):
		self.s.sendall('exit')
		self.s.close
	
