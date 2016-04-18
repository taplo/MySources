# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 20:34:24 2016

@author: WangTao
下载网络股票日线数据，并存入HDF5文件以备进行数据分析使用
"""

import tushare as ts
import pandas as pd
#import talib
#import matplotlib.pyplot as plt
import multiprocessing


#将上市时间的整形变量转换成符合要求的字符串变量
def ChangeDate(i):
	if i>0:
		s=str(i)
		r=s[0:4]+'-'+s[4:6]+'-'+s[6:8]
		return r
	else:
		return ''

#加载本地数据
def LoadLocalData():
	"""
	判断当前是哪台设备，不同的设备用不同的文件路径加载数据文件
	"""
	import os
	hostname=os.popen('hostname').read()

	if 'PrivateBook' in hostname:#家庭笔记本
		return pd.HDFStore('c:\\tmp\\save.h5',mode='a')
	elif 'USER-20151209CR' in hostname:#办公室台式机
		return pd.HDFStore('d:\\my documents\\python\\save.h5',mode='a')
	else:
		return None

#下载个股全部前复权日线数据
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
	return df

#首次的全部数据下载
def DownloadAllDataFirst():

	#获得网络股票数据列表
	nbi=ts.get_stock_basics()
	nbi=nbi.sort_index(ascending=1)
	
	#开启多进程数据下载
	count=multiprocessing.cpu_count()
	if count>2:
		count=count-1
	pool = multiprocessing.Pool(count)
	print 'Total '+str(count)+' processings!'
	result={}
	for s in xrange(len(nbi)):
	    result[nbi.index.values[s]]=pool.apply_async(DownloadQfqAll, (nbi.index.values[s],ChangeDate(nbi.ix[0,14])))
	pool.close()
	pool.join()
	
	print 'Download finished!'

	#添加日线数据进入存储数据表
	#给nbi添加一列用于存放日线数据
	tmp=pd.Series(result)
	nbi['qfqdata']=tmp
	
	return nbi
	

if __name__ == '__main__':
	'''
	#从本地加载数据
	store=LoadLocalData()
	'''

	nbi=DownloadAllDataFirst()
	store=pd.HDFStore('d:\\my documents\\python\\save.h5',mode='a')
	store['BI']=nbi
	store.close()
	
	
	
	
	
	


