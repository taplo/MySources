# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 20:34:24 2016

@author: WangTao
下载网络股票日线数据，并存入HDF5文件以备进行数据分析使用
本程序主要用于本地已经有数据文件的情况下进行数据补全
"""

import tushare as ts
import pandas as pd
import multiprocessing
from multiprocessing.pool import ThreadPool
import datetime as dt
import time
totalStatus = {}
lastday = pd.Timestamp.now()

#将上市时间的整形变量转换成符合要求的字符串变量
def ChangeDate(i):
	r=''
	if i>0:
		s=str(i)
		r=s[0:4]+'-'+s[4:6]+'-'+s[6:8]
	return r

#判断最后一个交易日和更新的下载日期
def set_lastday():
	global lastday
	nt=dt.datetime.now()
	cls=dt.time(15,30)
	if nt.time()>cls:
		wd=dt.date.today()
	else:
		wd=dt.date.today()-dt.timedelta(days=1)
	while ts.is_holiday(str(wd)):
		wd = wd-dt.timedelta(days=1)
	lastday=pd.Timestamp(wd)


#加载本地数据
def LoadLocalData():
	"""
	判断当前是哪台设备，不同的设备用不同的文件路径加载数据文件
	"""
	import os
	hostname=os.popen('hostname').read()

	if 'PrivateBook' in hostname:#家庭笔记本
		store=pd.HDFStore('c:\\tmp\\save.h5',mode='a')
	elif 'USER-20160422LP' in hostname:#办公室台式机
		store=pd.HDFStore(u'D:\\用户目录\\My Documents\\Python\\save.h5',mode='a')
	else:
		store=pd.HDFStore('d:\\save.h5',mode='a')
	
	return store


#下载个股指定日期后的前复权日线数据的单线程函数
def DownloadQfqAll(code,st):
	'''
	code is stockcode in string type
	st is time to market in string 'YYYY-MM-DD' type
	'''
	try:
		if len(st)>8:
			df=ts.get_h_data(code,start=st)
		else:
			df=ts.get_h_data(code)
		df=df.sort_index(axis=0)
		df=df.sort_index(axis=1)
	except:
		df=pd.DataFrame()
		
	return [code,df]

#下载个股指定日期后的除权日线数据的单线程函数
def DownloadCqAll(code,st):
	'''
	code is stockcode in string type
	st is time to market in string 'YYYY-MM-DD' type
	'''
	try:
		if len(st)>8:
			df=ts.get_h_data(code,autype=None,start=st,retry_count=5,pause=1)
		else:
			df=ts.get_h_data(code,autype=None,retry_count=5,pause=1)
		df=df.sort_index(axis=0)
		df=df.sort_index(axis=1)
	except:
		df=pd.DataFrame()

	return [code,df]


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


#按照列表多线程下载数据的函数
def MultiDownload(kind,lst):
	#创建线程池
	count=multiprocessing.cpu_count()
	#pool=ThreadPool(processes=count*2)
	pool=multiprocessing.Pool(processes=count*2)

	#启动线程池
	result=[]
	date={}
	if kind=='qfq':
		for i in xrange(len(lst)):
		    result.append(pool.apply_async(DownloadQfqAll, (lst.index[i],lst[i])))
	else:
		for i in xrange(len(lst)):
			result.append(pool.apply_async(DownloadCqAll, (lst.index[i],lst[i])))
	pool.close()
	status=CheckResult(result)
	oldq=0
	while status['finished']<status['all']:
		if status['finished']!=oldq:
			print u'\n\t\t已经完成%s/%s项下载任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])
		time.sleep(1)
		oldq=status['finished']
		status=CheckResult(result)
	pool.join()
	#print "多线程下载结束！"
	if kind=='qfq':
		totalStatus['qfqDownload']=u'已经完成%s/%s项前复权下载任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])
	else:
		totalStatus['cqDownload']=u'已经完成%s/%s项除权下载任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])
	for res in result:
		try:
			t=res.get()
			if len(t[1])>0:
				date[t[0]]=t[1]
		except:
			#print err.message
			pass
	if len(date)>0:
		pan=pd.Panel(date)
		pan=pan.sort_index(axis=0,ascending=1)
	else:
		pan=pd.Panel()

	return pan

#检查个股日线数据的情况并更新的单线程函数
def UpdateStockData(kind,code,df):
	u'更新个股最新数据并对清权股票数据更新。如果无需更新则返回原来的df！'
	'''
	#判断最后一个交易日
	nt=dt.datetime.now()
	cls=dt.time(15,30)
	if nt.time()>cls:
		wd=dt.date.today()
	else:
		wd=dt.date.today()-dt.timedelta(days=1)
	while ts.is_holiday(str(wd)):
		wd = wd-dt.timedelta(days=1)
	lastday=pd.Timestamp(wd)
	downday=wd-dt.timedelta(days=10)
	'''
	global lastday
	#对比日期
	df = df.dropna()
	#df = df.sort_index(ascending=1)
	check = max(df.index)

	if lastday>check:
		downday = dt.date(check.year, check.month, check.day)
		downday = downday - dt.timedelta(days=10)
		if kind=='qfq':
			try:
				tmp = DownloadQfqAll(code,str(downday))
				df1=tmp[1]
			except:
				df1=pd.DataFrame()
		elif kind=='cq':
			try:
				tmp = DownloadCqAll(code,str(downday))
				df1=tmp[1]
			except:
				df1=pd.DataFrame()
		else:
			df1=pd.DataFrame()
			
		if len(df)>0:
			#对比是否发生清权
			dp=pd.concat([df,df1])
			dp=dp.drop_duplicates()
			ls=dp.index.duplicated()
			if sum(ls)>0: #有清权
				#重新下载数据
				if kind=='qfq':
					res = DownloadQfqAll(code,str(df.ix[0].name)[:10])
				else:
					res = DownloadCqAll(code,str(df.ix[0].name)[:10])
				return [code,res]#返回重新下载的值
			else:#无清权，返回更新值
				return [code,dp]
		else:
			#无更新值，返回代码
			return code
	else:
		#无更新值，返回代码
		return code


#按数据表多线程更新股票数据的多线程启动函数
def MultiUpdate(kind,pan):
	u'多线程更新股票日线数据'
	#创建线程池
	count=multiprocessing.cpu_count()
	#pool=ThreadPool(processes=count*2)
	pool=multiprocessing.Pool(processes=count*2)
	#启动线程/进程池
	result=[]
	date={}
	
	
	if kind=='qfq':
		for i in xrange(len(pan)):
			code=pan.items[i]
			df=pan[code]
			result.append(pool.apply_async(UpdateStockData, ('qfq',code,df)))
	elif kind=='cq':
		for i in xrange(len(pan)):
			code=pan.items[i]
			df=pan[code]
			result.append(pool.apply_async(UpdateStockData, ('cq',code,df)))
	else:
		print 'Kind Error!!!'
	pool.close()
	status=CheckResult(result)
	oldq=0
	while status['finished']<status['all']:
		if status['finished']!=oldq:
			print u'\n\t\t已经完成%s/%s项更新任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])
		time.sleep(1)
		oldq=status['finished']
		status=CheckResult(result)
	pool.join()
	if kind=='qfq':
		totalStatus['qfqUpdate']=u'已经完成%s/%s项前复权更新任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])
	else:
		totalStatus['cqUpdate']=u'已经完成%s/%s项除权下载任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])
	for res in result:
		try:
			t=res.get()
			if type(t)==list:
				date[t[0]]=t[1]
		except:
			pass
	
	try:	
		if len(date)>0:
			tmppan=pd.Panel(date)
			for s in tmppan.items.tolist():
				pan[s]=tmppan[s]
			pan=pan.sort_index()
		else:
			pass
	except Exception as err:
		print err.message
	return pan


if __name__ == '__main__':

	totalStatus['Starttime']=dt.datetime.now()
	
	#设定最后一个交易日
	set_lastday()

	#获得股票列表
	bi=ts.get_stock_basics()
	bi=bi.sort_index(ascending=1)
	lst=bi.timeToMarket
	lst=lst.apply(ChangeDate)

	#-----------------------前复权数据处理--------------------------------------
	#从本地加载数据
	store=LoadLocalData()#加载前复权数据
	ls = store.keys()
	if '/qfq' in ls:
		qfqpan=store['qfq']
	else:
		qfqpan=pd.Panel()

	pan=qfqpan
	
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
	if len(pan)>0:
		qfqpan=pan.copy()
	store.qfq=qfqpan
	store.flush()
		
	#------------------------------除权数据处理---------------------------------
	#从本地加载数据
	if '/cq' in ls:
		cqpan=store['cq']
	else:
		cqpan=pd.Panel()
	pan=cqpan
	
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
	if len(pan)>0:
		cqpan=pan.copy()
	
	#--------------------------结果存盘-----------------------------------------
	filename=store.filename
	qfqpan=store.qfq
	store.flush()
	store.close()
	store=pd.HDFStore(filename,mode='w')
	store['qfq']=qfqpan
	store['cq']=cqpan
	store.flush()
	store.close()

	#---------------------------数据处理结束-------------------------------------

	totalStatus['Endtime']=dt.datetime.now()

	print u'下载情况：',totalStatus['qfqDownload']
	print u'         ',totalStatus['cqDownload']
	print u'更新情况：',totalStatus['qfqUpdate']
	print u'         ',totalStatus['cqUpdate']
	print u'开始时间：',totalStatus['Starttime']
	print u'结束时间：',totalStatus['Endtime']
	print u'用时:',totalStatus['Endtime']-totalStatus['Starttime']

	raw_input("\nPress the enter key to exit....")

