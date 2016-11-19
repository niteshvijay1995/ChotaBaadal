#!/usr/bin/python           # This is client.py file

import socket               # Import socket module
import sys

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = int(sys.argv[1])                # Reserve a port for your service.
s.connect((host, port))

with open(sys.argv[2]) as f:
	for line in f:
		print line
		line = line.strip()
		s.sendall(line)
		if line[0] == 'i':
			print(s.recv(1024))

s.close                     # Close the socket when done