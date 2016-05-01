# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 22:01:29 2016
多进程的Queue测试程序
@author: WangTao
"""

import numpy as np
import pandas as pd
import time
import multiprocessing
import os
import datetime as dt

#检查所有线程是否全部完成
def CheckResult(result):
	u'检查线程是否全部完成'
	if type(result)==list:
		lst=[]
		lst2=[]
		status={}
		for res in result:
			t=res.ready()
			lst.append(t)
			if t:
				try:
					lst2.append(res.successful())
				except:
					lst2.append(False)

		status['all']=len(result)
		status['finished']=sum(lst)
		status['successful']=sum(lst2)
	else:
		status['all']=len(result)
		status['finished']=len(result)
		status['successful']=0

	return status


#随机休眠函数，休眠结束后在文件中记录休眠时间
def RndSleep(q, slp):
	time.sleep(slp)
	pid = os.getpid()

	filename = q.get()

	try:
		df = pd.read_hdf(filename, 'df')
		if len(df)>0:
			df = df.append({'id':pid,'time':slp}, ignore_index=True)
			df.to_hdf(filename, 'df')
	except:
		try:
			store = pd.HDFStore(filename, mode = 'a')
			df = store['df']
		except:
			df = pd.DateFrame()
		df = df.append({'id':pid,'time':slp}, ignore_index=True)
		store['df'] = df
		store.flush()
		store.close()

	q.put(filename)
	print 'finished' + str(pid) + str(dt.datetime.now())

	return pid


if __name__ == '__main__':

	#生成随机数列表
	to_slp = np.random.random(100)
	to_slp = to_slp * 2

	#创建存储句柄
	filename = 'c:\\tmp\\queue.h5'

	#创建队列
	manager = multiprocessing.Manager()
	queue = manager.Queue(1)
	queue.put(filename)

	#创建线程池
	count=multiprocessing.cpu_count()
	pool=multiprocessing.Pool(processes=count*2)

	#启动线程/进程池
	result=[]
	date=[]

	for t in to_slp:
		result.append(pool.apply_async(RndSleep, (queue, t)))
	pool.close()

	status=CheckResult(result)
	oldq=0
	while status['finished']<status['all']:
		if status['finished']!=oldq:
			print u'\n\t\t已经完成%s/%s项更新任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])
		time.sleep(1)
		oldq=status['finished']
		status=CheckResult(result)
	status = CheckResult(result)
	print u'\n\t\t已经完成%s/%s项更新任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])

	pool.join()

	for s in status:
		print s, ':', status[s]

	for res in result:
		try:
			t=res.get()
			date.append(t)
		except Exception as err:
			print err.message


