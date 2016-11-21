#!/usr/bin/python           # This is client.py file
from jioClient import jioClient
import sys
import json
import time

PORT1 = 45674
PORT2 = 34533
PORT3 = 65453

nc1 = jioClient('M-1908',PORT1)
nc2 = jioClient('M-1907',PORT2)

nodes = [nc1,nc2]

clc = jioServer(PORT3)
clc.listen()

RRpos = 0	#Round Robin position

def connect_node_controller():
	for node in nodes:
		node.connect()
		print('LOG :: Connected node controller : ',node)


def get_all_nodes_stats():
	for node in nodes:
		ret_msg = node.call_func('get_stats')
		node_stats = json.loads(ret_msg)
		node_stats['mem']
		node_stats['vcpu']

def round_robin(memory,cores):
	connect_node_controller()
	done_flag = False
	no_of_try = 0
	while not done_flag and no_of_try<=len(nodes):
		if RRpos>len(nodes):
			RRpos = 0
		ret_msg = nodes[RRpos].call_func('get_stats')
		node_stats = json.loads(ret_msg)
		avail_mem = node_stats['mem']
		avail_cores = node_stats['vcpu']
		if avail_mem>memory and avail_cores>cores:
			print('LOG :: Creating VM at NC',RRpos+1)
			VM_Name = 'CB'+str(int(time.time()))
			status = nodes[RRpos].call_func('create',VM_Name,memory,cores)
			if status=='True':
				done_flag = True
				print('LOG :: VM created at NC',RRpos+1)
			else:
				print('LOG :: Error Creating VM at NC',RRpos+1)
		RRpos = RRpos+1
		no_of_try = no_of_try+1
nc1.close()