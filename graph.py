import time
import libvirt
f= open("guru99.txt","w+")
conn = libvirt.open('qemu:///system')
if conn == None:
		print('Failed to open connection to qemu:///system')
while True:
	mem= conn.getFreeMemory()
	domainIDs = conn.listDomainsID()
	no_of_VM = len(domainIDs)
	stats = conn.getCPUStats(0)
	str1 = str(mem)+' '+str(no_of_VM)+' '+str(stats)
	f.write(str1)
	time.sleep(2)
f.close