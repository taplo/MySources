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
status={}
n = 20
lst = [0]*n #公用的数据，安全起见，每个线程只操作自己的那个位置。

def func(l):
	start = time.clock()
	global lst
	count = 0
	for i in xrange(l):
		for j in xrange(i):
			count += 1
	end = time.clock()
	s = [str(l), str(end-start)]
	lst[l] = end-start
	return s

#检查所有线程是否全部完成
def CheckResult(result):
	u'检查线程是否全部完成'
	global status
	if type(result) == list and type(result[0]) == multiprocessing.pool.AsyncResult:
		lst = []
		lst2 = []
		status = {}
		for res in result:
			t = res.ready()
			lst.append(t)
			if t:
				try:
					lst2.append(res.successful())
				except:
					lst2.append(False)
		status['all'] = len(result)
		status['finished'] = sum(lst)
		status['successful'] = sum(lst2)
	else:
		status['all'] = len(result)
		status['finished'] = len(result)
		status['successful'] = 0

	return status


if __name__ == "__main__":
	global status
	#创建线程池
	count = multiprocessing.cpu_count()
	pool = ThreadPool(processes=count)

	result = []
	for s in xrange(n):
		result.append(pool.apply_async(func, (s, )))
	pool.close()
	status = CheckResult(result)
	oldq = 0
	while status['finished'] < status['all']:
		if status['finished'] != oldq:
			print u'\n已经完成%s/%s项下载任务！其中成功%s个！'%(status['finished'], status['all'], status['successful'])
		time.sleep(0.1)
		oldq = status['finished']
		status = CheckResult(result)
	pool.join()
	print "Sub-process(es) done."
	for res in result:
		t = res.get()
		print "No.%s processing used %s seconds!"%(t[0], t[1])
