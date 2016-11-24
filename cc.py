#!/usr/bin/python           # This is client.py file
from jioClient import jioClient
import sys
import json
import time


PORT1 = 45677
PORT2 = 47777

nc1 = jioClient('172.50.88.13',PORT1)
nc2 = jioClient('172.50.88.12',PORT2)

nodes = [nc1,nc2]

RRpos = 0	#Round Robin position

def connect_node_controller():
	for node in nodes:
		try:
			node.connect()
			print'LOG :: Connected node controller : ',node
		except Exception as e:
			print 'ERROR :: ',e


connect_node_controller()

def get_all_nodes_stats():
	stats_list = []
	for node in nodes:
		ret_msg = node.call_func('get_stats')
		node_stats = json.loads(ret_msg)
		#node_stats['mem']
		#node_stats['vcpu']
		node_stats['node']  = node
		stats_list.append(node_stats)
	return stats_list

def greedy(memory,cores,disk):
	print 'Greedy Scheduling'
	ret_msg = {}
	done_flag = False
	error = 'Unavailable resources'
	for node in nodes:
		resources = node.call_func('get_stats')
		#print 'LOG :: ret_msg',resources
		node_stats = json.loads(resources)
		avail_mem = node_stats['mem']
		avail_cores = node_stats['vcpu']
		avail_disk = node_stats['disk']
		print 'STATUS :: Available memory - ',avail_mem,'  Available cores - ',avail_cores,' Available disk - ',avail_disk
		if avail_mem>memory and avail_cores>cores and avail_disk>disk:
			print('LOG :: Creating VM at ',node)
			VM_Name = 'CB'+str(int(time.time()))
			status = node.call_func('create',VM_Name,memory,cores,disk)
			print 'LOG :: Status - ',status
			if status=='True':
				done_flag = True
				ret_msg['VM_Name'] = VM_Name
				ret_msg['Node'] = RRpos+1
				break
			else:
				error = 'Internal issue'
	ret_msg['Success'] = done_flag
	if not done_flag:
		ret_msg['Error'] = error
	return json.dumps(ret_msg)

def round_robin(memory,cores,disk):
	print 'Round Robin Scheduling'
	global RRpos
	print 'LOG :: RR position - ',RRpos
	done_flag = False
	no_of_try = 0
	print 'Loop condition -',(not done_flag) and (no_of_try<len(nodes))
	ret_msg = {}
	error = 'Resources unavailable'
	while (not done_flag) and (no_of_try<=len(nodes)):
		if RRpos>=len(nodes):
			RRpos = 0
		resources = nodes[RRpos].call_func('get_stats')
		#print 'LOG :: Available Resources before starting VM',resources
		node_stats = json.loads(resources)
		avail_mem = node_stats['mem']
		avail_cores = node_stats['vcpu']
		avail_disk = node_stats['disk']
		print 'STATUS :: Available memory - ',avail_mem,'  Available cores - ',avail_cores,' Available disk - ',avail_disk
		if avail_mem>memory and avail_cores>cores and avail_disk>disk:
			print('LOG :: Creating VM at NC',RRpos+1)
			VM_Name = 'CB'+str(int(time.time()))
			status = nodes[RRpos].call_func('create',VM_Name,memory,cores,disk)
			print 'LOG :: Status - ',status
			if status=='True':
				done_flag = True
				ret_msg['VM_Name'] = VM_Name
				ret_msg['Node'] = RRpos+1
			else:
				error = 'Internal issue'
		RRpos = RRpos+1
		no_of_try = no_of_try+1
	ret_msg['Success'] = done_flag
	if not done_flag:
		ret_msg['Error'] = error
	return json.dumps(ret_msg)

def match_making(memory,cores,disk):
	ret_msg = {}
	done_flag = Flase
	node_stats_list = get_all_nodes_stats()
	sorted(node_stats_list, key = lambda x: (x['mem'],x['vcpu']))
	nodes_stats = node_stats_list[0]
	avail_mem = node_stats['mem']
	avail_cores = node_stats['vcpu']
	avail_disk = node_stats['disk']
	if avail_mem>memory and avail_cores>cores and avail_disk>disk:
		node = node_stats['node']
		print('LOG :: Creating VM at ',node)
		VM_Name = 'CB'+str(int(time.time()))
		status = node.call_func('create',VM_Name,memory,cores,disk)
		print 'LOG :: Status - ',status
		if status=='True':
			done_flag = True
			ret_msg['VM_Name'] = VM_Name
			ret_msg['Node'] = RRpos+1
			break
		else:
			error = 'Internal issue'
	ret_msg['Success'] = done_flag
	if not done_flag:
		ret_msg['Error'] = error
	return json.dumps(ret_msg)

def deleteVM(name,node):
	nc = nodes[node-1]
	return nc.call_func('delete',name)

def first_fit_bin_packing():
	i = 0
	for pri_node in nodes:
		for j in range(i+1,len(nodes)):
			node = nodes[j]
			domains = node.call_func('getAllVM')
			domains = json.loads(domains)
			for domain_name in domains:
				resources = pri_node.call_func('get_stats')
				pri_node_stat = json.loads(resources)
				domain = domains[domain_name]
				if domain['mem']<pri_node_stat['mem'] and domain['vcpu']<pri_node_stat['vcpu']:
					print 'Migrating domain ',domain_name
					node.call_func('migrate',domain_name,pri_node.getHost())
					print 'Domain Migrated Successfully' 
			print domains
		i += 1
	return 'hello'

def getVM():
	VMs = []
	for node in nodes:
		domains = node.call_func('getAllVM')
		domains = json.loads(domains)
		domain_list = []
		for domain_name in domains:
			domain_list.append(domain_name)
		VMs.append(domain_list)
	print VMs
	ret_msg = {}
	ret_msg['VMs'] = VMs
	return json.dumps(ret_msg)
def exit():
	for node in nodes:
		node.close()