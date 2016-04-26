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
import datetime as dt
import time
store=object

#将上市时间的整形变量转换成符合要求的字符串变量
def ChangeDate(i):
	r=''	
	if i>0:
		s=str(i)
		r=s[0:4]+'-'+s[4:6]+'-'+s[6:8]
	return r

#加载本地数据
def LoadLocalData(kind):
	"""
	判断当前是哪台设备，不同的设备用不同的文件路径加载数据文件
	"""
	import os
	global store
	hostname=os.popen('hostname').read()

	if 'PrivateBook' in hostname:#家庭笔记本
		store=pd.HDFStore('c:\\tmp\\save.h5',mode='a')
	elif 'USER-20160422LP' in hostname:#办公室台式机
		store=pd.HDFStore(u'D:\\用户目录\\My Documents\\Python\\save.h5',mode='a')
	else:
		store=pd.HDFStore('d:\\save.h5',mode='a')
	
	try:
		pan=store[kind]
	except:
		pan=pd.Panel()
	
	return pan
	
#保存本地数据
def SaveLocalData(kind,pan):
	global store
	del store[kind]
	store[kind]=pan
	store.close()

#下载个股指定日期后的前复权日线数据的单线程函数
def DownloadQfqAll(code,st):
	'''
	code is stockcode in string type
	st is time to market in string 'YYYY-MM-DD' type
	'''
	if len(st)>10:
		df=ts.get_h_data(code,start=st,retry_count=5,pause=1)
	else:
		df=ts.get_h_data(code,retry_count=5,pause=1)
	df=df.sort_index(axis=0)
	df=df.sort_index(axis=1)
	#print st+'finished!'
	return [code,df]

#下载个股指定日期后的除权日线数据的单线程函数
def DownloadCqAll(code,st):
	'''
	code is stockcode in string type
	st is time to market in string 'YYYY-MM-DD' type
	'''
	if len(st)>10:
		df=ts.get_h_data(code,autype=None,start=st,retry_count=5,pause=1)
	else:
		df=ts.get_h_data(code,autype=None,retry_count=5,pause=1)
	df=df.sort_index(axis=0)
	df=df.sort_index(axis=1)
	print st+'finished!'
	return [code,df]

#返回短时间更新数据的起始时间
def UpdateDate(s):
	#判断最后一个交易日
	wd=dt.date.today()
	while ts.is_holiis_holiday(str(wd)):
		wd = wd-dt.timedelta(days=1)

	#有初始时间的设置为5日前，没有的设为3日前
	if len(s)>1:
		day=str(wd-dt.timedelta(days=5))
	else:
		day=str(wd-dt.timedelta(days=3))
	
	return day
		
#检查所有线程是否全部完成
def CheckResult(result):
	if type(result)==list and type(result[0])==multiprocessing.pool.AsyncResult:
		lst=[]
		for res in result:
			lst.append(res.ready())
			return sum(lst) 
	else:
		return 0
	

#按照列表多线程下载数据的函数
def MultiDownload(kind,lst):
	#创建线程池
	count=multiprocessing.cpu_count()
	pool=ThreadPool(processes=count*2)

	#启动线程池
	result=[]
	date={}
	for i in xrange(len(lst)):
		if kind=='qfq':
		    result.append(pool.apply_async(DownloadQfqAll, (lst.index[i],lst[i])))
		else:
			result.append(pool.apply_async(DownloadCqAll, (lst.index[i],lst[i])))
	pool.close()
	qcount=CheckResult(result)
	while qcount:
		print u'\n已经完成%s/%s项下载任务！'%(qcount,len(result))
		time.sleep(15)
		qcount=CheckResult(result)
	pool.join()
	print "多线程下载结束！"
	for res in result:
		try:
			t=res.get()
			date[t[0]]=t[1]
		except Exception as err:
			print err.message

	pan=pd.Panel(date)
	pan=pan.sort_index(axis=0,ascending=1)

	return pan
	
#检查个股日线数据的情况并更新的单线程函数
def UpdateStockData(kind,code,df):
	u'更新个股最新数据并对清权股票数据更新。如果无需更新则返回原来的df！'
	#判断最后一个交易日
	wd=dt.date.today()
	while ts.is_holiis_holiday(str(wd)):
		wd = wd-dt.timedelta(days=1)
	lastday=pd.Timestamp(wd)
	#对比日期
	df = df.dropna()	
	df = df.sort_index(ascending=1)
	check = df.iloc[-1]
	
	if lastday>check.name:
		if kind=='qfq':
			df1 = DownloadQfqAll(code,UpdateDate(str(wd)))
		elif kind=='cq':
			df1 = DownloadCqAll(code,UpdateDate(str(wd)))
		else:
			df1=pd.DataFrame()
		
		if len(df1)>0	:	
			#对比是否发生清权
			dp=pd.concat([df,df1])
			dp=dp.drop_duplicates()
			ls=dp.index.duplicated()
			if sum(ls)>0: #有清权
				#重新下载数据
				if kind=='qfq':
					df1 = DownloadQfqAll(code,str(df.ix[0].name)[:10])
				elif kind=='cq':
					df1 = DownloadCqAll(code,str(df.ix[0].name)[:10])
				return df1
			else:#无清权
				return dp
		else:
			#无更新值
			return df
	else:
		#无更新值
		return df

	
#按数据表多线程更新股票数据的多线程启动函数
def MultiUpdate(kind,pan):
	u'多线程更新股票日线数据'
	#创建线程池
	count=multiprocessing.cpu_count()
	pool=ThreadPool(processes=count)
	#启动线程/进程池
	result=[]
	date={}
	qfq=['qfq']*len(pan)
	cq=['cq']*len(pan)
	for i in xrange(len(pan)):
		if kind=='qfq':	    
			result.append(pool.apply_async(UpdateStockData, (qfq,pan.items[i],pan[pan.items[i]])))
		elif kind=='cq':
			result.append(pool.apply_async(UpdateStockData, (cq,pan.items[i],pan[pan.items[i]])))
	pool.close()
	qcount=CheckResult(result)
	while qcount:
		print u'\n已经完成%s/%s项更新任务！'%(qcount,len(result))
		time.sleep(15)
		qcount=CheckResult(result)
	pool.join()
	for res in result:
		try:
			t=res.get()
			date[t[0]]=t[1]
		except Exception as err:
			print err.message,'code:',t[0]
	data=pd.Series(date)
	data.sort_index(ascending=1)
	date=data.to_dict()
	pan=pd.Panel(date)
	pan=pan.sort_index()
	
	return pan


if __name__ == '__main__':
	
	
	global store	
	
	
	#获得股票列表
	bi=ts.get_stock_basics()
	bi=bi.sort_index(ascending=1)
	lst=bi.timeToMarket
	lst=lst.apply(ChangeDate)

	#-----------------------前复权数据处理--------------------------------------
	#从本地加载数据
	pan=LoadLocalData('qfq')#加载前复权数据
	
	#补全缺失的个股
	#获得缺失的股票列表
	miss=lst.drop(pan.items.tolist())
	#下载缺失股票数据
	if len(miss)>0:	
		misspan=MultiDownload('qfq',miss)
		#合并缺失数据
		pan=pd.concat([pan,misspan],axis=0)
		pan=pan.sort_index(axis=0,ascending=1)
	#更新日线数据
	pan=MultiUpdate('qfq',pan)
		
	#保存数据文件
	SaveLocalData('qfq',pan)
	
	#------------------------------除权数据处理---------------------------------
	#从本地加载数据
	pan=LoadLocalData('cq')#加载前复权数据
	
	#补全缺失的个股
	#获得缺失的股票列表
	miss=lst.drop(pan.items.tolist())
	#下载缺失股票数据
	if len(miss)>0:	
		misspan=MultiDownload('cq',miss)
		#合并缺失数据
		pan=pd.concat([pan,misspan],axis=0)
		pan=pan.sort_index(axis=0,ascending=1)
	#更新日线数据
	pan=MultiUpdate('cq',pan)
	
	#保存数据文件
	SaveLocalData('cq',pan)

	#---------------------------数据处理结束-------------------------------------	
	
	
	


