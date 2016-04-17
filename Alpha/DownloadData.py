# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 20:34:24 2016

@author: WangTao
下载网络股票日线数据，并存入HDF5文件以备进行数据分析使用
"""

import tushare as ts
import pandas as pd
import talib
import matplotlib.pyplot as plt



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


if __name__ == '__main__':

	#从本地加载数据
	store=LoadLocalData()


	#获得网络股票数据列表
	nbi=ts.get_stock_basics()


