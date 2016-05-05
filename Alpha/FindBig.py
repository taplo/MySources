# -*- coding: utf-8 -*-
"""
Created on Tue May 03 21:24:00 2016
FileName:FindBig.py
用于在日线中寻找大行情阶段
大行情：
1、单边行情，最大回撤不超过10%
2、快速行情，三个月内
3、大幅度，涨幅70%以上
4、行情开始前无停盘——即非重组股
@author: WangTao
"""
import pandas as pd
import datetime as dt
import multiprocessing
import time


#全局变量
global totalStatus
totalStatus = {}

#加载本地数据路径
def load_local_path():
	"""
	判断当前是哪台设备，不同的设备用不同的文件路径加载数据文件
	"""
	import os
	hostname=os.popen('hostname').read()

	if 'PrivateBook' in hostname:#家庭笔记本
		filepath = 'c:\\tmp\\'
		#filename = 'c:\\tmp\\save.h5'
	elif 'USER-20160422LP' in hostname:#办公室台式机
		filepath = u'D:\\用户目录\\My Documents\\Python\\'
		#filename = u'D:\\用户目录\\My Documents\\Python\\save.h5'
	else:
		filepath = 'd:\\'
		#filename = 'd:\\save.h5'

	totalStatus['filepath'] = filepath
	return filepath


#检查所有线程是否全部完成
def check_result(result):
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
	
#数据合并，将收盘价数据Series和交易日历合并，形成适于分析的DataFrame
def make_data(se = pd.Series()):
	global totalStatus
	if len(se)>0:
		calender = totalStatus['calender']
		data = pd.DataFrame(se, columns=['price',])
		data = data.resample('1d')
		df = pd.merge(data, calender, left_index=1, right_index=1)
		return df
	else:
		return pd.DataFrame()


#列出高比例结果和比例
def gethighrate(local, se=pd.Series(), period=30, rate=60):
	length = len(se)
	if length > 0:	
		ratelst ={}
		for i in xrange(length):
			if i <= period:
				start = 0
			else:
				start = i - period
			l = se[start:i].min()
			h = se[start:i].max()
			ratelst[se.index[i]] = ((h/l) - 1) * 100
		result = pd.Series(ratelst)
		result = result[result>rate]
		result = result.drop_duplicates()
		return [local, result]
	else:
		return se


if __name__ == '__main__':

	global totalStatus
	totalStatus['starttime'] = dt.datetime.now()

	filepath = load_local_path()
	totalStatus['calender'] = pd.read_hdf(filepath+'info.h5', '/calender')

	store = pd.HDFStore(filepath+'save.h5', mode='r')
	#获得本地股票列表和总表
	bi = store['/basicinfo']
	bi = bi.sort_index()
	totalStatus['basicinfo'] = bi
	lst = store.keys()
	lst.remove('/basicinfo')
	store.close()
	
	
	
	
	
	
	
	
	
	
	totalStatus['endtime'] = dt.datetime.now()