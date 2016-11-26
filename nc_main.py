from jioServer import jioServer
import nc as nc
import sys
if __name__ == "__main__": 
	if len(sys.argv)>1:
		PORT1 = int(sys.argv[1])
	else:
		PORT1 = 45671
	connect_flag = False
	while not connect_flag:
		try:
			cc = jioServer(PORT1)
			cc.listen()
			connect_flag = True
		except:
			print 'PORT',PORT1,' busy!! Enter new PORT'
			PORT1 = int(raw_input())
	cc.recv_msg_call_func(nc)
	exit(0)