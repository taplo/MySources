# -*- coding: utf-8 -*-
"""
Created on Tue May 03 21:24:00 2016
FileName:FindBig.py
用于在日线中寻找大行情阶段
大行情：
1、单边行情，最大回撤不超过10%
2、快速行情，三个月内
3、大幅度，涨幅70%以上
4、行情开始前无停盘——即非重组股
@author: WangTao
"""
import pandas as pd
import datetime as dt
import multiprocessing
import time


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








if __name__ == '__main__':
	pass
