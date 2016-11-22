from jioServer import jioServer
import cc as cc
import sys
if __name__ == "__main__":
	if len(len(sys.argv))>1:
		PORT3 = int(sys.argv[1])
	else:
		PORT3 = 65454
	clc = jioServer(PORT3)
	clc.listen()
	clc.recv_msg_call_func(cc)
	cc.exit()