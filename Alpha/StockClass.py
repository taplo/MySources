# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 11:50:00 2016

@author: WangTao
个股的类用于数据获取和个股的分析计算
"""
import numpy as np
import pandas as pd
import talib
import matplotlib.pyplot as plt
import tushare as ts
from scipy import stats



class Stock(object):
	u'''用于进行个股的数据获取和相应分析计算的类
	类建立实例的时候获取全部数据\
	构造个股对象，info是BasicInfo中的一行记录，store是本地数据文件的HDF文件句柄'''
	version=' V0.1__2016/4/24'

	def __init__(self, info, store):
		u'构造个股对象，info是BasicInfo中的一行记录，store是本地数据文件的HDF文件句柄'
		if type(info)==pd.core.series.Series:
			self.name=info['name'].decode('utf-8')
			self.code=info.name
			self.info=info
			self.__store=store
		else:
			self.name=''
			self.code=''
			self.info=[]

		if type(store)==pd.io.pytables.HDFStore and len(self.name)>0:
			try:
				self.data=store[self.code]
				self.data=self.data.dropna()
			except:
				self.data=pd.DataFrame()

