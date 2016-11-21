#!/usr/bin/python           # This is client.py file
from jioClient import jioClient
import sys
import json
import time

PORT1 = 45675
PORT2 = 34534

nc1 = jioClient('M-1908',PORT1)
nc2 = jioClient('172.50.88.12',PORT2)

nodes = [nc1,nc2]

RRpos = 0	#Round Robin position

def connect_node_controller():
	for node in nodes:
		node.connect()
		print'LOG :: Connected node controller : ',node

connect_node_controller()
def get_all_nodes_stats():
	for node in nodes:
		ret_msg = node.call_func('get_stats')
		node_stats = json.loads(ret_msg)
		node_stats['mem']
		node_stats['vcpu']

def round_robin(memory,cores):
	print 'Round Robin Scheduling'
	global RRpos
	print 'LOG :: RR position - ',RRpos
	done_flag = False
	no_of_try = 0
	print 'Loop condition -',(not done_flag) and (no_of_try<len(nodes))
	ret_msg = 'NCs out of resources'
	while (not done_flag) and (no_of_try<=len(nodes)):
		if RRpos>=len(nodes):
			RRpos = 0
		resources = nodes[RRpos].call_func('get_stats')
		print 'LOG :: ret_msg',resources
		node_stats = json.loads(resources)
		avail_mem = node_stats['mem']
		avail_cores = node_stats['vcpu']
		print 'STATUS :: Available memory - ',avail_mem,'  Available cores - ',avail_cores
		if avail_mem>memory and avail_cores>cores:
			print('LOG :: Creating VM at NC',RRpos+1)
			VM_Name = 'CB'+str(int(time.time()))
			status = nodes[RRpos].call_func('create',VM_Name,memory,cores)
			print 'LOG :: Status - ',status
			if status=='True':
				done_flag = True
				ret_msg = 'VM created at NC'+str(RRpos+1)
			else:
				ret_msg = 'ERROR :: Error creating VM at NC'+str(RRpos+1)
		RRpos = RRpos+1
		no_of_try = no_of_try+1
	return ret_msg


def exit():
	for node in nodes:
		node.close()