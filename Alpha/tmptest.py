# -*- coding: utf-8 -*-
"""
Created on Fri Apr 01 07:57:11 2016
tmptest.py 仅供测试
@author: Administrator
"""
import pandas as pd
import talib
import matplotlib.pyplot as plt
import MySQLdb
import tushare as ts
from scipy import stats

'''
#获得当日大单数据测试
def GetDayData(code):
    import tushare as ts
    import datetime as dt

    if code=='':
        code='600030'
    df=ts.get_sina_dd(code, date=str(dt.date.today()))
    s=df.describe()
    print code
    print s
    #return s
'''

#家庭笔记本测试用数据读取
def LapTopLoad():
	return pd.DataFrame.from_csv("c:\\users\\wangtao\\documents\\600999.csv")

#办公室台式机测试用数据读取
def OfficeDesktopLoad():
	#打开数据库链接
	db=MySQLdb.connect("localhost","dbuser","dbuser","test")
	cur=db.cursor()
	dbCommand="select date,open,high,close,low,vol,turn from DateLine where code='%s' order by date DESC"%('600999')
	try:
		cur.execute(dbCommand)
		o=cur.fetchall()
		#将结果转化成pandas的DataFrame数据结构
		t1=[]
		t2=[]
		for i in xrange(len(o)):
			t1.append(o[i][0])
			t2.append(pd.Series(o[i][1:7],index=['open','high','close','low','vol','turn']))
		obj=pd.DataFrame(t2,index=t1)
		obj.index.name='date'
	except Exception as err:
		obj=err.message
	finally:
		db.close()
		return obj

#从网络获取数据
def NetworkLoad():
	return ts.get_h_data('600999')


#实验数据加载函数
def LoadTestData():
	import os
	import socket
	try:
		socket.gethostbyname('baidu.com')
		return NetworkLoad()
	except:
		hostname=os.popen('hostname').read()
		if 'PrivateBook' in hostname:#家庭笔记本
			return LapTopLoad()
		elif 'USER-20151209CR' in hostname:#办公室台式机
			return OfficeDesktopLoad()
		else:
			return '数据加载错误，请手动加载！'

#根据整体价格分布计算每天收盘后的简单上涨概率
def CalcSimpleUpRatio(df):
	"参数df为个股日线数据的DataFrame类型参数。返回错误信息或增加了概率列的DataFrame数据。"
	try:
		df.sort_index(ascending=1)
		lst=[100-stats.percentileofscore(df.close,f) for f in df.close]
		df['ratio']=lst
		return df
	except Exception as err:
		return err.message

#根据整体价格分布计算每天收盘后的简单上涨概率_计算全部股份
def CalcAllSimpleUpRatio(pan):
	"参数pan为所有日线数据的Panel类型参数，返回错误信息或以代码为索引的收盘价和上涨简单概率DataFrame数据"
	try:
		pan=pan.sort_index(axis=1,ascending=1)
		cl=pan.major_xs(pan.major_axis[-1]).ix['close']
		cl=cl.dropna()
		lst=[100-stats.percentileofscore(pan[i].close.dropna(),cl[i]) for i in cl.index]
		res=pd.DataFrame(cl)
		res['ratio']=lst
		return res
	except Exception as err:
		return err.message


if __name__ == '__main__':

	#加载实验数据
	dp=LoadTestData()
	if len(dp)<50:
		print dp
		exit()

	#CCI结果
	ccilist=talib.CCI(dp.high.values,dp.low.values,dp.close.values,timeperiod=10)
	#合并入数据表
	dp['cci']=ccilist

	close=dp.close
	cci=dp.cci

	#数据显示
	close.plot()
	cci.plot()

	plt.show()




	'''
	macdlist=talib.MACD(dp.close.values,12,26,9)

	print macdlist
	'''


