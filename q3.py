#import ptrace.debugger
import subprocess
import signal
import os
import sys
import time
var = False

# add relevant stuff as given at: https://criu.org/Checkpoint/Restore
def save_process(pid):
	t = PtraceProcess(pid)
	t.syscall()
	t.detach()

	registerValues = t.getregs()             # read all registers
	fo = fopen("img-dir/stats.img", "wb")
	fo.write(registerValues);
	fo.close()

	t.dumpCode()                        # dump code (as assembler or hexa is the disassembler is missing)
	fo = fopen("img-dir/fd.img", "wb")
	fo.write(t.fileDescriptors);
	fo.close()

	t.dumpStack()            # dump stack (memory words around ESP)
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
	global var
	if(var):
		save_process(pid)
	if not (check_pid(pid)):
		print "Process with this pid doesn't exist."
		return
	os.system("mkdir img-dir_" + str(pid))
	os.system("echo 12345678 | sudo -S criu dump -t " + str(pid) +" --images-dir ./img-dir_" + str(pid) + "/ --shell-job -vvv -o dump.log")
	print "Process successfully checkpointed."

	command = "crit show img-dir_" + str(pid) + "/core-" + str(pid) + ".img"
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)		
	process.wait()
	while True:
		line = process.stdout.readline()
		if line != '':
			#the real code does filtering here
			print line.rstrip()
		else:
			break
def restore(pid):
	if os.path.isdir("./img-dir_" + str(pid)):
		#os.system("pwd")
		os.chdir("./img-dir_" + str(pid) + "/")
		# subprocess.call("echo 12345678 | sudo -i", shell=True)
		#os.system("pwd")
		#os.system("echo 12345678 | sudo -S criu restore -d -vvv -o restore.log &")
		# #os.system("pwd")
		# command = "pwd"
		# process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)		
		# print process.stdout.readline()
		#subprocess.call("cd " + "./img-dir_" + str(pid) + "/", shell=True)
		#subprocess.call("criu restore --shell-job -d -vvv -o restore.log", shell=True) #&& echo 'Process restored successfully.'", shell=True)
		command = "echo 12345678 | sudo -S criu restore -D /home/nilay/ChotaBaadal/img-dir_" + str(pid) + "/ -d -vvv -o restore.log"
		process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)		
		process.wait()
		#print process.stdout.readline()
		#os.system("echo 123 | sudo -S criu restore --shell-job -d -vvv -o restore.log")
		# print "Process restored successfully."

if __name__ == "__main__":
	if sys.argv[1] == 'c':
		checkpoint(int(sys.argv[2]))
	elif sys.argv[1] == 'r':
		restore(int(sys.argv[2]))
	else:
		print "Invalid command."