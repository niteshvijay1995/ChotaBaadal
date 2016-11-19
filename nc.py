from  __future__ import print_function
import sys
import libvirt
import os
import xml.etree.ElementTree
import socket               # Import socket module
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
import os
from collections import namedtuple

_ntuple_diskusage = namedtuple('usage', 'total used free')

def disk_usage(path):
    """Return disk usage statistics about the given path.

    Returned valus is a named tuple with attributes 'total', 'used' and
    'free', which are the amount of total, used and free space, in bytes.
    """
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return _ntuple_diskusage(total, used, free)


def create(name):
	global xmlconfig
	xmlfile = xmlconfig.replace('#chotabaadal', name)	
	dom = conn.createXML(xmlfile, 0)
	if dom == None:
		print('Failed to create a domain from an XML definition.', file=sys.stderr)
		exit(1)

	print('Guest '+dom.name()+' has booted', file=sys.stderr)	

def stop(name):
	os.system('virsh suspend ' + name)

def delete(name):
	os.system('virsh destroy ' + name)

def resume(name):
	os.system('virsh resume ' + name)

if __name__ == "__main__": 
	conn = libvirt.open('qemu:///system')
	if conn == None:
		print('Failed to open connection to qemu:///system', file=sys.stderr)
		exit(1)
	s = socket.socket()         # Create a socket object
	host = socket.gethostname() # Get local machine name
	port = int(sys.argv[1])     # Reserve a port for your service.
	s.bind((host, port))        # Bind to the port
	s.listen(5)                 # Now wait for client connection.
	while True:
		c, addr = s.accept()     # Establish connection with client.
		#print 'Got connection from', addr
		print (c.recv(1024))
		resume('centos11')
		delete('centos11')
		create('centos11')
		stop('centos11')
		resume('centos11')
		domainIDs = conn.listDomainsID()
		if domainIDs == None:
			print('Failed to get a list of domain IDs', file=sys.stderr)
		print("Active domain IDs:")
		print ("Total" + str(disk_usage("/"))[0]))
		print ("Used" + str(disk_usage("/"))[1]))
		print ("Free" + str(disk_usage("/"))[2]))
		
		if len(domainIDs) == 0:
			print('  None')
		else:
			print (len(domainIDs))
			for domainID in domainIDs:
				dom = conn.lookupByID(domainID)
				if dom == None:
					print('Failed to get the domain object', file=sys.stderr)
				else:
					state, maxmem, mem, cpus, cput = dom.info()
					device_info = ' '.join([str(i) for i in dom.info()]) 
					c.send(device_info)
					print('The state is ' + str(state))
					print('The max memory is ' + str(maxmem))
					print('The memory is ' + str(mem))
					print('The number of cpus is ' + str(cpus))
					print('The cpu time is ' + str(cput))
		c.close()                # Close the connection

	conn.close()
	exit(0)
