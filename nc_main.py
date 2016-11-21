from jioServer import jioServer
import nc as nc
import sys
if __name__ == "__main__": 
	PORT1 = 45675
	cc = jioServer(PORT1)
	cc.listen()
	cc.recv_msg_call_func(nc)
	exit(0)