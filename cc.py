#!/usr/bin/python           # This is client.py file
from jioClient import jioClient
import sys
import json
import time
import libvirt

conn = libvirt.open("qemu:///system")
pool = conn.storagePoolLookupByName('images')

nodes = []
i = 1
while True:
	print 'NC',i,' IP -'
	IP = raw_input()
	print 'NC',i,' PORT - '
	PORT  = int(raw_input())
	try:
		nc = jioClient(IP,PORT)
		nodes.append(nc)
	except Exception as e:
		print 'ERROR :: NC connection failed with Error ',e
	print 'Add more NC? (y/n)'
	response = raw_input()
	i += 1
	if response != 'y':
		break

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
	node_idx = 1
	for node in nodes:
		ret_msg = node.call_func('get_stats')
		node_stats = json.loads(ret_msg)
		#node_stats['mem']
		#node_stats['vcpu']
		node_stats['node']  = node_idx
		stats_list.append(node_stats)
		node_idx += 1
	return stats_list

def greedy(memory,cores,disk):
	print 'Greedy Scheduling'
	ret_msg = {}
	done_flag = False
	error = 'Unavailable resources'
	i = 1
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
				ret_msg['Node'] = i
				break
			else:
				error = 'Internal issue'
		i += 1
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
	done_flag = False
	node_stats_list = get_all_nodes_stats()
	node_stats_list = sorted(node_stats_list, key = lambda x: (x['mem'],x['vcpu']))
	node_stats = node_stats_list[-1]
	avail_mem = node_stats['mem']
	avail_cores = node_stats['vcpu']
	avail_disk = node_stats['disk']
	error = 'Resources unavailable'
	if avail_mem>memory and avail_cores>cores and avail_disk>disk:
		node = nodes[node_stats['node']-1]
		print('LOG :: Creating VM at ',node)
		VM_Name = 'CB'+str(int(time.time()))
		status = node.call_func('create',VM_Name,memory,cores,disk)
		print 'LOG :: Status - ',status
		if status=='True':
			done_flag = True
			ret_msg['VM_Name'] = VM_Name
			ret_msg['Node'] = node_stats['node']
		else:
			error = 'Internal issue'
	ret_msg['Success'] = done_flag
	if not done_flag:
		ret_msg['Error'] = error
	print ret_msg
	return json.dumps(ret_msg)

def deleteVM(name,node):
	nc = nodes[node-1]
	return nc.call_func('delete',name)

def first_fit_bin_packing():
	i = 0
	res = 0
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
					res += 1 
			print domains
		i += 1
	return str(res)+' domains migrated.'

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

def createStoragePoolVolume(name, disk_size):
    stpVolXml = """
    <volume>
        <name>"""+name+""".qcow2</name>
        <allocation>0</allocation>
        <capacity unit="G">"""+str(disk_size)+"""</capacity>
        <target>
            <format type='qcow2'/>
            <path>/var/lib/libvirt/images/"""+name+""".qcow2</path>
            <permissions>
                <owner>107</owner>
                <group>107</group>
                <mode>0744</mode>
                <label>virt_image_t</label>
            </permissions>
        </target>
    </volume>
    """
    stpVol = pool.createXML(stpVolXml, 0)
    return stpVol

def createVol(node,domain_name,disk_name,disk_size,vol_name):
	stpVol = createStoragePoolVolume(disk_name,disk_size)
	nc = nodes[node-1]
	return nc.call_func('addVol',domain_name,disk_name,vol_name)

def createVol2(node,domain_name,disk_name,vol_name):
	nc = nodes[node-1]
	return nc.call_func('addVol',domain_name,disk_name,vol_name)

def detachVol(node,domain_name,vol_name):
	nc = nodes[node-1]
	return nc.call_func('delVol',domain_name,vol_name)

def start_auto_scale():
	for node in nodes:
		node.call_func('autoscale')
	return 'Success'

def exit():
	for node in nodes:
		node.close()