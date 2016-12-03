import time

c = 0
while True:
	f = open('file.txt', 'a')
	f.write(str(c) + '\n')
	c += 1 
	f.close()
	time.sleep(1)