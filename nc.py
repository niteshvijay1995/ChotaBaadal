import sys
import libvirt
import os
import xml.etree.ElementTree
import subprocess
import socket							 # Import socket module
available_vcpu = 16
xmlconfig = """
<domain type='kvm'>
<name>#chotabaadal</name>
	<memory unit='KiB'>2097152</memory>
	<currentMemory unit='KiB'>2097152</currentMemory>
	<vcpu placement='static'>2</vcpu>
	<os>
		<type arch='x86_64' machine='pc-i440fx-xenial'>hvm</type>
		<boot dev='hd'/>
	</os>
	<features>
		<acpi/>
		<apic/>
	</features>
	<cpu mode='custom' match='exact'>
		<model fallback='allow'>Haswell</model>
	</cpu>
	<clock offset='utc'>
		<timer name='rtc' tickpolicy='catchup'/>
		<timer name='pit' tickpolicy='delay'/>
		<timer name='hpet' present='no'/>
	</clock>
	<on_poweroff>destroy</on_poweroff>
	<on_reboot>restart</on_reboot>
	<on_crash>restart</on_crash>
	<pm>
		<suspend-to-mem enabled='no'/>
		<suspend-to-disk enabled='no'/>
	</pm>
	<devices>
		<emulator>/usr/bin/kvm-spice</emulator>
		<disk type='file' device='disk'>
			<driver name='qemu' type='qcow2'/>
			<source file='/var/lib/libvirt/images/centos7.qcow2'/>
			<target dev='vda' bus='virtio'/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
		</disk>
		<disk type='file' device='cdrom'>
			<driver name='qemu' type='raw'/>
			<target dev='hda' bus='ide'/>
			<readonly/>
			<address type='drive' controller='0' bus='0' target='0' unit='0'/>
		</disk>
		<controller type='usb' index='0' model='ich9-ehci1'>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x7'/>
		</controller>
		<controller type='usb' index='0' model='ich9-uhci1'>
			<master startport='0'/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0' multifunction='on'/>
		</controller>
		<controller type='usb' index='0' model='ich9-uhci2'>
			<master startport='2'/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x1'/>
		</controller>
		<controller type='usb' index='0' model='ich9-uhci3'>
			<master startport='4'/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x2'/>
		</controller>
		<controller type='pci' index='0' model='pci-root'/>
		<controller type='ide' index='0'>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
		</controller>
		<controller type='virtio-serial' index='0'>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
		</controller>
		<interface type='network'>
			<mac address='52:54:00:29:3d:b9'/>
			<source network='default'/>
			<model type='virtio'/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
		</interface>
		<serial type='pty'>
			<target port='0'/>
		</serial>
		<console type='pty'>
			<target type='serial' port='0'/>
		</console>
		<channel type='unix'>
			<source mode='bind'/>
			<target type='virtio' name='org.qemu.guest_agent.0'/>
			<address type='virtio-serial' controller='0' bus='0' port='1'/>
		</channel>
		<input type='tablet' bus='usb'/>
		<input type='mouse' bus='ps2'/>
		<input type='keyboard' bus='ps2'/>
		<graphics type='vnc' port='-1' autoport='yes'/>
		<video>
			<model type='cirrus' vram='16384' heads='1'/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
		</video>
		<memballoon model='virtio'>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
		</memballoon>
	</devices>
</domain>

"""

# message encoding:
# i - provide info of all VMs running on the physical machine.
# c <num> create vm centos<num>
# s <num>
# d <num>
# r <num>
# e - exit node controller.

# state, maxmem, mem, cpus, cput = dom.info()

def create(name):
	global xmlconfig
	xmlfile = xmlconfig.replace('#chotabaadal', name) 
	dom = conn.createXML(xmlfile, 0)
	if dom == None:
		print('Failed to create a domain from an XML definition.')
		exit(1)

	print('Guest '+dom.name()+' has booted')	

def stop(name):
	os.system('virsh suspend ' + name)

def delete(name):
	os.system('virsh destroy ' + name)

def resume(name):
	os.system('virsh resume ' + name)

if __name__ == "__main__": 
	conn = libvirt.open('qemu:///system')
	if conn == None:
		print('Failed to open connection to qemu:///system')
		exit(1)

	memory = conn.getFreeMemory()
	s = socket.socket()				 # Create a socket object
	host = socket.gethostname() # Get local machine name
	port = int(sys.argv[1])		 # Reserve a port for your service.
	s.bind((host, port))				# Bind to the port
	s.listen(5)								 # Now wait for client connection.
	c, addr = s.accept()		 # Establish connection with client.
	while True:
		
		#print 'Got connection from', addr
		msg = c.recv(1024).split(' ')
		print "msg = ",
		print msg
		mem = str(memory)
		if msg[0] == 'e':
			break
		elif msg[0] == 'i':
			domainIDs = conn.listDomainsID()
			if domainIDs == None:
				print('Failed to get a list of domain IDs')
			print("Active domain IDs: "),
			print (len(domainIDs))
			usedvcpu = 0
			for domainID in domainIDs:
				dom = conn.lookupByID(domainID)
				if dom == None:
					print('Failed to get the domain object')
				else:
					state, maxmem, memo, cpus, cput = dom.info()
					usedvcpu += cpus
			mem = mem + ' ' + str(available_vcpu - usedvcpu)
			#mem = str(mem) + ' available vcpu = ' + str(available_vcpu - usedvcpu)
			print mem
			c.send(mem)
		else:
			name = 'centos' + msg[1]
			if msg[0] == 'c':
				create(name)
			elif msg[0] == 's':
				stop(name)
			elif msg[0] == 'd':
				delete(name)
			elif msg[0] == 'r':
				resume(name)

	c.close()							 # Close the connection

	conn.close()
	exit(0)
