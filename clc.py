from jioClient import jioClient
PORT3 = 65454
cc1 = jioClient('M-1908',PORT3)
cc1.connect()
#print cc1.call_func('round_robin',3000000,2,20)	#memory,cores,disk
print cc1.call_func('round_robin',3000000,2,30)
cc1.close()