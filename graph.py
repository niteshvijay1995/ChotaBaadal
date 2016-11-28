import time
import libvirt
f= open("data.txt","w+")
conn = libvirt.open('qemu:///system')
if conn == None:
		print('Failed to open connection to qemu:///system')
while True:
	sec = int(time.time())
	mem= conn.getFreeMemory()
	domainIDs = conn.listDomainsID()
	no_of_VM = len(domainIDs)
	stats = conn.getCPUStats(0)
	str1 = str(sec) + ' '+str(mem)+' '+str(no_of_VM)+' '+str(stats)+'\n'
	f.write(str1)
	print '.'
	time.sleep(2)
f.close