#!/usr/bin/python           # This is client.py file

import socket               # Import socket module
import sys
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = int(sys.argv[1])                # Reserve a port for your service.

s.connect((host, port))
s.sendall('centos11 chalu karo and info bhejo')
print s.recv(1024)
#print info
s.close                     # Close the socket when done