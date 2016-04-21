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

#将上市时间的整形变量转换成符合要求的字符串变量
def ChangeDate(i):
	if i>0:
		s=str(i)
		r=s[0:4]+'-'+s[4:6]+'-'+s[6:8]
		return r
	else:
		return ''

#下载个股全部前复权日线数据
def DownloadQfqAll(code,st):
	'''
	code is stockcode in string type
	st is time to market in string 'YYYY-MM-DD' type
	'''
	if len(st)>2:
		df=ts.get_h_data(code,start=st,retry_count=5,pause=1)
		df=df.sort_index(ascending=1)
	else:
		df=ts.get_h_data(code,retry_count=5,pause=1)
	print code+':'+st+' finished!'
	return [code,df]





if __name__ == '__main__':

	FileName='d:\\my documents\\python\\save.h5'
	#获得网络股票数据列表
	nbi=ts.get_stock_basics()
	nbi=nbi.sort_index(ascending=1)
	lst=nbi.timeToMarket
	lst=lst.apply(ChangeDate)

	#创建线程池
	count=multiprocessing.cpu_count()
	pool=ThreadPool(processes=count)

	#启动线程池
	result=[]
	date={}
	for i in xrange(len(lst)):
	    result.append(pool.apply_async(DownloadQfqAll, (lst.index[i],lst[i])))
	pool.close()
	pool.join()
	print "Sub-threads done."
	for res in result:
		try:
			t=res.get()
			date[t[0]]=t[1]
		except Exception as err:
			print err.message

	data=pd.Series(date)
	data.sort_index(ascending=1)
	date=data.to_dict()
	pan=pd.Panel(date)
	store=pd.HDFStore(FileName,mode='a')
	store['allqfqdata']=pan
	store.close()


	print 'done!'
