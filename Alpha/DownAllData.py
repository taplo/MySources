# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 21:41:36 2016

@author: WangTao
下载全部日线数据并保存到本地文件
"""
import tushare as ts
import pandas as pd
from multiprocessing.pool import ThreadPool
import multiprocessing
import time
import datetime as dt
#import os

global finished
global total

#将上市时间的整形变量转换成符合要求的字符串变量
def ChangeDate(i):
	if i > 0:
		s = str(i)
		r = s[0:4]+'-'+s[4:6]+'-'+s[6:8]
		return r
	else:
		return ''

#下载个股全部前复权日线数据
def DownloadQfqAll(code, st):
	'''
	code is stockcode in string type
	st is time to market in string 'YYYY-MM-DD' type
	'''
	if len(st) > 2:
		df=ts.get_h_data(code, start=st, retry_count=5, pause=1)
		df=df.sort_index(ascending=1)
	else:
		df=ts.get_h_data(code,retry_count=5,pause=1)
	#print code+':'+st+' finished!'
	df=df.sort_index(axis=0)
	df=df.sort_index(axis=1)
	return [code,df]

#下载个股全部除权日线数据
def DownloadCqAll(code,st):
	'''
	code is stockcode in string type
	st is time to market in string 'YYYY-MM-DD' type
	'''
	if len(st)>2:
		df=ts.get_h_data(code,start=st,autype=None,retry_count=5,pause=1)
		df=df.sort_index(ascending=1)
	else:
		df=ts.get_h_data(code,autype=None,retry_count=5,pause=1)
	#print code+':'+st+' finished!'
	df=df.sort_index(axis=0)
	df=df.sort_index(axis=1)
	return [code,df]

#callback函数
def PutResult(res):
	global finished
	global total
	try:
		if type(res)==list:
			t=res[0]
			finished+=1
			#os.system('cls')
			print 'stock:%s finished %s/%s!'%(t,finished,total)
		else:
			print '***',res,'***'
	except:
		print '***',res,'***'
		
#检查所有线程是否全部完成
def CheckResult(result):
	if type(result)==list and type(result[0])==multiprocessing.pool.AsyncResult:
		for res in result:
			if res.ready()!=True:
				return False
	else:
		return True
	
if __name__ == '__main__':
	
	global finished
	global total
	finished=0
	FileName=u'D:\\用户目录\\My Documents\\Python\\save.h5'
	#获得网络股票数据列表
	nbi=ts.get_stock_basics()
	nbi=nbi.sort_index(ascending=1)
	lst=nbi.timeToMarket
	lst=lst.apply(ChangeDate)
	total=len(lst)

	
	#创建线程池
	count=multiprocessing.cpu_count()
	pool=ThreadPool(processes=count)
	'''
	#创建进程池
	count=multiprocessing.cpu_count()
	pool=multiprocessing.Pool(processes=count-1)
	print 'Downloading started...'
	'''
	#启动线程/进程池
	result=[]
	date={}
	for i in xrange(len(lst)):
	    result.append(pool.apply_async(DownloadQfqAll, (lst.index[i],lst[i]),callback=PutResult))
	pool.close()
	#while pool._state==1:
	#while pool._inqueue.qsize()>count:
	while CheckResult(result)!=True:
		print u'仍有%s任务在排队中！\t %s'%(pool._inqueue.qsize(),str(dt.datetime.now()))
		time.sleep(15)
	pool.join()
	print "Sub-threads done."
	for res in result:
		try:
			t=res.get()
			date[t[0]]=t[1]
		except Exception as err:
			print err.message

	del pool	
	
	data=pd.Series(date)
	data.sort_index(ascending=1)
	date=data.to_dict()
	pan=pd.Panel(date)
	pan=pan.sort_index()
	store=pd.HDFStore(FileName,mode='a')
	store['qfq']=pan
	store.close()
	del pan	
	
	#下载除权数据--------------------------------------------

	#创建线程池
	pool=ThreadPool(processes=count)

	#启动线程池
	result=[]
	date={}
	finished=0
	for i in xrange(len(lst)):
	    result.append(pool.apply_async(DownloadCqAll, (lst.index[i],lst[i]),callback=PutResult))
	pool.close()
	while CheckResult(result)!=True:
		print u'仍有%s任务在排队中！\t %s'%(pool._inqueue.qsize(),str(dt.datetime.now()))
		time.sleep(15)
	pool.join()
	print "Sub-threads done."
	for res in result:
		try:
			t=res.get()
			date[t[0]]=t[1]
		except Exception as err:
			print err.message

	del pool	
	
	data=pd.Series(date)
	data.sort_index(ascending=1)
	date=data.to_dict()
	pan=pd.Panel(date)
	pan=pan.sort_index()
	store=pd.HDFStore(FileName,mode='a')
	store['cq']=pan
	store.close()

	print 'done!'
