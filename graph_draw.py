import matplotlib.pyplot as plt


p1=open('data1.txt').readlines()
p2=open('data2.txt').readlines()
p3=open('data3.txt').readlines()
p4=open('data4.txt').readlines()

p1_memory=[]
p2_memory=[]
p3_memory=[]
p4_memory=[]
for i in range(len(p1)):
	p1_memory.append(int(p1[i].split(':')[2].strip().split()[0][:-2])/10**12)
	p2_memory.append(int(p2[i].split(':')[2].strip().split()[0][:-2])/10**12)
	p3_memory.append(int(p3[i].split(':')[2].strip().split()[0][:-2])/10**12)
	p4_memory.append(int(p4[i].split(':')[2].strip().split()[0][:-2])/10**12)

x=[i for i in range(0,480,2)]
plt.plot(x,p1_memory,linewidth=1.5,label='NC21')
plt.plot(x,p2_memory,linewidth=1.5,label='NC12')
plt.plot(x,p3_memory,linewidth=1.5,label='NC11')
plt.plot(x,p4_memory,linewidth=1.5,label='NC22')
plt.title("Cpu")
plt.xlabel("Time(s)")
plt.ylabel("CPu")
plt.grid(True)
plt.legend(loc='best',prop={'size':12})
plt.show()

