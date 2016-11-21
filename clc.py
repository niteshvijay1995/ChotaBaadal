from jioClient import jioClient
PORT3 = 65454
cc1 = jioClient('M-1908',PORT3)
clouds = [cc1]
for cloud in clouds:
	cloud.connect()
VMs = {}	#Dictionary of VMs created (Key-VM_Name)
#print cc1.call_func('round_robin',3000000,2,20)	#memory,cores,disk

while True:
	print '==============CB================'
	print 'Hello, Welcome to Chota Baadal.'
	print 'Press n to create new VM'
	print 'Press d to delete a VM'
	print 'Press q to quit'
	print '================================'
	inp = str(raw_input())
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
		VM_info = cc1.call_func('round_robin',mem,cores,disk)
		VM_info = json.loads(VM_info)
		if VM_info['Success']:
			print '\n--------------------------------'
			print 'VM created successfully'
			print 'VM Name : ',VM_info['VM_Name']
			print 'Zone : ',zone
			print '----------------------------------\n'
			VMs[VM_info['VM_Name']] = {'cc':cloud,'nc':VM_info['Node']}
		else:
			print 'Sorry, unable to create new VM due to ',VM_info['Error']
	if inp == 'd':
		print 'Select the VM which you want to delete'
		i = 1
		VM_list = []
		for name in VM_Name:
			print i,'. ',name
			VM_list.append(name)
		n = int(raw_input())
		VM = VMs[VM_list[n-1]]
		cloud = VM['cc']
		status = cloud.call_func('deleteVM',VM_list[n-1],VM['nc'])
		print status
	if inp == 'q':
		break;
for cloud in clouds:
	cloud.close()