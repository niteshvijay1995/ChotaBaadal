import socket
import json
class jioServer:
	'Server Class for communication and calling function'
	def __init__(self,port):
		self.port = port
		self.host = '172.50.88.13'
		self.s = socket.socket()
		self.s.bind((self.host, self.port)) 
	def listen(self):
		self.s.listen(5)
		print("JIOSERVER :: Listening...")
		self.c, self.addr = self.s.accept()
		print ("JIOSERVER :: Connected with Client on ",self.addr)
		
	def recv_msg_call_func(self,func_file):
		while True:
			print("JIOSERVER :: Receiving message...")
			msg = self.c.recv(1024)
			print("LOG ::  Message received : ",msg)
			if msg=='exit' or msg=='':
				break;
			json_msg = json.loads(msg)
			func_name = json_msg['func_name']
			args = json_msg['args']
			try:
				ret_msg = getattr(func_file,func_name)(*args)
			except Exception as e:
				ret_msg = 'Error :: '+str(e)
			self.c.send(ret_msg)
		self.c.close()








	
