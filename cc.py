#!/usr/bin/python           # This is client.py file
from jioClient import jioClient
import sys

port = int(sys.argv[1])
nc1 = jioClient('M-1908',port)
nc1.connect()
print(nc1.call_func('get_stats'))
print(nc1.call_func('create','6'))
nc1.close()