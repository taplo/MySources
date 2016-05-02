# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 11:50:00 2016

@author: WangTao
个股的类用于数据获取和个股的分析计算
"""
import numpy as np
import pandas as pd
import talib as ta
#import matplotlib.pyplot as plt
#import tushare as ts
from scipy import stats
import os



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
	__info = pd.DataFrame() #个股的基础信息
	__qfq = pd.DataFrame()#前复权数据
	__cq = pd.DataFrame()#除权数据

	#-------------------------------方法----------------------------------------
	#-----------------------------------默认方法重写----------------------------
	def __init__(self, code):
		u'构造个股对象，code为股票代码'
		filename = self.__load_filename()
		bi = pd.read_hdf(filename, '/basicinfo')

		try:
			info=bi.loc[code]
		except KeyError:
			print 'code error 1!'+code
			return None
		self.name = info['name'].decode('utf-8')
		self.code = code
		self.__info = info

		try:
			self.__qfq = pd.read_hdf(filename, '/qfq/'+code)
			self.__cq = pd.read_hdf(filename, '/cq/'+code)
		except KeyError:
			print 'code error 2!'+code
			return None

	#-----------------------------------公开方法--------------------------------
	#MACD计算函数
	def macd(self,fast=12,slow=26,signal=9,kind='qfq'):
		u'MACD计算函数，返回以时间序列为索引的三项指标的DataFrame'
		if kind=='qfq':
			df = self.__qfq
		else:
			df = self.__cq

		diff, dea, macd = ta.MACD(df.close.values, fastperiod=fast , slowperiod=slow , signalperiod=signal)
		MACD = pd.DataFrame(index = df.index)
		MACD['DEA'] = dea
		MACD['DIFF'] = diff
		MACD['MACD'] = macd

		return MACD

	#根据整体价格分布计算每天收盘后的简单上涨概率
	def calc_simple_up_ratio(self, kind = 'qfq'):
		u"参数kind表明分析数据的类型，‘qfq’ 前复权， ‘cq’ 除权， 默认为前复权。返回带有时间序列的Series结构数据。"
		if kind == 'qfq':
			df = self.__qfq
		else:
			df = self.__cq

		df = df.sort_index()
		lst = [100 - stats.percentileofscore(df.close, f) for f in df.close]
		ratio = pd.Series(lst, index = df.index)
		return ratio

	#均线计算公式
	def single_ma(self, days = 5, kind = 'qfq'):
		u'计算单一均线值函数，days为平均周期，默认为5天。返回带有时间序列索引的Series结构数据。'
		if kind == 'qfq':
			df = self.__qfq
		else:
			df = self.__cq

		df = df.sort_index()
		lst = ta.MA(df.close.values, days, 0)
		MA = pd.Series(data = lst, index = df.index)
		return MA

	#OBV计算函数
	def obv(self, kind = 'qfq'):
		u'计算OBV指标。'
		if kind == 'qfq':
			df = self.__qfq
		else:
			df = self.__cq
		df = df.sort_index()

		lst = ta.OBV(df.close.values, df.volume.values)
		OBV = pd.Series(data = lst, index = df.index)
		return OBV

	#布林线计算函数
	def boll(self, kind = 'qfq', timeperiod = 20, nbdevup = 2, nvdevdn = 2, matype = 0):
		u'布林线计算函数。'
		if kind == 'qfq':
			df = self.__qfq
		else:
			df = self.__cq
		df = df.sort_index()

		upperband, middleband, lowerband = ta.BBANDS(df.close.values, timeperiod, nbdevup, nvdevdn, matype)
		BOLL = pd.DataFrame(index = df.index)
		BOLL['upperband'] = upperband
		BOLL['middleband'] = middleband
		BOLL['lowerband'] = lowerband
		return BOLL



	#上穿判断
	def cross_up(self, line1, line2):
		u'判断line1是否在最后一日上穿line2，返回bool值。这两个序列必须按照时间正向排序，即末尾为最新值！'
		if len(line1)>1 and len(line2)>1:
			if line1[-2] < line2[-2] and line1[-1] > line2[-1]:
				return True
			else:
				return False
		else:
			print u'参数错误！line1和line2必须为值序列！'

	#-----------------------------------私有方法--------------------------------
	def __load_filename(self):
		"""
		判断当前是哪台设备，不同的设备用不同的文件路径加载数据文件
		"""
		hostname=os.popen('hostname').read()
		if 'PrivateBook' in hostname:#家庭笔记本
			filename = 'c:\\tmp\\save.h5'
		elif 'USER-20160422LP' in hostname:#办公室台式机
			filename = u'D:\\用户目录\\My Documents\\Python\\save.h5'
		else:
			filename = 'd:\\save.h5'
		return filename










