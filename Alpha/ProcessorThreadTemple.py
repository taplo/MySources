# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

'''
#多进程测试
import multiprocessing
import time

def func(msg):
  for i in xrange(3):
    print msg
    time.sleep(1)
  return "done " + msg

if __name__ == "__main__":
  pool = multiprocessing.Pool(processes=4)
  result = []
  for i in xrange(10):
    msg = "hello %d" %(i)
    result.append(pool.apply_async(func, (msg, )))
  pool.close()
  pool.join()
  for res in result:
    print res.get()
  print "Sub-process(es) done."
'''

'''
#多进程测试
import multiprocessing as mp

def func(times):
	t=0.0
	try:
		for i in range(times*10000):
			t+i
	except Exception as err:
		print err.message+'!'
	print times/100

if __name__ == "__main__":
	jobs=[]
	for i in range(50):
		p=mp.Process(target=func,args=((i+1)*100,))
		jobs.append(p)
		p.start()
	print 'Main Process is Over!'
'''

'''
#多线程测试
import thread

def func(times):
	t=0.0
	try:
		for i in range(times*1000000):
			t=t+i/100
	except Exception as err:
		print err.message+'!'
	print t/100

if __name__ == "__main__":
	try:
		for i in range(30):
			thread.start_new_thread(func,(i+1,))
	except Exception as err:
		print err.message

	print 'Main thread is over!'
'''


#多进程的进程池测试
#今后可以作为模板使用

import multiprocessing
import time
i=0

def func(l):
	start=time.clock()
	count=0
	global i
	for i in xrange(l):
		for j in xrange(i):
			count+=1
	end=time.clock()
	s=[str(i),str(end-start)]
	return s


if __name__ == "__main__":
	count=multiprocessing.cpu_count()
	if count>2:
		count=count-1
	pool = multiprocessing.Pool(count)
	result=[]
	for s in xrange(100):
	    result.append(pool.apply_async(func, (s, )))
	pool.close()
	pool.join()
	print "Sub-process(es) done."
	for res in result:
		t=res.get()
		print "No.%s processing used %s seconds!"%(t[0],t[1])


'''
if __name__ == "__main__":
	pass
'''
