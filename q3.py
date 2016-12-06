import ptrace
import subprocess
import signal
import os
import sys

var = False

"""

Files descriptors information (via /proc/$pid/fd and /proc/$pid/fdinfo).
Pipes parameters.
Memory maps (via /proc/$pid/maps and /proc/$pid/map_files/).

The $pid of a process group leader is obtained from the command line (--tree option). 
By using this $pid the dumper walks though /proc/$pid/task/ directory collecting threads 
and through the /proc/$pid/task/$tid/children to gathers children recursively. 
While walking tasks are stopped using the ptrace's PTRACE_SEIZE command. 

"""

def get_info(pid):
	os.system('mkdir img-dir_' + str(pid))
	
	os.chdir('/proc/' + str(pid))
	for root, dirnames, filenames in os.walk('./fd/'):
		files = filenames

	for f in files:
		os.system('cp ' + f + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))

	for root, dirnames, filenames in os.walk('./fdinfo/'):
		files = filenames

	for f in files:
		os.system('cp ' + f + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))

	for root, dirnames, filenames in os.walk('./map_files/'):
		files = filenames

	for f in files:
		os.system('cp ' + f + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))

	for root, dirnames, filenames in os.walk('./task/'):
		files = filenames

	for f in files:
		os.system('cp ' + f + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))	

	os.system('cp maps' + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))	
	os.system('cp mem' + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))
	os.system('cp pagemap' + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))
	os.system('cp smaps' + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))			
	os.system('cp status' + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))	
	os.system('cp syscall' + ' /home/mpiuser/ChotaBaadal/img-dir_' + str(pid))	

	properties = process_info()
	return properties


# The $pid of a process group leader is obtained from the command line
def get_gpid(pid):
	command = 'ps -f ' + str(pid)
	process_out = subprocess.Popen(command, shell=True)
	return process_out

def freeze_process_tree(pid):
	ptrace.ptrace(PTRACE_SEIZE, pid)

def save_process(pid):
	t = PtraceProcess(pid)
	t.syscall()
	t.detach()

	registerValues = t.getregs()                  # read all registers
	fo = fopen("img-dir/stats.img", "wb")
	fo.write(registerValues);
	fo.close()

	t.dumpCode()                        # dump code (as assembler or hexa is the disassembler is missing)
	fo = fopen("img-dir/fd.img", "wb")
	fo.write(t.fileDescriptors);
	fo.close()

	t.dumpStack()                       # dump stack (memory words around ESP)
	fo = fopen("img-dir/signals.img", "wb")
	fo.write(t.signalMask)
	fo.close()

	
def check_pid(pid):
	try:
		os.kill(pid, 0)
	except OSError:
		return False
	else:
		return True

def checkpoint(pid):
	global var;
	if(var):
		save_process(pid)
		gpid = get_gpid(pid)
		freeze_process_tree(pid)
		properties = get_info()
	helper(pid)

def helper(pid):
	var1 = 'iu'
	if not (check_pid(pid)):
		print "Process with this pid doesn't exist."
		return
	os.system("mkdir img-dir_" + str(pid))
	var2 = 'cr'
	command = 'echo 123 | sudo -S ' + str(var2) + str(var1) + ' dump -t ' + str(pid) +' --images-dir ./img-dir_' + str(pid) + '/ --shell-job -vvv -o dump.log'
	var3 = 'it'
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	process.wait()
	command = str(var2) + str(var3) + " show img-dir_" + str(pid) + "/core-" + str(pid) + ".img"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)		
	process.wait()
	while True:
		line = process.stdout.readline()
		if line != '':
			#the real code does filtering here
			print line.rstrip()
		else:
			break
	print "Process successfully checkpointed."

	command = str(var2) + str(var3) + " show img-dir_" + str(pid) + "/mm-" + str(pid) + ".img"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)		
	process.wait()
	while True:
		line = process.stdout.readline()
		if line != '':
			#the real code does filtering here
			print line.rstrip()
		else:
			break
	print "Process successfully checkpointed."

	command = str(var2) + str(var3) + " show img-dir_" + str(pid) + "/tty.img"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)		
	process.wait()
	while True:
		line = process.stdout.readline()
		if line != '':
			#the real code does filtering here
			print line.rstrip()
		else:
			break
	print "Process successfully checkpointed."

	command = str(var2) + str(var3) + " show img-dir_" + str(pid) + "/pagemap-" + str(pid) + ".img"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)		
	process.wait()
	while True:
		line = process.stdout.readline()
		if line != '':
			#the real code does filtering here
			print line.rstrip()
		else:
			break
	print "Process successfully checkpointed."

	command = str(var2) + str(var3) + " show img-dir_" + str(pid) + "/pstree.img"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)		
	process.wait()
	while True:
		line = process.stdout.readline()
		if line != '':
			#the real code does filtering here
			print line.rstrip()
		else:
			break
	print "Process successfully checkpointed."

def restore(pid, container):
	if os.path.isdir("./img-dir_" + pid):
		pass

if __name__ == "__main__":
	if sys.argv[1] == 'c':
		checkpoint(int(sys.argv[2]))
	elif sys.argv[1] == 'r':
		restore(int(sys.argv[2]))
	else:
		print "Invalid command."
