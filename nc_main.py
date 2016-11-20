from jioServer import jioServer
import sys
if __name__ == "__main__": 
	port = int(sys.argv[1])		 # Reserve a port for your service.
	cc = jioServer(port)
	cc.listen()
	cc.recv_msg()
	exit(0)