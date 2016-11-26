from jioServer import jioServer
import cc as cc
import sys
if __name__ == "__main__":
	if len(sys.argv)>1:
		PORT3 = int(sys.argv[1])
	else:
		PORT3 = 65454
	connect_flag = False
	while not connect_flag:
		try:
			clc = jioServer(PORT3)
			clc.listen()
			connect_flag = True
		except:
			print 'PORT ',PORT3,' busy!! Enter new PORT'
			PORT3 = int(raw_input())
	clc.recv_msg_call_func(cc)