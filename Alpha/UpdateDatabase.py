# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %Taplo
FileName:UpdateDatabase.py
更新数据数据内容
"""
import tushare as ts
import pandas as pd
import datetime as dt

store=object()


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
			df=ts.get_h_data(code,start=st,retry_count=5,pause=1)
		else:
			df=ts.get_h_data(code,retry_count=5,pause=1)
	except:
		df=pd.DataFrame()

	try:
		if len(df)>0:
			df=df.sort_index(axis=0)
			return df
		else:
			return pd.DataFrame()
	except:
		return pd.DataFrame()

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
	except:
		df=pd.DataFrame()

	try:
		if len(df)>0:
			df=df.sort_index(axis=0)
			return df
		else:
			return pd.DataFrame()
	except:
		return pd.DataFrame()



#检查个股日线数据的情况并更新的单线程函数
def UpdateStockData(kind,code,df):
	u'更新个股最新数据并对清权股票数据更新。如果无需更新则返回原来的df！'
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
	#对比日期
	df = df.dropna()
	df = df.sort_index(ascending=1)
	check = df.iloc[-1]

	if lastday>check.name:
		if kind=='qfq':
			df1 = DownloadQfqAll(code,str(downday))
		elif kind=='cq':
			df1 = DownloadCqAll(code,str(downday))
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




if __name__ == '__main__':

	totalStatus={}
	totalStatus[u'开始时间']=dt.datetime.now()

	global store
	store=LoadLocalData()

	#获得股票列表
	bi=ts.get_stock_basics()
	bi=bi.sort_index(ascending=1)
	lst=bi.timeToMarket
	lst=lst.apply(ChangeDate)

	#-----------------------前复权数据处理--------------------------------------
	pan=store['qfq']
	
	#补全缺失的个股
	#获得缺失的股票列表
	if len(store)>0:
		pan=store['qfq']
		miss=lst.drop(pan.items.tolist())
	else:
		miss=lst
	
	if len(miss)>0:
		print u'需下载%s个股票的数据！'%(len(miss))
		for i in xrange(len(miss)):
			cout=0
			df=DownloadQfqAll(miss.index[i],miss[i])
			while len(df)==0 and cout<2:
				print u'下载错误，重新下载！'
				df=DownloadQfqAll(miss.index[i],miss[i])
				cout+=1
			print u'已下载%s股日线数据，共计%s条！'%(miss.index[i],len(df))
			if len(df>0):			
				pan[miss.index[i]]=df
		pan=pan.sort_index(axis=0)
		print u'共下载%s个股票数据！'%(i+1)
		totalStatus[u'前复权下载']=u'共下载%s个股票数据！'%(i+1)
	else:
		print u'无缺失股票数据！'
	
	#更新日线数据
	try:
		for i in xrange(len(pan)):
			pan[pan.items[i]]=UpdateStockData('qfq',pan.items[i],pan[pan.items[i]])
		print u'共更新%s个股票的日线数据！'%(i+1)
	except Exception as err:
		print err.message
	totalStatus[u'前复权更新']=u'共更新%s个股票的日线数据！'%(i+1)
	#保存数据文件
	store.remove('qfq')
	store.flush()
	store['qfq']=pan
	#-----------------------除权数据处理--------------------------------------
	pan=store['cq']
	
	#补全缺失的个股
	#获得缺失的股票列表
	if len(store)>0:
		pan=store['cq']
		miss=lst.drop(pan.items.tolist())
	else:
		miss=lst

	if len(miss)>0:
		print u'需下载%s个股票的数据！'%(len(miss))
		for i in xrange(len(miss)):
			cout=0
			df=DownloadCqAll(miss.index[i],miss[i])
			while len(df)==0 and cout<2:
				print u'下载错误，重新下载！'
				df=DownloadCqAll(miss.index[i],miss[i])
				cout+=1
			print u'已下载%s股日线数据，共计%s条！'%(miss.index[i],len(df))
			if len(df>0):			
				pan[miss.index[i]]=df
		pan=pan.sort_index(axis=0)
		print u'共下载%s个股票数据！'%(i+1)
		totalStatus[u'除权下载']=u'共下载%s个股票数据！'%(i+1)
	else:
		print u'无缺失股票数据！'
	
	#更新日线数据
	try:
		for i in xrange(len(pan)):
			pan[pan.items[i]]=UpdateStockData('cq',pan.items[i],pan[pan.items[i]])
		print u'共更新%s个股票的日线数据！'%(i+1)
	except Exception as err:
		print err.message
	totalStatus[u'除权更新']=u'共更新%s个股票的日线数据！'%(i+1)
	#保存数据文件
	store.remove('cq')
	store.flush()
	store['cq']=pan
	store.flush()
	store.close()
	#------------------数据下载结束--------------------------------------------
	totalStatus[u'结束时间']=dt.datetime.now()

	print totalStatus


