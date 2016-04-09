#C:\Users\WangTao\Documents\Python
#FileName:timertest.py
# -*- coding:utf-8-*-

#计时测试
import time
from timeit import timeit,repeat


start_cpu=time.clock()
start_real=time.time()
for i in xrange(5000):
	x=0
	for j in xrange(i):
		x=x+1
end_cpu=time.clock()
end_real=time.time()
print "%f real Seconds"%(end_real-start_real)
print "%f CPU Seconds"%(end_cpu-start_cpu)


t1=timeit('a=9*9*9*9*9*9')
print t1
t2=repeat('a=9*9*9*9*9*9')
print t2
