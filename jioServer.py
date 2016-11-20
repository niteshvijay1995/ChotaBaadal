import socket
import nc
class jioServer:
	'Server Class for communication between NC and CC'
	def __init__(self,port):
		self.port = port
		self.host = socket.gethostname()
		self.s = socket.socket()
		self.s.bind((self.host, self.port)) 
	def listen(self):
		self.s.listen(5)
		print("Listening...")
		self.c, self.addr = self.s.accept()
		print ("Connected with Client on ",self.addr)
		
	def recv_msg(self):
		while True:
			print("Receiving message...")
			self.func = self.c.recv(1024).split(' ')
			if self.func[0]=='exit':
				break
			print("Message received - ",self.func)
			try:
				if len(self.func)>1:
					ret_msg = getattr(nc,self.func[0])(self.func[1])
				else:
					ret_msg = getattr(nc,self.func[0])()
			except:
				ret_msg = 'Error'
			self.c.send(ret_msg)
		self.c.close()






	
