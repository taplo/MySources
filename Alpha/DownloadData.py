# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 20:34:24 2016

@author: WangTao
下载网络股票日线数据，并存入HDF5文件以备进行数据分析使用
本程序主要用于本地已经有数据文件的情况下进行数据补全
"""

import tushare as ts
import pandas as pd
from multiprocessing.pool import ThreadPool
import multiprocessing
store=object

#将上市时间的整形变量转换成符合要求的字符串变量
def ChangeDate(i):
	r=''	
	if i>0:
		s=str(i)
		r=s[0:4]+'-'+s[4:6]+'-'+s[6:8]
	return r

#加载本地数据
def LoadLocalData():
	"""
	判断当前是哪台设备，不同的设备用不同的文件路径加载数据文件
	"""
	import os
	global store
	hostname=os.popen('hostname').read()

	if 'PrivateBook' in hostname:#家庭笔记本
		store=pd.HDFStore('c:\\tmp\\save.h5',mode='a')
	elif 'USER-20151209CR' in hostname:#办公室台式机
		store=pd.HDFStore('d:\\my documents\\python\\save.h5',mode='a')
	else:
		store=pd.HDFStore('d:\\save.h5',mode='a')
	try:		
		pan=store['qfqdata']
		for i in xrange(2):
			pan=pan.sort_index(axis=i,ascending=1)
	except:
		pan=pd.Panel()
		
	return pan
	
#保存本地数据
def SaveLocalData(pan):
	global store
	store['qfqdata']=pan

#下载个股指定日期后的前复权日线数据的单线程函数
def DownloadQfqAll(code,st):
	'''
	code is stockcode in string type
	st is time to market in string 'YYYY-MM-DD' type
	'''
	if len(st)>2:
		df=ts.get_h_data(code,start=st)
	else:
		df=ts.get_h_data(code)
	df=df.sort_index(ascending=1)
	print st+'finished!'
	return [code,df]


#按照列表多线程下载数据的函数
def MultiDownload(lst):
	#创建线程池
	count=multiprocessing.cpu_count()
	pool=ThreadPool(processes=count*2)

	#启动线程池
	result=[]
	date={}
	for i in xrange(len(lst)):
	    result.append(pool.apply_async(DownloadQfqAll, (lst.index[i],lst[i])))
	pool.close()
	pool.join()
	print "多线程下载结束！"
	for res in result:
		try:
			t=res.get()
			date[t[0]]=t[1]
		except Exception as err:
			print err.message

	pan=pd.Panel(date)
	pan.sort_index(axis=0,ascending=1)

	return pan


if __name__ == '__main__':
	#从本地加载数据
	pan=LoadLocalData()
	
	#获得股票列表
	bi=ts.get_stock_basics()
	bi=bi.sort_index(ascending=1)
	lst=bi.timeToMarket
	lst=lst.apply(ChangeDate)
	
	#补全缺失的个股
	#获得缺失的股票列表
	miss=lst.drop(pan.items.tolist())
	#下载缺失股票数据
	misspan=MultiDownload(miss)
	#合并缺失数据
	pan=pd.concat([pan,misspan],axis=0)
	
	

	
	
	
	#保存数据文件
	SaveLocalData(pan)
	#关闭保存文件
	global store
	store.close()
	


