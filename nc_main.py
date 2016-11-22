from jioServer import jioServer
import nc as nc
import sys
if __name__ == "__main__": 
	if len(sys.argv)>1:
		PORT1 = int(sys.argv[1])
	else:
		PORT1 = 45674
	cc = jioServer(PORT1)
	cc.listen()
	cc.recv_msg_call_func(nc)
	exit(0)