import libvirt
import os
import xml.etree.ElementTree
import subprocess
import uuid
import socket
import json
import random
TOTAL_VCPU = 16
conn = libvirt.open('qemu:///system')
if conn == None:
		print('Failed to open connection to qemu:///system')
		exit(1)
xmlconfig = """
<domain type='kvm'>
	<name>#CBname</name>
	<uuid>#CBuuid</uuid>
	<memory unit='KiB'>#CBmemory</memory>
	<currentMemory unit='KiB'>#CBmemory</currentMemory>
	<vcpu placement='static'>#CBcores</vcpu>
	<os>
		<type arch='x86_64' machine='pc-i440fx-xenial'>hvm</type>
		<boot dev='hd'/>
		<boot dev='cdrom'/>
	</os>
	<features>
		<acpi/>
		<apic/>
		<pae/>
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
			<driver name='qemu' type='raw'/>
			<source file='/var/lib/libvirt/images/#CBname.img'/>
			<target dev='vda' bus='virtio'/>
			<alias name="virtio-disk0"/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
		</disk>
		<disk type='file' device='cdrom'>
			<driver name='qemu' type='raw'/>
			<source file="/var/lib/libvirt/boot/auto2.iso"/>
			<target dev='hdc' bus='ide'/>
			<readonly/>
			<alias name="ide0-1-0"/>
			<address type='drive' controller='0' bus='1' target='0' unit='0'/>
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
		<controller type='pci' index='0' model='pci-root'>
			<alias name="pci.0"/>
		</controller>
		<controller type='ide' index='0'>
			<alias name="ide0"/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
		</controller>
		<controller type='virtio-serial' index='0'>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
		</controller>
		<serial type='pty'>
			<source path="/dev/pts/12"/>
			<target port='0'/>
			<alias name="serial0"/>
		</serial>
		<console tty="/dev/pts/12" type="pty">
			<source path="/dev/pts/12"/>
			<target port="0" type="serial"/>
			<alias name="serial0"/>
		</console>
		<input bus="ps2" type="mouse"/>
		<input bus="ps2" type="keyboard"/>
		<channel type='unix'>
			<source mode='bind'/>
			<target type='virtio' name='org.qemu.guest_agent.0'/>
			<address type='virtio-serial' controller='0' bus='0' port='1'/>
		</channel>
		<input type='tablet' bus='usb'/>
		<input type='mouse' bus='ps2'/>
		<input type='keyboard' bus='ps2'/>
		<graphics type='vnc' port='-1' autoport='yes' listen="127.0.0.1">
			<listen address="127.0.0.1" type="address"/>
		</graphics>
		<sound model="ich6">
			<alias name="sound0"/>
			<address bus="0x00" domain="0x0000" function="0x0" slot="0x08" type="pci"/>
		</sound>
		<video>
			<model type='cirrus' vram='9216' heads='1'/>
			<alias name="video0"/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
		</video>
		<memballoon model='virtio'>
			<alias name="balloon0"/>
			<address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
		</memballoon>
	</devices>
</domain>

"""

# state, maxmem, mem, cpus, cput = dom.info()
def randomMAC():
	mac = [ 0x00, 0x16, 0x3e,
		random.randint(0x00, 0x7f),
		random.randint(0x00, 0xff),
		random.randint(0x00, 0xff) ]
	return ':'.join(map(lambda x: "%02x" % x, mac))

def create(name,memory,vcpu,disk):
	img_path = '/var/lib/libvirt/images/%s.img'%name
	cmd = 'qemu-img create -f raw '+img_path+' '+str(disk)+'G'
	print cmd
	try:
		os.system(cmd)
	except Exception as e:
		print str(e)
	global xmlconfig
	xmlfile = xmlconfig.replace('#CBname', name)
	xmlfile = xmlfile.replace('#CBmemory', str(memory))
	xmlfile = xmlfile.replace('#CBcores', str(vcpu))
	xmlfile = xmlfile.replace('#CBuuid',str(uuid.uuid3(uuid.NAMESPACE_DNS, str(name))))
	xmlfile = xmlfile.replace('#CBmac', randomMAC())	
	dom = conn.createXML(xmlfile, 0)
	if dom == None:
		print('LOG :: Failed to create a domain from an XML definition.')
		return 'False'
	return 'True'

def stop(name):
	os.system('virsh suspend ' + name)

def delete(name):
	os.system('virsh destroy ' + name)
	return 'Deleted'

def resume(name):
	os.system('virsh resume ' + name)

def free_disk_space(path):
	s = os.statvfs(path)
	return (s.f_bsize*s.f_bavail)/(1024**3)


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
	json_msg['disk'] = free_disk_space('/var/lib/libvirt/images')
	print json_msg
	return json.dumps(json_msg)

def migrate(domName,destHost):
	dest_conn = libvirt.open('qemu+ssh://'+destHost+'/system')
	if dest_conn == None:
		print('Failed to open connection to qemu+ssh://'+destHost+'/system')
		exit(1)
	dom = conn.lookupByName(domName)
	if dom == None:
		print('Failed to find the domain '+domName)
		exit(1)
	#scp img file to destination host
	os.system('scp /var/lib/libvirt/images/'+domName+'.img '+destHost+':/var/lib/libvirt/images/')
	new_dom = dom.migrate(dest_conn, 0, None, None, 0)
	if new_dom == None:
		print('Could not migrate to the new domain')
		exit(1)
	print('Domain was migrated successfully.')
	os.system('rm  /var/lib/libvirt/images/'+domName+'.img')
	dest_conn.close()
	return 'True'

def getAllVM():
	domains = {}
	domainIDs = conn.listDomainsID()
	for domainID in domainIDs:
		dom = conn.lookupByID(domainID)
		if dom == None:
			print('Failed to get the domain object')
		else:
			domains[dom.name()] = {}
			domains[dom.name()]['mem'] = dom.info()[2]
			domains[dom.name()]['vcpu'] = dom.info()[3]
			img_size=os.path.getsize("/var/lib/libvirt/images/"+dom.name()+".img")/1024**3
			domains[dom.name()].append(img_size)
	return json.dumps(domains)