# -*- coding: utf-8 -*-
"""
Created on Fri Apr 01 07:57:11 2016
tmptest.py 仅供测试
@author: Administrator
"""
import pandas as pd
import talib


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
	return pd.DataFrame.from_csv("c:\\users\\wangtao\\documents\\600606.csv")


#实验数据加载函数
def LoadTestData():
	import os
	hostname=os.popen('hostname').read()
	if 'PrivateBook' in hostname:#家庭笔记本
		return LapTopLoad()
	else:
		pass


if __name__ == '__main__':
	import talib
	#加载实验数据
	dp=LoadTestData()

	#CCI结果
	ccilist=talib.CCI(dp.high.values,dp.low.values,dp.close.values,timeperiod=10)

	print ccilist



