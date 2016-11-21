import libvirt
import os
import xml.etree.ElementTree
import subprocess
import socket
import json
TOTAL_VCPU = 16
conn = libvirt.open('qemu:///system')
if conn == None:
		print('Failed to open connection to qemu:///system')
		exit(1)
xmlconfig = """
<domain type='kvm'>
<name>#CBname</name>
	<memory unit='KiB'>#CBmemory</memory>
	<currentMemory unit='KiB'>#CBmemory</currentMemory>
	<vcpu placement='static'>#CBcores</vcpu>
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

# state, maxmem, mem, cpus, cput = dom.info()

def create(name,memory,vcpu):
	global xmlconfig
	xmlfile = xmlconfig.replace('#CBname', name)
	xmlfile = xmlconfig.replace('#CBmemory', memory)
	xmlfile = xmlconfig.replace('#CBcores', vcpu)
	dom = conn.createXML(xmlfile, 0)
	if dom == None:
		print('LOG :: Failed to create a domain from an XML definition.')
		return 'False'
	return 'True'

def stop(name):
	os.system('virsh suspend ' + name)

def delete(name):
	os.system('virsh destroy ' + name)

def resume(name):
	os.system('virsh resume ' + name)

def get_stats():
	json_msg = {}
	json_msg['mem']= conn.getFreeMemory()
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
	available_vcpu = TOTAL_VCPU - usedvcpu
	json_msg['vcpu'] = available_vcpu
	print json_msg
	return json.dumps(json_msg)



