# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 11:50:00 2016

@author: WangTao
个股的类用于数据获取和个股的分析计算
"""
import numpy as np
import pandas as pd
import talib as ta
import matplotlib.pyplot as plt
import tushare as ts
from scipy import stats



class Stock(object):
	u'''用于进行个股的数据获取和相应分析计算的类
	类建立实例的时候获取全部数据\
	构造个股对象，info是BasicInfo中的一行记录，store是本地数据文件的HDF文件句柄'''
	version=' V0.1__2016/4/24'

	#--------------------------------属性---------------------------------------
	#------------------------------------公开属性-------------------------------
	name=''#股票名称
	code=''#股票代码

	#------------------------------------私有属性-------------------------------
	__qfq=pd.DataFrame()#前复权数据
	__cq=pd.DataFrame()#除权数据

	#-------------------------------方法----------------------------------------
	#-----------------------------------默认方法重写----------------------------
	def __init__(self, code):
		u'构造个股对象，code为股票代码'

		bi = ts.get_stock_basics()
		try:
			info=bi[code]
		except KeyError:
			print 'code error!'+code
			break
		self.name = info['name'].decode('utf-8')
		self.code = code
		self.info = info

		try:
			store = pd.HDFStore('c:\\tmp\\save.h5',mode='r')
			__qfq = store.qfq[code]
			__qfq = __qfq.dropna()
			__qfq = __qfq.sort_index()
			__cq = store.cq[code]
			__cq = __cq.dropna()
			__cq = __cq.sort_index()
			store.close()
		except KeyError:
			print 'code error!'+code
			break

	#-----------------------------------公开方法--------------------------------
	def macd(self,fast=12,slow=26,signal=9,kind='qfq'):
		if kind=='qfq':
			diff, dea, macd = ta.MACD(__qfq.close.tolist(), fastperiod=fast , slowperiod=slow , signalperiod=signal)

	#-----------------------------------私有方法--------------------------------










