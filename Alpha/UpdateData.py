# -*- coding: utf-8 -*-
"""
Created on Sat Apr 30 20:34:08 2016
UpdateData
in new file tructure of HDF5
@author: WangTao
"""
import tushare as ts
import pandas as pd
import datetime as dt
import multiprocessing
import time

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
	hostname=os.popen('hostname').read()

	if 'PrivateBook' in hostname:#家庭笔记本
		filename = 'c:\\tmp\\save.h5'
	elif 'USER-20160422LP' in hostname:#办公室台式机
		filename = u'D:\\用户目录\\My Documents\\Python\\save.h5'
	else:
		filename = 'd:\\save.h5'

	return filename

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

#下载个股指定日期后的前复权日线数据的单线程函数
def DownloadData(local, st, q):
	'''
	code is stockcode in string type
	st is time to market in string 'YYYY-MM-DD' type
	'''
	t = local.split('/')
	kind = t[1]
	code = t[2]

	if kind=='cq':
		kind = None
	try:
		if len(st)>8:
			df=ts.get_h_data(code, start = st, autype = kind)
		else:
			df=ts.get_h_data(code, autype = kind)

		if len(df)>0:
			df = df.sort_index()
			df = df.sort_index(axis = 1)
			filename = q.get()
			try:
				df.to_hdf(filename, local)
			except:
				store = pd.HDFStore(filename, mode = 'a')
				store[local] = df
				store.flush()
				store.close()

			q.put(filename)
			return True
	except:
		return False


#检查个股日线数据的情况并更新的单线程函数
def UpdateStockData(local, q):
	u'更新个股最新数据并对清权股票数据更新。如果无需更新则返回原来的df！'
	#分解基础信息
	t = local.split('/')
	kind = t[1]
	code = t[2]
	if kind == 'cq':
		kind = None

	#判断最后一个交易日
	nt = dt.datetime.now()
	cls = dt.time(15,30)
	if nt.time()>cls:
		wd = dt.date.today()
	else:
		wd = dt.date.today() - dt.timedelta(days=1)
	while ts.is_holiday(str(wd)):
		wd = wd-dt.timedelta(days=1)
	lastday = pd.Timestamp(wd)

	#对比日期
	filename = q.get()
	df = pd.read_hdf(filename, local)
	q.put(filename)
	df = df.dropna()
	df = df.sort_index()
	df = df.sort_index(axis = 1)
	check = df.iloc[-1].name

	if lastday>check:
		downday = check.date() - dt.timedelta(days=10)
		df1 = ts.get_h_data(code, start = str(downday), autype = kind)

		if len(df1)>0	:
			#对比是否发生清权
			dp = pd.concat([df,df1])
			dp = dp.drop_duplicates()
			ls = dp.index.duplicated()
			if sum(ls)>0: #有清权
				#重新下载数据
				return DownloadData(local, str(df.ix[0].name)[:10], q)
			else:#无清权
				dp = dp.sort_index()
				dp = dp.sort_index(axis = 1)
				filename = q.get()

				try:
					dp.to_hdf(filename, local)
				except:
					store = pd.HDFStore(filename, mode = 'a')
					store[local] = dp
					store.flush()
					store.close()

				q.put(filename)
				return True
		else:
			#无更新值
			return False
	else:
		#无更新值
		return True


#多线程发起函数
def MultiStart(down_dict = {}):
	#创建存储句柄
	filename = LoadLocalData()

	#创建队列
	manager = multiprocessing.Manager()
	queue = manager.Queue(1)
	queue.put(filename)

	#创建线程池
	count=multiprocessing.cpu_count()
	pool=multiprocessing.Pool(processes=count*2)
	#启动线程/进程池
	result=[]
	#判断状态
	if len(down_dict)>0: #有个股数据缺失，下载数据------------------------------
		for s in down_dict:
			result.append(pool.apply_async(DownloadData, (s, down_dict[s], queue)))
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
		status = CheckResult(result)
		totalStatus['个股数据下载：']=u'已经完成%s/%s项下载任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])

	else: #开始更新数据------------------------------------------
		filename = queue.get()
		store = pd.HDFStore(filename, mode = 'r')
		lst = store.keys()
		store.close()
		queue.put(filename)
		if '/basicinfo' in lst:
			lst.remove('/basicinfo')
		for s in lst:
			result.append(pool.apply_async(UpdateStockData, (s, queue)))
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
		status = CheckResult(result)
		totalStatus['个股数据更新：']=u'已经完成%s/%s项更新任务！其中成功%s个！'%(status['finished'],status['all'],status['successful'])


if __name__ == '__main__':


	totalStatus = {}
	totalStatus[u'开始时间'] = dt.datetime.now()


	#获得股票列表
	nbi = ts.get_stock_basics()
	nbi = nbi.sort_index(ascending=1)
	nlst = nbi.timeToMarket
	nlst = nlst.apply(ChangeDate)

	filename = LoadLocalData()
	store = pd.HDFStore(filename, mode = 'r')

	#获得本地数据列表
	lst = store.keys()
	store.close()
	if '/basicinfo' in lst:
		lst.remove('/basicinfo')

	#生成应下载列表
	tmplst = nlst.index.tolist()
	down_list = []
	for s in tmplst:
		down_list.append('/qfq/'+s)
		down_list.append('/cq/'+s)


	#-------------------------补全数据------------------------------------------
	for s in lst:
		down_list.remove(s)

	if len(down_list)>0: #有个股数据需要补全
		down_dict = {}
		for s in down_list:
			down_dict[s] = nlst[s[-6:]]

		MultiStart(down_dict) #开始多线程数据补全

	else:#无需个股数据补全，开始更新
		pass

	#-------------------------检查更新数据--------------------------------------
	MultiStart() #开始多线程更新

	#------------------数据下载结束--------------------------------------------
	store = pd.HDFStore(filename, mode = 'a')
	try:
		store.remove('/basicinfo')
	except:
		pass
	store['/basicinfo'] = nbi
	store.flush()
	store.close()
	totalStatus[u'结束时间']=dt.datetime.now()

	for d in totalStatus:
		print d,'\t',totalStatus[d]
