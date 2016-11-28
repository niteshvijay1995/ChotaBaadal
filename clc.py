from jioClient import jioClient
import json
import os.path
import thread
import time

clouds = []
i = 1
while True:
	print 'CC',i,' IP -'
	IP = raw_input()
	print 'CC',i,' PORT - '
	PORT  = int(raw_input())
	try:
		cc = jioClient(IP,PORT)
		clouds.append(cc)
	except Exception as e:
		print 'ERROR :: CC connection failed with Error ',e
	print 'Add more CC? (y/n)'
	response = raw_input()
	i += 1
	if response != 'y':
		break

for cloud in clouds:
	cloud.connect()
VMs = {}	#Dictionary of VMs created (Key-VM_Name)
#print cc1.call_func('round_robin',3000000,2,20)	#memory,cores,disk

def first_fit_bin_packing():
	print 'First fit bin packing' 
	while True:
		for cloud in clouds:
			status = cloud.call_func('first_fit_bin_packing')
			print status
		time.sleep(120)


algo = 'round_robin'
#algo = 'greedy'
#algo = 'match_making'

if os.path.isfile('log.txt'):
	s = open('log.txt', 'r').read()
	VMs = eval(s)
try:
	while True:
		print '==============CB================'
		print 'Hello, Welcome to Chota Baadal.'
		print 'Press n to create new VM'
		print 'Press d to delete a VM'
		print 'Press s to start first_fit_bin_packing'
		print 'Press g to start script'
		print 'Press c to change algo'
		print 'Press q to quit'
		print '================================'
		inp = str(raw_input())
		if inp == 'c':
			print 'Algo name'
			algo = raw_input()
		if inp == 'g':
			print 'Enter filename'
			file_name = raw_input()
			file = open(file_name, 'r')
			for line in file:
				values = line.split()
				zone = int(values[0])
				cloud = clouds[zone-1]
				mem = int(values[1])*1024
				cores = int(values[2])
				disk = int(values[3])
				VM_info = cloud.call_func(algo,mem,cores,disk)
				print VM_info
				VM_info = json.loads(VM_info)
				if VM_info['Success']:
					print '\n--------------------------------'
					print 'VM created successfully'
					print 'VM Name : ',VM_info['VM_Name']
					print 'Zone : ',zone
					print 'Node : ',VM_info['Node']
					print '----------------------------------\n'
					VMs[VM_info['VM_Name']] = {'cc':zone-1,'nc':VM_info['Node']}
				else:
					print 'Sorry, unable to create new VM due to ',VM_info['Error']

		if inp == 'n':
			print 'Please select the zone (1/2)'
			zone = int(raw_input())
			cloud = clouds[zone-1]
			print 'Memory requirement in MB : '
			mem = int(raw_input())*1024
			print 'Cores requirement : '
			cores = int(raw_input())
			print 'Disk requirement in GB : '
			disk = int(raw_input())
			VM_info = cloud.call_func(algo,mem,cores,disk)
			print VM_info
			VM_info = json.loads(VM_info)
			if VM_info['Success']:
				print '\n--------------------------------'
				print 'VM created successfully'
				print 'VM Name : ',VM_info['VM_Name']
				print 'Zone : ',zone
				print 'Node : ',VM_info['Node']
				print '----------------------------------\n'
				VMs[VM_info['VM_Name']] = {'cc':zone-1,'nc':VM_info['Node']}
			else:
				print 'Sorry, unable to create new VM due to ',VM_info['Error']
		if inp == 'd':
			print 'Select the VM which you want to delete'
			VM_list = []
			cloud_idx = 0
			i = 1
			for cloud in clouds:
				domain_list = cloud.call_func('getVM')
				domain_list = json.loads(domain_list)['VMs']
				node_idx = 1 
				for node in domain_list:
					for domain_name in node:
						print i,'. ',domain_name
						VM_list.append([domain_name,node_idx,cloud_idx])
						i += 1
					node_idx += 1
			if len(VM_list)==0:
				print 'No VM created!'
				continue
			print '0 to Cancel'
			n = int(raw_input())
			if n==0:
				continue
			domain_name_to_delete = VM_list[n-1][0]
			node_to_call = VM_list[n-1][1]
			cloud = clouds[VM_list[n-1][2]]
			status = cloud.call_func('deleteVM',domain_name_to_delete,node_to_call)
			print status,' ',VM_list[n-1]
			if status == 'Deleted':
				'VM deleted successfully'
		if inp == 's':
			try:
				thread.start_new_thread(first_fit_bin_packing,())
			except Exception as e:
				print 'Error in starting thread - ',e
		if inp == 'q':
			break;

	for cloud in clouds:
		cloud.close()
except Exception as e:
	print e
finally:
    target = open('log.txt','wb')
    target.write(str(VMs))
    #print VMs

