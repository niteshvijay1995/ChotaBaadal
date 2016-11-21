from jioServer import jioServer
import nc as nc
import sys
if __name__ == "__main__": 
	port = int(sys.argv[1])		 # Reserve a port for your service.
	cc = jioServer(port)
	cc.listen()
	cc.recv_msg_call_func(nc)
	exit(0)