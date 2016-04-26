# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 21:54:20 2016
多线程测试
@author: WangTao
"""

#多进程的进程池测试
#今后可以作为模板使用
from multiprocessing.pool import ThreadPool
import multiprocessing
import time
lst=[0]*10 #公用的数据，安全起见，每个线程只操作自己的那个位置。

def func(l):
	start=time.clock()
	global lst
	count=0
	for i in xrange(l):
		for j in xrange(i):
			count+=1
	end=time.clock()
	s=[str(l),str(end-start)]
	lst[l]=end-start
	return s


if __name__ == "__main__":
	#创建线程池
	count=multiprocessing.cpu_count()
	pool=ThreadPool(processes=count)

	result=[]
	for s in xrange(10):
	    result.append(pool.apply_async(func, (s, )))
	pool.close()
	pool.join()
	print "Sub-process(es) done."
	for res in result:
		t=res.get()
		print "No.%s processing used %s seconds!"%(t[0],t[1])
	print lst
